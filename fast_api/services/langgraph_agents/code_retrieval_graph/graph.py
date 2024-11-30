from typing import TypedDict, cast

from langgraph.graph import START, StateGraph, END
from langchain_core.runnables import RunnableConfig

from fast_api.services.langgraph_agents.utils import load_chat_model
from fast_api.services.langgraph_agents.code_retrieval_graph.state import AgentState, InputState
from fast_api.services.langgraph_agents.code_retrieval_graph.configuration import AgentConfiguration

def create_research_plan(
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
    response = cast(Plan, model.invoke(messages))
    return {
        "steps": response["steps"],
        "documents": "delete",
        "query": state.messages[-1].content,
    }

builder = StateGraph(AgentState, input=InputState, config_schema=AgentConfiguration)
builder.add_edge(START, "create_research_plan")
builder.add_node(create_research_plan)
builder.add_edge("create_research_plan", END)

graph = builder.compile()

for chunk in graph.stream({"messages": [{"role": "user", "content": "How do I implement a RAG agent using LangGraph architecture?"}]}):
    print(chunk)

graph.name = "CodeRetrievalGraph"