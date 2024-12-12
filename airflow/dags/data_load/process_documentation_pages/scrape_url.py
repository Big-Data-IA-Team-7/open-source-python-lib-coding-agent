from bs4 import BeautifulSoup
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader

def extract_with_metadata(html: str) -> str:
    """Extract content and metadata from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    
    
    title = soup.find('title')
    title_text = title.text.strip() if title else 'Untitled Page'
    
   
    meta_desc = soup.find('meta', {'name': 'description'})
    description = meta_desc.get('content', '').strip() if meta_desc else None
    if not description:
       
        first_p = soup.find('p')
        description = (first_p.text.strip()[:200] + '...') if first_p else 'No description available'
    
    # Set custom attributes that RecursiveUrlLoader will add to metadata
    soup.attrs['extracted_title'] = title_text
    soup.attrs['extracted_description'] = description
    
    # Return the HTML content
    return str(soup)

def load_recursive_url(start_url, base_url, **kwargs):
    """
    Load documents recursively from a given URL.

    :param start_url: The URL to start crawling from.
    :param base_url: The base URL to restrict crawling to.
    :param kwargs: Airflow context dictionary
    :return: Number of documents scraped
    """
    # Create the loader with metadata extraction
    loader = RecursiveUrlLoader(
        start_url,
        max_depth=5,
        prevent_outside=True,
        extractor=extract_with_metadata,
        base_url=base_url
    )
    
    # Load the documents
    documents = loader.load()
    
    # Convert documents to a serializable format with enhanced metadata
    serializable_docs = [
        {
            'page_content': doc.page_content,
            'metadata': {
                'title': doc.metadata.get('extracted_title', 'Untitled Page'),
                'description': doc.metadata.get('extracted_description', 'No description available'),
                'source': doc.metadata.get('url', ''),  
                **doc.metadata  
            }
        } for doc in documents
    ]
    
    
    ti = kwargs['ti']
    ti.xcom_push(key='scraped_documents', value=serializable_docs)
    
    return len(serializable_docs)
