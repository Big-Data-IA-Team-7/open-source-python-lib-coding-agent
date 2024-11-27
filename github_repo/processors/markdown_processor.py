from pathlib import Path
from typing import Dict, Any, List
import os

def extract_markdown_content(filepath: Path) -> List[Dict[str, Any]]:
    """
    Process a single .md file, extracting its content and metadata.
    
    Args:
        filepath (Path): Path to the markdown file
        
    Returns:
        List[Dict[str, Any]]: List containing processed markdown information
        
    Raises:
        FileNotFoundError: If the markdown file doesn't exist
        UnicodeDecodeError: If the file encoding is not supported
        ValueError: If the file is empty or too large
    """
    if not filepath.exists():
        error_msg = f"Markdown file not found: {filepath}"
        print(f"Error: {error_msg}")
        raise FileNotFoundError(error_msg)

    # Check file size (100MB limit)
    file_size = os.path.getsize(filepath)
    if file_size > 100 * 1024 * 1024:  # 100MB
        error_msg = f"Markdown file too large: {filepath} ({file_size / (1024*1024):.2f} MB)"
        print(f"Error: {error_msg}")
        raise ValueError(error_msg)

    try:
        # Get the folder name
        folder_name = filepath.parent.name if filepath.parent != Path() else "root"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for empty file
        if not content.strip():
            return [{
                "file_path": str(filepath),
                "file_name": filepath.name,
                "folder_name": folder_name,
                "full_content": "",
                "sections": [],
                "total_sections": 0,
                "is_empty": True
            }]
            
        # Split content into sections based on headers
        sections = []
        current_section = []
        current_header = "Introduction"
        header_stack = []
        
        for line in content.split('\n'):
            if line.strip().startswith('#'):
                # If we have content in current section, save it
                if current_section:
                    sections.append({
                        "header": current_header,
                        "content": '\n'.join(current_section).strip(),
                        "header_level": len(header_stack[-1]) if header_stack else 1
                    })
                
                # Start new section
                header_level = len(line.split()[0])
                current_header = line.strip('# ').strip() or "Untitled Section"
                header_stack.append('#' * header_level)
                current_section = []
            else:
                current_section.append(line)
        
        # Add the last section
        if current_section:
            sections.append({
                "header": current_header,
                "content": '\n'.join(current_section).strip(),
                "header_level": len(header_stack[-1]) if header_stack else 1
            })
        
        # Handle case where no sections were found
        if not sections:
            sections = [{
                "header": "Main Content",
                "content": content.strip(),
                "header_level": 1
            }]

        # Create the markdown document entry
        markdown_doc = {
            "file_path": str(filepath),
            "file_name": filepath.name,
            "folder_name": folder_name,
            "full_content": content,
            "sections": sections,
            "total_sections": len(sections),
            "is_empty": False,
            "has_valid_structure": True  # Since we're not checking for code cells
        }
        
        return [markdown_doc]
        
    except UnicodeDecodeError as e:
        print(f"Error: Encoding error in {filepath}: {e}")
        raise
    except MemoryError as e:
        print(f"Error: Insufficient memory to process {filepath}: {e}")
        raise
    except Exception as e:
        print(f"Error: Error processing markdown file {filepath}: {e}")
        raise