import pandas as pd
from data_load.process_github_repo.processors.markdown_processor import extract_markdown_content

def process_md_files(**kwargs):
    """
    Process a list of md files to extract markdown content
    Args:
        md_files (list): List of Python file paths to process

    Returns:
        dict: Dictionary containing DataFrames for extracted structures
    """
    ti = kwargs['ti']
    
    # Pull the list of Python files from the 'list_files' task
    md_files = ti.xcom_pull(task_ids='list_files', key=None)['md_files']
    
    if not md_files:
        print("No markdown files to process.")
        return {
            'markdown_docs': pd.DataFrame()
        }

    all_markdown_cells = []

    for md_file in md_files:
        try:
            markdown_cells = extract_markdown_content(md_file)
            all_markdown_cells.extend(markdown_cells)
        except Exception as e:
            print(f"Error processing notebook {md_file}: {e}")

    # Convert to DataFrames
    results_md = {
       'markdown_docs': pd.DataFrame(all_markdown_cells) if all_markdown_cells else pd.DataFrame()
    }

    # Print summaries
    print(f'Total number of markdown documents: {len(results_md["markdown_docs"])}')


    # Push the results to XCom
    ti.xcom_push(key='md_processing_results', value=results_md)

    return results_md
