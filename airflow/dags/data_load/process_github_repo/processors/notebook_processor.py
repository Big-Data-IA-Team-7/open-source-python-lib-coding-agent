import json
from bs4 import BeautifulSoup
from bs4.builder import ParserRejectedMarkup
from pathlib import Path
from typing import Dict, Any, List
from pathlib import Path

def convert_html_to_markdown(html_content: str) -> str:
    """
    Converts HTML content in markdown cells to plain markdown and extracts links.
    
    Args:
        html_content (str): HTML content to convert
        
    Returns:
        str: Converted markdown content
        
    Raises:
        ParserRejectedMarkup: If the HTML content is malformed
        ValueError: If the input is not a string
    """
    if not isinstance(html_content, str):
        error_msg = f"Expected string input, got {type(html_content)}"
        print(f"Error: {error_msg}")
        raise ValueError(error_msg)
        
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        plain_text = soup.get_text()

        links = []
        for a_tag in soup.find_all('a', href=True):
            try:
                links.append(f"[{a_tag.text}]({a_tag['href']})")
            except KeyError as e:
                print(f"Warning: Malformed link tag found: {a_tag}. Error: {e}")
                continue

        markdown_content = plain_text.strip() + "\n" + "\n".join(links)
        return markdown_content
        
    except ParserRejectedMarkup as e:
        print(f"Error: Failed to parse HTML content: {e}")
        return html_content  # Return original content if parsing fails
    except Exception as e:
        print(f"Error: Unexpected error in markdown conversion: {e}")
        return html_content

def get_parent_folder_name(file_path: Path) -> str:
    """
    Extract the immediate parent folder name from a file path.
    
    Args:
        file_path (Path): Path object representing the file location
        
    Returns:
        str: Name of the immediate parent folder, or "root" if in root directory
    """
    try:
        # Get the parent folder
        parent_folder = file_path.parent
        
        # If the parent is the root directory, return "root"
        if parent_folder == Path():
            return "root"
            
        # Return the name of the immediate parent folder
        return parent_folder.name
        
    except Exception as e:
        print(f"Error: Could not extract folder name from {file_path}: {e}")
        return "unknown"

def extract_notebook_cells(filepath) :
    """
    Process a single .ipynb file, extracting code cells with surrounding markdown context.
    
    Args:
        filepath (Path): Path to the Jupyter notebook file
        
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing processed cell information
        
    Raises:
        FileNotFoundError: If the notebook file doesn't exist
        json.JSONDecodeError: If the notebook is not valid JSON
        UnicodeDecodeError: If the file encoding is not supported
    """
    '''if not filepath.exists():
        error_msg = f"Notebook file not found: {filepath}"
        print(f"Error: {error_msg}")
        raise FileNotFoundError(error_msg) '''
    filepath = Path(filepath)
    processed_cells = []
    markdown_buffer = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                notebook_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid notebook format in {filepath}: {e}")
                raise
    except UnicodeDecodeError as e:
        print(f"Error: Encoding error in {filepath}: {e}")
        raise
    except Exception as e:
        print(f"Error: Error reading notebook {filepath}: {e}")
        raise

    # Validate notebook structure
    if not isinstance(notebook_data, dict) or 'cells' not in notebook_data:
        error_msg = f"Invalid notebook structure in {filepath}: missing 'cells' key or incorrect format"
        print(f"Error: {error_msg}")
        return []

    # Get the folder name once for all cells
    folder_name = get_parent_folder_name(filepath)

    for index, cell in enumerate(notebook_data.get('cells', [])):
        try:
            cell_type = cell.get('cell_type')
            if cell_type not in ['markdown', 'code']:
                print(f"Warning: Skipping unknown cell type '{cell_type}' in {filepath}")
                continue

            source_content = cell.get('source', [])
            if isinstance(source_content, list):
                source_content = ''.join(source_content)
            elif not isinstance(source_content, str):
                print(f"Warning: Unexpected source content type in {filepath}: {type(source_content)}")
                continue

            if cell_type == 'markdown':
                try:
                    markdown_text = convert_html_to_markdown(source_content)
                    markdown_buffer.append(markdown_text)
                except Exception as e:
                    print(f"Warning: Error converting markdown in {filepath}: {e}")
                    markdown_buffer.append(source_content)
                    
            elif cell_type == 'code':
                markdown_above = '\n'.join(markdown_buffer) if markdown_buffer else "Markdown not found"
                markdown_below = "Markdown not found"

                # Look ahead for following markdown
                try:
                    for next_index in range(index + 1, len(notebook_data['cells'])):
                        next_cell = notebook_data['cells'][next_index]
                        if next_cell['cell_type'] == 'markdown':
                            next_source = ''.join(next_cell.get('source', []))
                            markdown_below = convert_html_to_markdown(next_source)
                            break
                        elif next_cell['cell_type'] == 'code':
                            break
                except Exception as e:
                    print(f"Warning: Error processing following cells in {filepath}: {e}")

                processed_cells.append({
                    "file_path": str(filepath),
                    "file_name": filepath.name,
                    "folder_name": folder_name,  # Added folder name
                    "cell_number": index + 1,
                    "code": source_content,
                    "markdown_above": markdown_above,
                    "markdown_below": markdown_below
                })

                markdown_buffer = []

        except Exception as e:
            print(f"Error: Error processing cell {index} in {filepath}: {e}")
            continue

    if not processed_cells:
        print(f"Warning: No code cells found in {filepath}")
        
    return processed_cells