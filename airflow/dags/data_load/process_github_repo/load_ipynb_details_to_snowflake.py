import pandas as pd
from typing import Dict
from data_load.process_github_repo.snowflake_loaders.db_connection import snowflake_connection, close_connection
from data_load.process_github_repo.snowflake_loaders.snowflake_data_loader import create_tables, insert_notebook_cells_data, insert_consolidated_notebooks_data


def load_ipynnb_data_to_snowflake(**kwargs):
    """
    Load ipynb file processing results into Snowflake.

    Args:
        data (Dict[str, pd.DataFrame]): Dictionary containing standalone_functions,
                                        class_methods, and global_statements DataFrames.
    """
    try:

        ti = kwargs['ti']
         # Pull the processing results from XCom
        data = ti.xcom_pull(task_ids='process_ipynb_files', key='ipynb_processing_results')
    
        # Establish Snowflake connection
        conn = snowflake_connection()
        if not conn:
            raise ConnectionError("Failed to establish Snowflake connection")
        
        # Create necessary tables
        create_tables(conn)
        
        # Insert Notebook data
        if 'notebook_cells' in data and not data['notebook_cells'].empty:
            print("Inserting notebook cell details into Snowflake...")
            insert_notebook_cells_data(conn, data['notebook_cells'])
        
        if 'consolidated_notebooks' in data:
            insert_consolidated_notebooks_data(conn, data['consolidated_notebooks'])
        
        print("Data successfully loaded into Snowflake.")
    except Exception as e:
        print(f"Error loading ipynb data to Snowflake: {str(e)}")
        raise
    finally:
        close_connection(conn)
