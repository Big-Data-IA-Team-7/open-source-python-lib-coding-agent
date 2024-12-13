import time
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from data_load.configuration.parameter_config import PINECONE_API, OPENAI_API
from openai import RateLimitError

def dict_to_document(doc_dict):
    """
    Reconstruct a Document from a dictionary.
    """
    return Document(
        page_content=doc_dict['page_content'], 
        metadata=doc_dict['metadata']
    )


def store_to_pinecone(index_name, **kwargs):
    """
    Store processed documents to a Pinecone index in batches, creating the index if it does not exist.
    
    :param index_name: Name of the Pinecone index.
    :param batch_size: Number of documents to process in each iteration.
    :param kwargs: Additional arguments (e.g., Airflow context).
    """
    from pinecone.exceptions import PineconeApiException
    
    
    ti = kwargs['ti']
    serializable_docs = ti.xcom_pull(key='processed_documents', task_ids='process_and_store_task')
    
    
    full_docs = [dict_to_document(doc_dict) for doc_dict in serializable_docs]
    
    
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large", 
        api_key=OPENAI_API
    )
    pc = Pinecone(api_key=PINECONE_API)
    batch_size=100
    
    if index_name not in pc.list_indexes():
        try:
            pc.create_index(
                name=index_name,
                dimension=3072,  # Dimension for text-embedding-3-large
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        except PineconeApiException as e:
            print(f"Index '{index_name}' already exists.")
    
    
    index = pc.Index(index_name)
    
    
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
    
    
    total_docs = len(split_docs)
    print(f"Total documents to process: {total_docs}")
    
    for i in range(0, total_docs, batch_size):
        batch = split_docs[i:i+batch_size]
        print(f"Processing batch {i // batch_size + 1}/{-(-total_docs // batch_size)}")
        
        
        max_retries = 5
        retry_delay = 60  
        for _ in range(max_retries):
            try:
                vector_store = PineconeVectorStore(
                    index=index, 
                    embedding=embeddings
                )
                vector_store.add_documents(batch)
                break
            except RateLimitError as e:
                print(f"OpenAI RateLimitError encountered: {e}")
                time.sleep(retry_delay)
            except Exception as e:
                print(f"Unexpected error occurred: {e}")
                raise
    
    
    return total_docs
