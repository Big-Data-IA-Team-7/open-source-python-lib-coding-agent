import os
import json
import hashlib
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from data_load.utils.helper_functions import clean_and_normalize_code, determine_file_extension, get_code_definitions, upload_file_to_s3
from data_load.parameter_config import AWS_S3_BUCKET_NAME


def process_content(**kwargs):
    """
    Processes loaded URLs and stores extracted code and metadata.
    
    :param kwargs: Airflow context dictionary
    :return: Number of processed documents
    """
    # Retrieve documents from XCom
    ti = kwargs['ti']
    documents = ti.xcom_pull(key='scraped_documents', task_ids='load_recursive_url_task')
    
    # Get S3 bucket name and local output directory from kwargs
    output_dir = kwargs.get('output_dir', 'langgraph_code_extracts')
    os.makedirs(output_dir, exist_ok=True)
    
    full_docs = []
    
    for doc in documents:
        soup = BeautifulSoup(str(doc['page_content']), 'html.parser')
        full_text = str(soup)
        code_blocks = soup.find_all(['pre', 'code'])
        
        for code_block in reversed(code_blocks):
            code_content = clean_and_normalize_code(code_block.get_text())
            code_lines = code_content.strip().split('\n')
            
            if len(code_lines) > 3:
                # Generate unique filename based on code content
                filename_base = hashlib.md5(code_content.encode()).hexdigest()
                ext = determine_file_extension(code_content)
                local_filename = os.path.join(output_dir, f"{filename_base}{ext}")
                
                # Write code to local file
                with open(local_filename, 'w', encoding='utf-8') as f:
                    f.write(code_content)
                
                # Upload to S3
                s3_key = f"code_extracts/langgraph-docs/{filename_base}{ext}"
                upload_success = upload_file_to_s3(
                    file_path=local_filename, 
                    s3_key=s3_key
                )
                
                # Generate code description
                try:
                    code_description = get_code_definitions(code_content)
                except Exception as e:
                    code_description = f"Unable to generate description: {str(e)}"
                
                # Append S3 location to description if upload was successful
                if upload_success:
                    code_description += f"\nS3 Location: s3://{AWS_S3_BUCKET_NAME}/{s3_key}"
                
                # Replace code block with description in text
                description_text = f"[CODE FILE: {s3_key}]\n{code_description}"
                full_text = full_text.replace(str(code_block), description_text)
        
        # Clean the text
        soup_result = BeautifulSoup(full_text, 'html.parser')
        clean_text = soup_result.get_text(separator='\n', strip=True)
        
        # Create document
        full_doc = Document(
            page_content=clean_text, 
            metadata=doc['metadata']
        )
        full_docs.append(full_doc)
    
    # Convert documents to dictionaries for XCom
    serializable_docs = [
        {
            'page_content': doc.page_content,
            'metadata': doc.metadata
        } for doc in full_docs
    ]
    
    # Push processed documents to XCom
    ti.xcom_push(key='processed_documents', value=serializable_docs)
    
    return len(serializable_docs)  # Return number of processed documents
