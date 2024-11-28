from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from data_load.parameter_config import PINECONE_API,OPENAI_API
import os

def store_to_pinecone(full_docs, **kwargs):
    """
    Store full_docs to a Pinecone index, creating the index if it does not exist.
    """
    # Initialize embeddings and Pinecone client
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=OPENAI_API)
    pc = Pinecone(api_key=PINECONE_API)

    # Define index name
    index_name = 'langgraph-docs'

    # Create index if it does not exist
    if index_name not in pc.list_indexes():
        pc.create_index(
            name=index_name,
            dimension=3072,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    # Retrieve the index
    index = pc.Index(index_name)

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=200)
    text_docs = [doc.page_content for doc in full_docs]
    split_docs = text_splitter.create_documents(text_docs)

    # Add documents to the Pinecone vector store
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)
    vector_store.add_documents(split_docs)
