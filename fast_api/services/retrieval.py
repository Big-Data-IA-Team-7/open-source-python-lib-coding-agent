from dotenv import load_dotenv
load_dotenv()

import os
from contextlib import contextmanager
from typing import Iterator

from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableConfig
from langchain_pinecone import PineconeVectorStore

from fast_api.services.langgraph_agents.configuration import BaseConfiguration
from fast_api.services.constants import PINECONE_DOCS_INDEX_NAME


def make_text_encoder(model: str) -> Embeddings:
    """Connect to the configured text encoder."""
    provider, model = model.split("/", maxsplit=1)
    match provider:
        case "openai":
            from langchain_openai import OpenAIEmbeddings

            return OpenAIEmbeddings(model=model)
        case _:
            raise ValueError(f"Unsupported embedding provider: {provider}")


@contextmanager
def make_pinecone_retriever(
    configuration: BaseConfiguration, embedding_model: Embeddings
) -> Iterator[BaseRetriever]:

    pinecone_api_key = os.environ.get("PINECONE_API_KEY", "not_provided")

    print(pinecone_api_key)

    vectorstore = PineconeVectorStore(index_name=PINECONE_DOCS_INDEX_NAME,
                                                pinecone_api_key=pinecone_api_key,
                                                embedding=embedding_model)

    search_kwargs = {**configuration.search_kwargs}
    yield vectorstore.as_retriever(search_kwargs=search_kwargs)

@contextmanager
def make_retriever(
    config: RunnableConfig,
) -> Iterator[BaseRetriever]:
    """Create a retriever for the agent, based on the current configuration."""
    # Create a BaseConfiguration object from the provided config
    configuration = BaseConfiguration.from_runnable_config(config)
    embedding_model = make_text_encoder(configuration.embedding_model)
    
    # Match based on the retriever provider in the configuration
    match configuration.retriever_provider:
        case "pinecone":
            # Use Pinecone retriever when configured
            with make_pinecone_retriever(configuration, embedding_model) as retriever:
                yield retriever

        case _:
            # Handle unsupported retriever providers
            raise ValueError(
                "Unrecognized retriever_provider in configuration. "
                f"Expected one of: {', '.join(BaseConfiguration.__annotations__['retriever_provider'].__args__)}\n"
                f"Got: {configuration.retriever_provider}"
            )