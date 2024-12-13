from typing import Any, TypedDict, cast, Literal
import logging

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage
from langgraph.graph import START, StateGraph, END

from fastapi_backend.langgraph_graphs.langgraph_agents.utils import load_chat_model, format_docs_code
from fastapi_backend.langgraph_graphs.langgraph_agents.code_retrieval_graph.researcher_graph.graph import graph as researcher_graph
from fastapi_backend.langgraph_graphs.langgraph_agents.code_generation_graph.state import AgentState, InputState
from fastapi_backend.langgraph_graphs.langgraph_agents.code_retrieval_graph.configuration import AgentConfiguration

logger = logging.getLogger(__name__)

async def conduct_research(state: AgentState) -> dict[str, Any]:
    """Execute the first step of the research plan.

    This function takes the first step from the research plan and uses it to conduct research.

    Args:
        state (AgentState): The current state of the agent, including the research plan steps.

    Returns:
        dict[str, list[str]]: A dictionary with 'documents' containing the research results and
                              'steps' containing the remaining research steps.
    """
    result = await researcher_graph.ainvoke({"question": state.research_steps[0], "library": state.library})

    logger.debug(f"Result: {result}")

    return {"documents": result["documents"], "library_code": result["library_code"], "research_steps": state.research_steps[1:]}

async def create_app_research_plan(
    state: AgentState, *, config: RunnableConfig
) -> dict[str, list[str]]:
    """Create a step-by-step research plan for answering a LangChain-related query.

    Args:
        state (AgentState): The current state of the agent, including conversation history.
        config (RunnableConfig): Configuration with the model used to generate the plan.

    Returns:
        dict[str, list[str]]: A dictionary with a 'steps' key containing the list of research steps.
    """

    class Plan(TypedDict):
        """Generate research plan."""

        app_steps: list[str]
        research_steps: list[str]

    configuration = AgentConfiguration.from_runnable_config(config)
    model = load_chat_model(configuration.query_model).with_structured_output(Plan)
    messages = [
        {"role": "system", "content": configuration.research_plan_system_prompt}
    ] + state.messages
    response = await cast(Plan, model.ainvoke(messages))
    logger.debug(f"Response: {response}")
    logger.debug(f"Research Steps: {response["research_steps"]}")
    logger.debug(f"App Steps: {response["app_steps"]}")
    return {
        "research_steps": response["research_steps"],
        "app_steps": response["app_steps"],
        "documents": "delete",
        "query": state.messages[-1].content,
    }

def check_finished(state: AgentState) -> Literal["build_app", "conduct_research"]:
    """Determine if the research process is complete or if more research is needed.

    This function checks if there are any remaining steps in the research plan:
        - If there are, route back to the `conduct_research` node
        - Otherwise, route to the `build_app` node

    Args:
        state (AgentState): The current state of the agent, including the remaining research steps.

    Returns:
        Literal["build_app", "conduct_research"]: The next step to take based on whether research is complete.
    """
    if len(state.research_steps) > 0:
        return "conduct_research"
    else:
        return "build_app"
    
async def build_app(
        state: AgentState, *, config: RunnableConfig
) -> dict[str, Any]:
    """Execute all the steps of the app plan.

    Follow the steps to build a complete application based on the user's query and conducted research.

    Args:
        state (AgentState): The current state of the agent, including the research plan steps.

    Returns:
        dict[str, list[str]]: A dictionary with 'documents' containing the research results and
                              'steps' containing the remaining research steps.
    """

    class CodeGenerated(TypedDict):
        """Generate the frontend and backend code"""
        
        frontend: str
        backend: str

    if state.code_evaluated:
        configuration = AgentConfiguration.from_runnable_config(config)
        model = load_chat_model(configuration.query_model).with_structured_output(CodeGenerated)
        top_k = 20
        context = format_docs_code(docs=state.documents[:top_k], code=state.library_code)
        prompt = configuration.regenerate_code_system_prompt.format(
            frontend=state.frontend,
            backend=state.backend,
            feedback_content=state.feedback_content,
            context=context
            )
    else:
        # config = RunnableConfig(
        #     configurable={
        #         "response_model": "anthropic/claude-3-5-sonnet-20241022"
        #     }
        # )
        configuration = AgentConfiguration.from_runnable_config(config)
        max_tokens_value = 4096
        model = load_chat_model(configuration.response_model, max_tokens=max_tokens_value).with_structured_output(CodeGenerated)
        top_k = 20
        context = format_docs_code(docs=state.documents[:top_k], code=state.library_code)
        prompt = configuration.build_app_response_system_prompt.format(steps=state.app_steps, context=context)

    messages = [
        {"role": "system", "content": prompt}
    ] + state.messages
    response = await cast(CodeGenerated, model.ainvoke(messages))

    logger.debug(f"Anthropic Response: {response}")

    return {"frontend": response["frontend"], "backend": response["backend"]}

async def evaluate_code(
    state: AgentState, *, config: RunnableConfig
) -> dict[str, Any]:
    """Evaluate the code generated by the LLM.

    This function evaluates the code generated by the LLM for the provided use case and provides constructive feedback.

    Args:
        state (AgentState): The current state of the agent, including retrieved documents and conversation history, the code generated.
        config (RunnableConfig): Configuration with the model used to respond.

    Returns:
        dict[str, list[BaseMessage]]: A dictionary with a 'messages' key containing the feedback response.
    """
    configuration = AgentConfiguration.from_runnable_config(config)
    model = load_chat_model(configuration.response_model)
    top_k = 20
    context = format_docs_code(docs=state.documents[:top_k], code=state.library_code)
    prompt = configuration.code_evaluation_system_prompt.format(
        frontend=state.frontend,
        backend=state.backend,
        context=context
    )
    messages = [{"role": "system", "content": prompt}] + state.messages
    response = await model.ainvoke(messages)
    return {"messages": [response], "feedback_content": response.content, "code_evaluated": True}

async def generate_requirements_txt(
    state: AgentState, *, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
    """Generate requirements.txt for the application based on the generated code.

    This function generates a requirements file for the provided use case using the conversation history and the documents retrieved by the researcher.

    Args:
        state (AgentState): The current state of the agent, including retrieved documents and conversation history.
        config (RunnableConfig): Configuration with the model used to respond.

    Returns:
        dict[str, list[BaseMessage]]: A dictionary with a 'messages' key containing the generated response.
    """
    configuration = AgentConfiguration.from_runnable_config(config)
    model = load_chat_model(configuration.response_model)
    prompt = configuration.requirements_txt_generation_system_prompt.format(frontend=state.frontend, backend=state.backend)
    messages = [{"role": "system", "content": prompt}] + state.messages
    response = await model.ainvoke(messages)
    return {"messages": [response], "requirements": response.content}

async def generate_readme_md(
    state: AgentState, *, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
    """Generate README.md for the application based on the generated code and requirements.

    This function generates a README file for the provided use case using the conversation history and the documents retrieved by the researcher.

    Args:
        state (AgentState): The current state of the agent, including retrieved documents and conversation history.
        config (RunnableConfig): Configuration with the model used to respond.

    Returns:
        dict[str, list[BaseMessage]]: A dictionary with a 'messages' key containing the generated response.
    """
    configuration = AgentConfiguration.from_runnable_config(config)
    model = load_chat_model(configuration.response_model)
    prompt = configuration.readme_md_txt_generation_system_prompt.format(
        frontend=state.frontend,
        backend=state.backend,
        requirements_txt=state.requirements
    )
    messages = [{"role": "system", "content": prompt}] + state.messages
    response = await model.ainvoke(messages)
    return {"messages": [response], "readme_content": response.content}

def decision_loop(state: AgentState) -> Literal["evaluate_code", "generate_requirements_txt"]:
    """Determine if the code has been reviewed atleast once.

    This function checks if the generated code has been are reviewed atleast once:
        - If it hasn't, route to the `feedback_content` node
        - Otherwise, route END the graph

    Args:
        state (AgentState): The current state of the agent, including the remaining research steps.

    Returns:
        Union[Literal["evaluate_code"], type(END)]: Returns "evaluate_code" if code hasn't been evaluated, 
        or END to terminate the graph.
    """
    if not state.code_evaluated:
        return "evaluate_code"
    else:
        return "generate_requirements_txt"

builder = StateGraph(AgentState, input=InputState, config_schema=AgentConfiguration)
builder.add_node(create_app_research_plan)
builder.add_node(conduct_research)
builder.add_node(build_app)
builder.add_node(evaluate_code)
builder.add_node(generate_requirements_txt)
builder.add_node(generate_readme_md)

builder.add_edge(START, "create_app_research_plan")
builder.add_edge("create_app_research_plan", "conduct_research")
builder.add_conditional_edges("conduct_research", check_finished)
builder.add_conditional_edges("build_app", decision_loop)
builder.add_edge("evaluate_code", "build_app")
builder.add_edge("generate_requirements_txt", "generate_readme_md")
builder.add_edge("generate_readme_md", END)

graph = builder.compile()
graph.name = "CodeGenerationGraph"

