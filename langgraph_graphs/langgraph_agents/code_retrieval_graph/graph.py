from typing import Any, TypedDict, cast, Literal

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage
from langgraph.graph import START, StateGraph, END

from langgraph_graphs.langgraph_agents.utils import load_chat_model, format_docs_code
from langgraph_graphs.langgraph_agents.code_retrieval_graph.researcher_graph.graph import graph as researcher_graph
from langgraph_graphs.langgraph_agents.code_retrieval_graph.state import AgentState, InputState
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

    return {"documents": result["documents"], "code": result["code"], "steps": state.steps[1:]}

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

def check_finished(state: AgentState) -> Literal["respond", "conduct_research"]:
    """Determine if the research process is complete or if more research is needed.

    This function checks if there are any remaining steps in the research plan:
        - If there are, route back to the `conduct_research` node
        - Otherwise, route to the `respond` node

    Args:
        state (AgentState): The current state of the agent, including the remaining research steps.

    Returns:
        Literal["respond", "conduct_research"]: The next step to take based on whether research is complete.
    """
    if len(state.steps or []) > 0:
        return "conduct_research"
    else:
        return "respond"

async def respond(
    state: AgentState, *, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
    """Generate a final response to the user's query based on the conducted research.

    This function formulates a comprehensive answer using the conversation history and the documents retrieved by the researcher.

    Args:
        state (AgentState): The current state of the agent, including retrieved documents and conversation history.
        config (RunnableConfig): Configuration with the model used to respond.

    Returns:
        dict[str, list[str]]: A dictionary with a 'messages' key containing the generated response.
    """
    configuration = AgentConfiguration.from_runnable_config(config)
    model = load_chat_model(configuration.response_model)
    top_k = 20
    context = format_docs_code(docs=state.documents[:top_k], code=state.code)
    prompt = configuration.response_system_prompt.format(context=context)
    messages = [{"role": "system", "content": prompt}] + state.messages
    response = await model.ainvoke(messages)
    return {"messages": [response], "answer": response.content}

builder = StateGraph(AgentState, input=InputState, config_schema=AgentConfiguration)
builder.add_node(create_research_plan)
builder.add_node(conduct_research)
builder.add_node(respond)

builder.add_edge(START, "create_research_plan")
builder.add_edge("create_research_plan", "conduct_research")
builder.add_conditional_edges("conduct_research", check_finished)
builder.add_edge("respond", END)

graph = builder.compile()
graph.name = "CodeRetrievalGraph"