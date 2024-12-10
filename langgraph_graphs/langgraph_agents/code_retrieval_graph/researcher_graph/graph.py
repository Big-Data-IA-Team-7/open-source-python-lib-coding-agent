"""Researcher graph used in the conversational retrieval system as a subgraph.

This module defines the core structure and functionality of the researcher graph,
which is responsible for generating search queries and retrieving relevant documents.
"""

import logging
from typing import cast
from typing_extensions import TypedDict

from pinecone.core.openapi.shared.exceptions import ServiceException

from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langchain_community.utilities import SQLDatabase

from langgraph_graphs import retrieval
from langgraph_graphs.langgraph_agents.code_retrieval_graph.configuration import AgentConfiguration
from langgraph_graphs.langgraph_agents.code_retrieval_graph.researcher_graph.state import QueryState, ResearcherState, SqlState
from langgraph_graphs.langgraph_agents.code_retrieval_graph.researcher_graph import configuration
from langgraph_graphs.langgraph_agents.utils import load_chat_model, replace_s3_locations_with_content, remove_code_file_placeholders, format_docs

logger = logging.getLogger(__name__)

async def generate_queries(
    state: ResearcherState, *, config: RunnableConfig
) -> dict[str, list[str]]:
    """Generate search queries based on the question (a step in the research plan).

    This function uses a language model to generate diverse search queries to help answer the question.

    Args:
        state (ResearcherState): The current state of the researcher, including the user's question.
        config (RunnableConfig): Configuration with the model used to generate queries.

    Returns:
        dict[str, list[str]]: A dictionary with a 'queries' key containing the list of generated search queries.
    """

    class Response(TypedDict):
        queries: list[str]

    configuration = AgentConfiguration.from_runnable_config(config)
    model = load_chat_model(configuration.query_model).with_structured_output(Response)
    messages = [
        {"role": "system", "content": configuration.generate_queries_system_prompt},
        {"role": "human", "content": state.question},
    ]
    response = cast(Response, await model.ainvoke(messages))
    return {"queries": response["queries"]}

async def retrieve_documents(
    state: QueryState, *, config: RunnableConfig
) -> dict[str, list[Document]]:
    """Retrieve documents based on a given query.

    This function uses a retriever to fetch relevant documents for a given query.

    Args:
        state (QueryState): The current state containing the query string.
        config (RunnableConfig): Configuration with the retriever used to fetch documents.

    Returns:
        dict[str, list[Document]]: A dictionary with a 'documents' key containing the list of retrieved documents.
    """
    try:
        with retrieval.make_retriever(config) as retriever:
            documents = await retriever.ainvoke(state.query, config)
            updated_docs = replace_s3_locations_with_content(documents)
            response = remove_code_file_placeholders(updated_docs)

            logging.debug(f"Retriever Graph: {response}")
            return {"documents": response}
    except ServiceException as e:
        logging.error(f"Pinecone service error: {str(e)}")
        raise  # Re-raise the error to be handled by the calling function

async def list_classes_and_apis(
    state: ResearcherState, *, config: RunnableConfig
) -> dict[str, list[str]]:
    """Generate search queries based on the question (a step in the research plan).

    This function uses a language model to generate diverse search queries to help answer the question.

    Args:
        state (ResearcherState): The current state of the researcher, including the user's question.
        config (RunnableConfig): Configuration with the model used to generate queries.

    Returns:
        dict[str, list[str]]: A dictionary with a 'queries' key containing the list of generated search queries.
    """

    class SqlResponse(TypedDict):
        """Response structure for model output."""
        
        class_names: list[str]
        api_names: list[str]

    configuration = AgentConfiguration.from_runnable_config(config)
    model = load_chat_model(configuration.query_model).with_structured_output(SqlResponse)
    formatted_context = format_docs(docs=state.documents)
    messages = [
        {"role": "system", "content": configuration.sql_code_check_prompt},
        {"role": "human", "content": formatted_context},
    ]
    response = cast(SqlResponse, await model.ainvoke(messages))

    return {"class_names": response["class_names"], "api_names": response["api_names"]}

async def query_database(
        state: SqlState, *, config: RunnableConfig
) -> dict[str, list[tuple[str, ...]]]:
    """Retrieve code based on the documents from an SQL agent.
    
    This function uses an SQL agent to fetch relevant code from Snowflake for a given document.
    
    Args:
        state (ResearcherState): The current state of the researcher, including the user's question.
        config (RunnableConfig): Configuration with the retriever used to fetch documents.

    Returns:
        dict[str, list[tuple[str, ...]]: A dictionary with a 'library_code' key containing the list of code retrieved from the Snowflake db.
    """

    db = SQLDatabase.from_uri(
        f"snowflake://{configuration.SNOWFLAKE_USER}:"
        f"{configuration.SNOWFLAKE_PASSWORD}@"
        f"{configuration.SNOWFLAKE_ACCOUNT}/"
        f"{configuration.SNOWFLAKE_DATABASE}/"
        f"{configuration.SNOWFLAKE_SCHEMA}?"
        f"warehouse={configuration.SNOWFLAKE_WAREHOUSE}&"
        f"role={configuration.SNOWFLAKE_ROLE}"
    )

    names = set(state.class_names) | set(state.api_names)  # Combine both lists and remove duplicates
    formatted_names = ", ".join(f"'{name}'" for name in names)

    query = f"""
    SELECT code FROM EDW.GITHUB_CLASSES WHERE CLASS_NAME IN ({formatted_names})
    UNION
    SELECT code FROM EDW.GITHUB_FUNCTIONS WHERE FUNCTION_NAME IN ({formatted_names});
    """

    response = db.run(query)

    # Process the response to ensure it's in the correct format
    if isinstance(response, str):
        # If it's a string representation of a list of tuples, eval it
        try:
            processed_response = eval(response)
            if not isinstance(processed_response, list):
                processed_response = [processed_response]
        except:
            # If eval fails, wrap the string in a tuple and list
            processed_response = [(response,)]
    elif isinstance(response, list):
        # If it's already a list but elements aren't tuples
        processed_response = [(item,) if not isinstance(item, tuple) else item for item in response]
    else:
        # Fallback case - wrap whatever we got in a tuple and list
        processed_response = [(response,)]

    return {"library_code": processed_response}

def retrieve_in_parallel(state: ResearcherState) -> list[Send]:
    """Create parallel retrieval tasks for each generated query.

    This function prepares parallel document retrieval tasks for each query in the researcher's state.

    Args:
        state (ResearcherState): The current state of the researcher, including the generated queries.

    Returns:
        Literal["retrieve_documents"]: A list of Send objects, each representing a document retrieval task.

    Behavior:
        - Creates a Send object for each query in the state.
        - Each Send object targets the "retrieve_documents" node with the corresponding query.
    """
    return [
        Send("retrieve_documents", QueryState(query=query)) for query in state.queries
    ]

# Define the graph
builder = StateGraph(ResearcherState)
builder.add_node(generate_queries)
builder.add_node(retrieve_documents)
builder.add_node(list_classes_and_apis)
builder.add_node(query_database)

builder.add_edge(START, "generate_queries")
builder.add_conditional_edges(
    "generate_queries",
    retrieve_in_parallel,
    path_map=["retrieve_documents"],
)

builder.add_edge("retrieve_documents", "list_classes_and_apis")
builder.add_edge("list_classes_and_apis", "query_database")
builder.add_edge("query_database", END)

# Compile into a graph object that you can invoke and deploy.
graph = builder.compile()
graph.name = "ResearcherGraph"