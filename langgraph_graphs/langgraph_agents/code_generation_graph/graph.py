from typing import Any, TypedDict, cast, Literal

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage
from langgraph.graph import START, StateGraph, END

from langgraph_graphs.langgraph_agents.utils import load_chat_model, format_docs_code
from langgraph_graphs.langgraph_agents.code_retrieval_graph.researcher_graph.graph import graph as researcher_graph
from langgraph_graphs.langgraph_agents.code_generation_graph.state import AgentState, InputState
from langgraph_graphs.langgraph_agents.code_retrieval_graph.configuration import AgentConfiguration






async def conduct_research(state: AgentState) -> dict[str, Any]:
    """Execute the first step of the research plan.

    This function takes the first step from the research plan and uses it to conduct research.

    Args:
        state (AgentState): The current state of the agent, including the research plan steps.

    Returns:
        dict[str, list[str]]: A dictionary with 'documents' containing the research results and
                              'steps' containing the remaining research steps.
    """
    result = await researcher_graph.ainvoke({"question": state.steps[0]})

    return {"documents": result["documents"], "code": result["library_code"], "steps": state.steps[1:]}





async def create_research_plan(
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

        steps: list[str]

    configuration = AgentConfiguration.from_runnable_config(config)
    model = load_chat_model(configuration.query_model).with_structured_output(Plan)
    messages = [
        {"role": "system", "content": configuration.research_plan_system_prompt}
    ] + state.messages
    response = await cast(Plan, model.ainvoke(messages))
    return {
        "steps": response["steps"],
        "documents": "delete",
        "query": state.messages[-1].content,
    }





def check_finished(state: AgentState) -> Literal["generate_code", "conduct_research"]:
    """Determine if the research process is complete or if more research is needed.

    This function checks if there are any remaining steps in the research plan:
        - If there are, route back to the `conduct_research` node
        - Otherwise, route to the `respond` node

    Args:
        state (AgentState): The current state of the agent, including the remaining research steps.

    Returns:
        Literal["generate_code", "conduct_research"]: The next step to take based on whether research is complete.
    """
    if len(state.steps or []) > 0:
        return "conduct_research"
    else:
        return "generate_code"
    


async def generate_code(
    state: AgentState, *, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
    """Generate code for a complete application based on the user's query and conducted research.

    This function generates complete application code for the provided use case using the conversation history and the documents retrieved by the researcher.

    Args:
        state (AgentState): The current state of the agent, including retrieved documents and conversation history.
        config (RunnableConfig): Configuration with the model used to respond.

    Returns:
        dict[str, list[BaseMessage]]: A dictionary with a 'messages' key containing the generated response.
    """
    configuration = AgentConfiguration.from_runnable_config(config)
    model = load_chat_model(configuration.response_model)
    top_k = 20
    context = format_docs_code(docs=state.documents[:top_k], code=state.code)
    prompt = configuration.code_generation_system_prompt.format(context=context)
    messages = [{"role": "system", "content": prompt}] + state.messages
    response = await model.ainvoke(messages)
    return {"messages": [response], "code_generated": response.content}

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
    prompt = configuration.requirements_txt_generation_system_prompt.format(code=state.code_generated)
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
        code=state.code_generated,
        requirements_txt=state.requirements
    )
    messages = [{"role": "system", "content": prompt}] + state.messages
    response = await model.ainvoke(messages)
    return {"messages": [response], "readme_content": response.content}

async def evaluate_code(
    state: AgentState, *, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
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
    top_k = 10
    context = format_docs_code(docs=state.documents[:top_k], code=state.code)
    prompt = configuration.code_evaluation_system_prompt.format(
        context=context,
        code=state.code_generated, 
        readme_content=state.readme_content, 
        requirements=state.requirements
    )
    messages = [{"role": "system", "content": prompt}] + state.messages
    response = await model.ainvoke(messages)
    return {"messages": [response], "feedback_content": response.content}

async def judge_evaluation(state: AgentState, *, config: RunnableConfig) -> dict[str, list[BaseMessage]]:
    """Judge and score the code generated by the LLM.

    This function evaluates the code generated by the LLM for the provided use case and provides constructive feedback.

    Args:
        state (AgentState): The current state of the agent, including retrieved documents and conversation history, the code generated.
        config (RunnableConfig): Configuration with the model used to respond.

    Returns:
        dict[str, list[BaseMessage]]: A dictionary with a 'messages' key containing the feedback response.
    """
    configuration = AgentConfiguration.from_runnable_config(config)
    model = load_chat_model(configuration.response_model)
    prompt = configuration.judge_evaluation_system_prompt.format(
        feedback=state.feedback_content
    )
    messages = [{"role": "system", "content": prompt}] + state.messages
    response = await model.ainvoke(messages)
    return {"messages": [response], "feedback_value": response.content}


def decision_loop(state: AgentState) -> Literal["send_response", "generate_code","generate_requirements_txt"]:
    return "send_response"



'''def decision_loop(state: AgentState) -> Literal["send_response", "generate_code","generate_requirements_txt"]:
    if state.feedback_value == 0:
        return "send_response"
    elif state.feedback_value == 1:
        return "generate_code"
    elif state.feedback_value == 2:
        return "generate_requirements_txt"
    else:
        return "generate_readme_md"
'''

def send_response(state: AgentState) -> dict[str, Any]:
    return {
        "code_generated": state.code_generated,
        "requirements": state.requirements,
        "readme": state.readme_content
    }

builder = StateGraph(AgentState, input=InputState, config_schema=AgentConfiguration)
builder.add_node(create_research_plan)
builder.add_node(conduct_research)
builder.add_node(generate_code)
builder.add_node(generate_requirements_txt)
builder.add_node(generate_readme_md)
builder.add_node(evaluate_code)
builder.add_node(judge_evaluation)
builder.add_node(send_response)

builder.add_edge(START, "create_research_plan")
builder.add_edge("create_research_plan", "conduct_research")
builder.add_conditional_edges("conduct_research", check_finished)
builder.add_edge("generate_code", "generate_requirements_txt")
builder.add_edge("generate_requirements_txt", "generate_readme_md")
builder.add_edge("generate_readme_md", "evaluate_code")
builder.add_edge("evaluate_code", "judge_evaluation")
builder.add_conditional_edges("judge_evaluation", decision_loop)
builder.add_edge("send_response", END)

graph = builder.compile()
graph.name = "CodeGenerationGraph"



async def run_graph():
    """Run the graph with a user query."""
    result = await graph.ainvoke({
        "messages": [{"role": "user", "content": "Build an RAG application using Langgraph to build a chatbot for Boston flight company"}]
    })
    print(result['code_generated'])

import asyncio

asyncio.run(run_graph())

