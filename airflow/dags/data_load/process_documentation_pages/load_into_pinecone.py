import os
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from data_load.configuration.parameter_config import PINECONE_API, OPENAI_API


def dict_to_document(doc_dict):
    """
    Reconstruct a Document from a dictionary.
    
    :param doc_dict: Dictionary representation of a Document
    :return: Reconstructed Document object
    """
    return Document(
        page_content=doc_dict['page_content'], 
        metadata=doc_dict['metadata']
    )


def store_to_pinecone(index_name, **kwargs):
    """
    Store processed documents to a Pinecone index, creating the index if it does not exist.
    
    :param index_name: Name of the Pinecone index.
    :param kwargs: Airflow context dictionary.
    :return: Number of documents processed.
    """
    # Retrieve processed documents from XCom
    ti = kwargs['ti']
    serializable_docs = ti.xcom_pull(key='processed_documents', task_ids='process_and_store_task')
    
    # Reconstruct Document objects
    full_docs = [dict_to_document(doc_dict) for doc_dict in serializable_docs]
    
    # Initialize embeddings and Pinecone client
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large", 
        api_key=OPENAI_API
    )
    pc = Pinecone(api_key=PINECONE_API)
    
    # Create index if it does not exist
    if index_name not in pc.list_indexes():
        pc.create_index(
            name=index_name,
            dimension=3072,  # Dimension for text-embedding-3-large
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    
    # Retrieve the index
    index = pc.Index(index_name)
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000, 
        chunk_overlap=200
    )
    split_docs = []
    for doc in full_docs:
        splits = text_splitter.split_text(doc.page_content)
        split_docs.extend([
            Document(
                page_content=split,
                metadata={
                    'title': doc.metadata.get('title', 'Untitled'),
                    'source': doc.metadata.get('source', ''),
                    'description': doc.metadata.get('description', 'No description available'),
                }
            ) for split in splits
        ])
    
    # Add documents to the Pinecone vector store
    vector_store = PineconeVectorStore(
        index=index, 
        embedding=embeddings
    )
    vector_store.add_documents(split_docs)
    
    # Return the number of documents processed for logging
    return len(split_docs)
