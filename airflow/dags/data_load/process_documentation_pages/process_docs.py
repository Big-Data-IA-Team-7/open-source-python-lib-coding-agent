import os
import hashlib
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from data_load.process_documentation_pages.utils.helper_functions import clean_and_normalize_code, determine_file_extension, get_code_definitions, upload_file_to_s3
from data_load.configuration.parameter_config import AWS_S3_BUCKET_NAME

def process_content(file_dir, **kwargs):
    """
    Processes loaded URLs and stores extracted code and metadata.
    
    :param file_dir: Directory name for storing code extracts.
    :param kwargs: Airflow context dictionary.
    :return: Number of processed documents.
    """
   
    ti = kwargs['ti']
    documents = ti.xcom_pull(key='scraped_documents', task_ids='load_recursive_url_task')
    
    
    os.makedirs(file_dir, exist_ok=True)
    
    full_docs = []
    
    for doc in documents:
        
        if len(doc['page_content']) < 300 or "404 - Not Found" in doc['page_content']:
            continue
        
        soup = BeautifulSoup(str(doc['page_content']), 'html.parser')
        full_text = str(soup)
        code_blocks = soup.find_all(['pre', 'code'])
        
        for code_block in reversed(code_blocks):
            code_content = clean_and_normalize_code(code_block.get_text())
            code_lines = code_content.strip().split('\n')
            
            if len(code_lines) > 5:
                
                filename_base = hashlib.md5(code_content.encode()).hexdigest()
                ext = determine_file_extension(code_content)
                local_filename = os.path.join(file_dir, f"{filename_base}{ext}")
                
                
                with open(local_filename, 'w', encoding='utf-8') as f:
                    f.write(code_content)
                
               
                s3_key = f"code_extracts/{file_dir}/{filename_base}{ext}"
                upload_success = upload_file_to_s3(
                    file_path=local_filename, 
                    s3_key=s3_key
                )
                
                
                try:
                    code_description = get_code_definitions(code_content)
                except Exception as e:
                    code_description = f"Unable to generate description: {str(e)}"
                
                
                if upload_success:
                    code_description += f"\nS3 Location: s3://{AWS_S3_BUCKET_NAME}/{s3_key}"
                
                
                description_text = f"[CODE FILE: {s3_key}]\n{code_description}"
                full_text = full_text.replace(str(code_block), description_text)
        
        
        soup_result = BeautifulSoup(full_text, 'html.parser')
        clean_text = soup_result.get_text(separator='\n', strip=True)
        
        
        full_doc = Document(
            page_content=clean_text, 
            metadata={
                'title': doc['metadata'].get('title', 'Untitled'),
                'source': doc['metadata'].get('source', ''),
                'description': doc['metadata'].get('description', 'No description available'),
                **doc['metadata']  # Include any additional metadata
            }
        )
        full_docs.append(full_doc)
    
    
    serializable_docs = [
        {
            'page_content': doc.page_content,
            'metadata': doc.metadata
        } for doc in full_docs
    ]
    
    
    ti.xcom_push(key='processed_documents', value=serializable_docs)
    
    return len(serializable_docs)  # Return number of processed documents
