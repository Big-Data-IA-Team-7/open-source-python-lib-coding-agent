import os
from contextlib import contextmanager
from typing import Iterator
import logging

from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableConfig
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

from fastapi_backend.langgraph_graphs.langgraph_agents.configuration import BaseConfiguration
from fastapi_backend.langgraph_graphs.constants import LANGGRAPH_DOCS_INDEX_NAME, LANGCHAIN_DOCS_INDEX_NAME, LLAMAINDEX_DOCS_INDEX_NAME

logger = logging.getLogger(__name__)

def make_text_encoder(model: str) -> Embeddings:
    """Connect to the configured text encoder."""
    provider, model = model.split("/", maxsplit=1)
    match provider:
        case "openai":

            return OpenAIEmbeddings(model=model)
        case _:
            logger.error(f"Unsupported embedding provider: {provider}")
            raise ValueError(f"Unsupported embedding provider: {provider}")

''' The Context Manager decorator is meant for automatic resource management, im this case,
of retrievers to setup and cleanup of resources. Setting the contextmanager decorator for a function
enables the use of 'with' clause for the function and also guarantees cleanup even if exceptions occur.
'''
@contextmanager
def make_pinecone_retriever(
    configuration: BaseConfiguration, embedding_model: Embeddings, library: str
) -> Iterator[BaseRetriever]:

    pinecone_api_key = os.environ.get("PINECONE_API_KEY", "not_provided")

    index_mapping = {
        'LangGraph': LANGGRAPH_DOCS_INDEX_NAME,
        'LangChain': LANGCHAIN_DOCS_INDEX_NAME,
        'LlamaIndex': LLAMAINDEX_DOCS_INDEX_NAME
    }

    index_name = index_mapping[library]

    vectorstore = PineconeVectorStore(
        index_name=index_name,
        pinecone_api_key=pinecone_api_key,
        embedding=embedding_model
    )

    search_kwargs = {**configuration.search_kwargs}
    yield vectorstore.as_retriever(search_kwargs=search_kwargs)

@contextmanager
def make_retriever(
    config: RunnableConfig,
    library: str
) -> Iterator[BaseRetriever]:
    """Create a retriever for the agent, based on the current configuration."""
    # Create a BaseConfiguration object from the provided config
    configuration = BaseConfiguration.from_runnable_config(config)
    embedding_model = make_text_encoder(configuration.embedding_model)
    
    # Match based on the retriever provider in the configuration
    match configuration.retriever_provider:
        case "pinecone":
            # Use Pinecone retriever when configured
            with make_pinecone_retriever(configuration, embedding_model, library) as retriever:
                yield retriever

        case _:
            # Handle unsupported retriever providers
            logger.error("Unrecognized retriever_provider in configuration.")
            raise ValueError(
                "Unrecognized retriever_provider in configuration. "
                f"Expected one of: {', '.join(BaseConfiguration.__annotations__['retriever_provider'].__args__)}\n"
                f"Got: {configuration.retriever_provider}"
            )