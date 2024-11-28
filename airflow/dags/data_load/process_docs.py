import os
import hashlib
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from data_load.utils.helper_functions import clean_and_normalize_code, determine_file_extension, get_code_definitions

def process_content(loader, **kwargs):
    """
    Processes loaded URLs and stores extracted code and metadata.
    """
    output_dir = kwargs.get('output_dir', 'langgraph_code_extracts')
    os.makedirs(output_dir, exist_ok=True)
    full_docs = []

    for doc in loader.load():
        soup = BeautifulSoup(str(doc.page_content), 'html.parser')
        full_text = str(soup)
        code_blocks = soup.find_all(['pre', 'code'])

        for code_block in reversed(code_blocks):
            code_content = clean_and_normalize_code(code_block.get_text())
            code_lines = code_content.strip().split('\n')

            if len(code_lines) > 3:
                filename_base = hashlib.md5(code_content.encode()).hexdigest()
                ext = determine_file_extension(code_content)
                filename = os.path.join(output_dir, f"{filename_base}{ext}")

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code_content)

                try:
                    code_description = get_code_definitions(code_content)
                except Exception as e:
                    code_description = f"Unable to generate description: {str(e)}"

                description_text = f"[CODE FILE: {filename}]\n{code_description}"
                full_text = full_text.replace(str(code_block), description_text)

        soup_result = BeautifulSoup(full_text, 'html.parser')
        clean_text = soup_result.get_text(separator='\n', strip=True)
        full_doc = Document(page_content=clean_text, metadata=doc.metadata)
        full_docs.append(full_doc)

    return full_docs
