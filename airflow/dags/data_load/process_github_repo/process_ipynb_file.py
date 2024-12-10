import pandas as pd
from data_load.process_github_repo.processors.notebook_processor import extract_notebook_cells, extract_consolidated_notebook
def process_ipynb_files(**kwargs):
    """
    Process a list of Python files to extract global statements, standalone functions, and class methods.

    Args:
        py_files (list): List of Python file paths to process

    Returns:
        dict: Dictionary containing DataFrames for extracted structures
    """
    ti = kwargs['ti']
    
    # Pull the list of Python files from the 'list_files' task
    ipynb_files = ti.xcom_pull(task_ids='list_files', key=None)['ipynb_files']
    
    if not ipynb_files:
        print("No ipynb files to process.")
        return {
            'notebook_cells': pd.DataFrame()
        }

    # Process Jupyter notebooks (both cell-wise and consolidated)
    all_notebook_cells = []
    all_consolidated_notebooks = []

    for notebook_file in ipynb_files:
        try:
             # Get individual cells
            notebook_cells = extract_notebook_cells(notebook_file)
            all_notebook_cells.extend(notebook_cells)


            # Get consolidated notebook
            consolidated_notebook = extract_consolidated_notebook(notebook_file)
            all_consolidated_notebooks.extend(consolidated_notebook)
        except Exception as e:
            print(f"Error processing notebook {notebook_file}: {e}")

    # Convert to DataFrames
    results_ipynb = {
       'notebook_cells': pd.DataFrame(all_notebook_cells) if all_notebook_cells else pd.DataFrame(),
       'consolidated_notebooks': pd.DataFrame(all_consolidated_notebooks) if all_consolidated_notebooks else pd.DataFrame()
    }

    # Print summaries
    print(f'Total number of notebook cells: {len(results_ipynb["notebook_cells"])}')
    print(f'Total number of consolidated notebooks: {len(results["consolidated_notebooks"])}')


    # Push the results to XCom
    ti.xcom_push(key='ipynb_processing_results', value=results_ipynb)

    return results_ipynb
