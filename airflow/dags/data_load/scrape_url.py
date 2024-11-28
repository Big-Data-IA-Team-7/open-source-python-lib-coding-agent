from bs4 import BeautifulSoup
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader

def load_recursive_url(**kwargs):
    """
    Load documents recursively from the LangGraph documentation site.
    
    :param kwargs: Airflow context dictionary
    :return: Number of documents scraped
    """
    # Create the loader
    loader = RecursiveUrlLoader(
        "https://langchain-ai.github.io/langgraph/",
        max_depth=5,
        prevent_outside=True,
        extractor=lambda x: str(BeautifulSoup(x, "html.parser")),
        base_url="https://langchain-ai.github.io/langgraph/"
    )
    
    # Load the documents
    documents = loader.load()
    
    # Convert documents to a serializable format
    serializable_docs = [
        {
            'page_content': doc.page_content,
            'metadata': doc.metadata
        } for doc in documents
    ]
    
    # Push the documents to XCom so they can be used by subsequent tasks
    ti = kwargs['ti']
    ti.xcom_push(key='scraped_documents', value=serializable_docs)
    
    #return len(serializable_docs)  # Return the number of documents for logging/tracking