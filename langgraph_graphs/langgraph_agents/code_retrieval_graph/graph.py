import asyncio

from typing import Any, TypedDict, cast

from langgraph.graph import START, StateGraph, END
from langchain_core.runnables import RunnableConfig

from langgraph_graphs.langgraph_agents.utils import load_chat_model, replace_s3_locations_with_content, remove_code_file_placeholders
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

    Behavior:
        - Invokes the researcher_graph with the first step of the research plan.
        - Updates the state with the retrieved documents and removes the completed step.
    """
    result = await researcher_graph.ainvoke({"question": state.steps[0]})
    
    updated_docs = replace_s3_locations_with_content(result["documents"])
    
    result["documents"] = remove_code_file_placeholders(updated_docs)
    return {"documents": result["documents"], "steps": state.steps[1:]}

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

builder = StateGraph(AgentState, input=InputState, config_schema=AgentConfiguration)
builder.add_edge(START, "create_research_plan")
builder.add_node(create_research_plan)
builder.add_node(conduct_research)
builder.add_edge("create_research_plan", "conduct_research")
builder.add_edge("conduct_research", END)

graph = builder.compile()

async def stream_output():
    async for chunk in graph.astream({"messages": [{"role": "user", "content": "How do I implement a RAG agent using LangGraph architecture?"}]}):
        print(chunk)

asyncio.run(stream_output())

graph.name = "CodeRetrievalGraph"