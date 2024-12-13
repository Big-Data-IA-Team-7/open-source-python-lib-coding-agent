from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, StateGraph, END

from fastapi_backend.langgraph_graphs.langgraph_agents.utils import load_chat_model, format_docs_code, web_search, scrape_url
from fastapi_backend.langgraph_graphs.langgraph_agents.code_retrieval_graph.researcher_graph.graph import graph as researcher_graph
from fastapi_backend.langgraph_graphs.langgraph_agents.error_handling_graph.state import AgentState, InputState
from fastapi_backend.langgraph_graphs.langgraph_agents.code_retrieval_graph.configuration import AgentConfiguration

async def conduct_web_search(state: AgentState) -> dict[str, Any]:
    """Perform web search to find relevant information about the error.

    This function performs a web search to find the relevant information about the error

    Args:
        state (AgentState): The current state of the agent.

    Returns:
        dict[str, str]: The content of the urls from the web search containing the information about the error
    """
    # Handle web search logic here.
    state.query  = f"Correct this code: {state.code}. Error: {state.error}."
    # Perform the search using SerpAPI
    search_results = web_search(state.query)
    print("Search Result URLs:")
    urls = [result['link'] for result in search_results]  # Get URLs from the results
    for url in urls:
        print(url)
    
    # Scrape content from the URLs
    scraped_contents = []
    for url in urls:
        scraped_content = scrape_url(url)
        scraped_contents.append(scraped_content)
    search_content = "\n\n".join(scraped_contents)
    return {"web_search": search_content, "query": state.messages[-1].content}

async def conduct_research(state: AgentState) -> dict[str, Any]:
    """Execute the first step of the research plan.

    This function takes the first step from the research plan and uses it to conduct research.

    Args:
        state (AgentState): The current state of the agent, including the research plan steps.

    Returns:
        dict[str, list[str]]: A dictionary with 'documents' containing the research results and
                              'steps' containing the remaining research steps.
    """
    result = await researcher_graph.ainvoke({"question": state.query, "library": state.library})

    return {"documents": result["documents"], "library_code": result["library_code"]}

async def handle_error(
    state: AgentState, *, config: RunnableConfig
) -> dict[str, str]:
    """Generate a final response to the user's query based on the retrieved documents.

    This function formulates a comprehensive answer using the web search information and the documents retrieved by the researcher.

    Args:
        state (AgentState): The current state of the agent, including retrieved documents.
        config (RunnableConfig): Configuration with the model used to respond.

    Returns:
        dict[str, list[str]]: A dictionary with a 'messages' key containing the generated response.
    """
    configuration = AgentConfiguration.from_runnable_config(config)
    model = load_chat_model(configuration.response_model)
    top_k = 20
    context = format_docs_code(docs=state.documents[:top_k], code=state.library_code)
    prompt = configuration.eh_response_system_prompt.format(
        task=state.task,
        code=state.code,
        error=state.error,
        context=context,
        web_search=state.web_search
    )

    messages = [{"role": "system", "content": prompt}] + state.messages
    response = await model.ainvoke(messages)
    return {"answer": response.content}

builder = StateGraph(AgentState, input=InputState, config_schema=AgentConfiguration)
builder.add_node(conduct_web_search)
builder.add_node(conduct_research)
builder.add_node(handle_error)

builder.add_edge(START, "conduct_web_search")
builder.add_edge("conduct_web_search", "conduct_research")
builder.add_edge("conduct_research", "handle_error")
builder.add_edge("handle_error", END)

graph = builder.compile()
graph.name = "ErrorHandlingGraph"