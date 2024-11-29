import pandas as pd
from pathlib import Path
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
    
    return {
        'py_files': [str(f) for f in py_files],
        'ipynb_files': [str(f) for f in ipynb_files],
        'md_files': [str(f) for f in md_files],
    } 