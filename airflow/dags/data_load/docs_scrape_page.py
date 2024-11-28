from bs4 import BeautifulSoup
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader
import os
import re
import hashlib
import requests
from langchain_core.documents import Document
from typing import List, Dict, Union
from openai import OpenAI
from data_load.parameter_config import OPENAI_API

def clean_and_normalize_code(code_content: str) -> str:
    """
    Clean and normalize the code content, preserving its original formatting
    
    Args:
        code_content (str): The raw code content
    
    Returns:
        str: Cleaned and normalized code content
    """
    # Remove any leading/trailing whitespace while preserving internal formatting
    lines = code_content.splitlines()
    
    # Remove any common leading whitespace
    if lines:
        # Determine the minimum indentation
        indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
        min_indent = min(indents) if indents else 0
        
        # Remove common leading whitespace
        lines = [line[min_indent:] if line.strip() else line for line in lines]
    
    # Rejoin the lines, preserving original line breaks
    return '\n'.join(lines)


def determine_file_extension(code_content: str) -> str:
    """
    Determine the file extension based on code content
    
    Args:
        code_content (str): The code content to analyze
    
    Returns:
        str: Appropriate file extension (.py or .sh)
    """
    # Check for Python-specific keywords
    py_indicators = [
        r'\bdef\b', r'\bclass\b', r'\bimport\b', r'\bself\b', 
        r':\s*$', r'from\s+\w+\s+import', r'__\w+__'
    ]
    
    # Check for Bash-specific indicators
    bash_indicators = [
        r'^#!/bin/bash', r'^#!/usr/bin/env\s+bash', 
        r'\becho\b', r'\bls\b', r'\bgrep\b', r'\bcat\b', 
        r'\bsed\b', r'\bawk\b', r'\bmkdir\b'
    ]
    
    # Check Python indicators first
    for pattern in py_indicators:
        if re.search(pattern, code_content, re.MULTILINE):
            return '.py'
    
    # Then check Bash indicators
    for pattern in bash_indicators:
        if re.search(pattern, code_content, re.MULTILINE):
            return '.sh'
    
    # Default to Python if no clear indication
    return '.py'




def get_code_definitions(code_snippets):
    """
    Generates definitions for a batch of code snippets using OpenAI API.
    """
    client = OpenAI(api_key=OPENAI_API)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that explains code snippets. Strictly describe the functionality of the code in 4-5 lines."},
                {"role": "user", "content": f"Explain what the following code does:\n\n{code_snippets}"}
            ],
            temperature=0.7
        )
        definitions = response.choices[0].message.content
    except Exception as e:
        definitions = f"Error: {str(e)}"
    return definitions



def extract_full_text(loader: RecursiveUrlLoader, output_dir: str = 'extracted_code') -> List[Document]:
    """
    Extract full text from loaded documents, saving code blocks to separate files
    with their descriptions
    
    Args:
        loader (RecursiveUrlLoader): Loaded documentation pages
        output_dir (str): Directory to save extracted code files
    
    Returns:
        List of Documents with extracted text and code references
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    full_docs = []
    
    for doc in loader.load():
        # Ensure we're working with the BeautifulSoup object
        if isinstance(doc.page_content, BeautifulSoup):
            soup = doc.page_content
        else:
            soup = BeautifulSoup(str(doc.page_content), 'html.parser')
        
        # Extract full text content with code blocks
        full_text = str(soup)
        
        # Find all code blocks
        code_blocks = soup.find_all(['pre', 'code'])
        
        # Process code blocks in reverse order to maintain correct replacement
        for code_block in reversed(code_blocks):
            # Extract code content
            code_content = clean_and_normalize_code(code_block.get_text())
            
            # Check number of lines in the code block
            code_lines = code_content.strip().split('\n')
            
            # Only extract to separate file if more than 3 lines
            if len(code_lines) > 3:
                # Only process if code content is not empty
                if code_content.strip():
                    # Generate a unique filename based on hash of content
                    filename_base = hashlib.md5(code_content.encode()).hexdigest()
                    
                    # Determine file extension
                    ext = determine_file_extension(code_content)
                    
                    # Create full filename
                    filename = os.path.join(output_dir, f"{filename_base}{ext}")
                    
                    # Write code to file
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(code_content)
                    
                    # Get code description
                    try:
                        code_description = get_code_definitions(code_content)
                    except Exception as e:
                        code_description = f"Unable to generate description: {str(e)}"
                    
                    # Create a description string that includes filename and description
                    description_text = f"[CODE FILE: {filename}]\n{code_description}"
                    
                    # Replace the entire code block with its description
                    # Using str(code_block) to match the entire block HTML
                    full_text = full_text.replace(str(code_block), description_text)
            # If 3 or fewer lines, keep as part of the text
            else:
                # Keep the original code block in the text
                continue
        
        # Convert back to BeautifulSoup to extract text
        soup_result = BeautifulSoup(full_text, 'html.parser')
        
        # Extract clean text
        clean_text = soup_result.get_text(separator='\n', strip=True)
        
        # Create a new Document with full extracted text as a string
        full_doc = Document(
            page_content=clean_text,
            metadata=doc.metadata
        )
        full_docs.append(full_doc)
    
    return full_docs





# Modified loader to ensure proper extraction
loader = RecursiveUrlLoader(
    "https://langchain-ai.github.io/langgraph/",
    max_depth=5,
    prevent_outside=True,
    # Use a lambda that returns a string instead of BeautifulSoup
    extractor=lambda x: str(BeautifulSoup(x, "html.parser")),
    base_url="https://langchain-ai.github.io/langgraph/"
)

# Extract full text with markers
full_text_docs = extract_full_text(loader, output_dir='langgraph_code_extracts')



print(full_text_docs[0])