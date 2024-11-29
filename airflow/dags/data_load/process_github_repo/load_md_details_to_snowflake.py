import pandas as pd
from typing import Dict
from data_load.process_github_repo.snowflake_loaders.db_connection import snowflake_connection, close_connection
from data_load.process_github_repo.snowflake_loaders.snowflake_data_loader import create_tables, insert_markdown_data


def load_markdown_data_to_snowflake(**kwargs):
    """
    Load markdown file processing results into Snowflake.

    Args:
        data (Dict[str, pd.DataFrame]): Dictionary containing standalone_functions,
                                        class_methods, and global_statements DataFrames.
    """
    try:

        ti = kwargs['ti']
         # Pull the processing results from XCom
        data = ti.xcom_pull(task_ids='process_md_files', key='md_processing_results')
    
        # Establish Snowflake connection
        conn = snowflake_connection()
        if not conn:
            raise ConnectionError("Failed to establish Snowflake connection")
        
        # Create necessary tables
        create_tables(conn)
        
        # Insert Markdown docs
        if 'markdown_docs' in data and not data['markdown_docs'].empty:
            print("Inserting notebook cell details into Snowflake...")
            insert_markdown_data(conn, data['markdown_docs'])
        
        print("Data successfully loaded into Snowflake.")
    except Exception as e:
        print(f"Error loading Markdown data to Snowflake: {str(e)}")
        raise
    finally:
        close_connection(conn)
