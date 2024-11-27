import pandas as pd
from pathlib import Path
from processors.python_processor import extract_python_structures
from processors.notebook_processor import extract_notebook_cells
from processors.markdown_processor import extract_markdown_content
from typing import Dict, Optional, Union

def extract_structures_from_repo(code_root: Union[str, Path]) -> Optional[Dict[str, pd.DataFrame]]:
    """
    Extract all Python structures, Jupyter notebook cells, and markdown content from the repository.
    
    Args:
        code_root (str or Path): Root directory of the repository
    
    Returns:
        dict: Dictionary of DataFrames with extracted code structures, notebook cells, and markdown content
    """
    code_root = Path(code_root)
    
    # Find all Python, Jupyter notebook, and markdown files
    py_files = list(code_root.glob('**/*.py'))
    ipynb_files = list(code_root.glob('**/*.ipynb'))
    md_files = list(code_root.glob('**/*.md'))
    
    print(f'Total number of .py files: {len(py_files)}')
    print(f'Total number of .ipynb files: {len(ipynb_files)}')
    print(f'Total number of .md files: {len(md_files)}')
    
    if len(py_files) == 0 and len(ipynb_files) == 0 and len(md_files) == 0:
        print('Verify repo exists and code_root is set correctly.')
        return None
    
    # Process Python files
    all_global_statements = []
    all_standalone_functions = []
    all_class_methods = []
    
    for py_file in py_files:
        try:
            structures = extract_python_structures(str(py_file))
            all_global_statements.extend(structures.get('global_statements', []))
            all_standalone_functions.extend(structures.get('standalone_functions', []))
            
            for cls in structures.get('classes', []):
                all_class_methods.extend(cls.get('methods', []))
        except Exception as e:
            print(f"Error processing Python file {py_file}: {e}")
    
    # Process Jupyter notebooks
    all_notebook_cells = []
    
    for notebook_file in ipynb_files:
        try:
            notebook_cells = extract_notebook_cells(notebook_file)
            all_notebook_cells.extend(notebook_cells)
        except Exception as e:
            print(f"Error processing notebook {notebook_file}: {e}")
    
    # Process markdown files
    all_markdown_docs = []
    
    for md_file in md_files:
        try:
            markdown_content = extract_markdown_content(md_file)
            all_markdown_docs.extend(markdown_content)
        except Exception as e:
            print(f"Error processing markdown file {md_file}: {e}")
    
    # Convert to DataFrames
    results = {
        'global_statements': pd.DataFrame(all_global_statements) if all_global_statements else pd.DataFrame(),
        'standalone_functions': pd.DataFrame(all_standalone_functions) if all_standalone_functions else pd.DataFrame(),
        'class_methods': pd.DataFrame(all_class_methods) if all_class_methods else pd.DataFrame(),
        'notebook_cells': pd.DataFrame(all_notebook_cells) if all_notebook_cells else pd.DataFrame(),
        'markdown_docs': pd.DataFrame(all_markdown_docs) if all_markdown_docs else pd.DataFrame()
    }
    
    # Print summaries
    print(f'Total number of global statements: {len(results["global_statements"])}')
    print(f'Total number of standalone functions: {len(results["standalone_functions"])}')
    print(f'Total number of class methods: {len(results["class_methods"])}')
    print(f'Total number of notebook cells: {len(results["notebook_cells"])}')
    print(f'Total number of markdown documents: {len(results["markdown_docs"])}')
    
    return results