import pandas as pd
from typing import Dict
from data_load.process_github_repo.snowflake_loaders.db_connection import snowflake_connection, close_connection
from data_load.process_github_repo.snowflake_loaders.snowflake_data_loader import create_tables, insert_functions_data,insert_classes_data,insert_global_statements_data


def load_python_data_to_snowflake(**kwargs):
    """
    Load Python file processing results into Snowflake.

    Args:
        data (Dict[str, pd.DataFrame]): Dictionary containing standalone_functions,
                                        class_methods, and global_statements DataFrames.
    """
    try:

        ti = kwargs['ti']
         # Pull the processing results from XCom
        data = ti.xcom_pull(task_ids='process_py_files', key='python_processing_results')
    
        # Establish Snowflake connection
        conn = snowflake_connection()
        if not conn:
            raise ConnectionError("Failed to establish Snowflake connection")
        
        # Create necessary tables
        create_tables(conn)
        
        # Insert standalone functions
        if 'standalone_functions' in data and not data['standalone_functions'].empty:
            print("Inserting standalone functions into Snowflake...")
            insert_functions_data(conn, data['standalone_functions'])
        
        # Insert class methods and corresponding classes
        if 'class_methods' in data and not data['class_methods'].empty:
            print("Inserting class methods into Snowflake...")
            insert_classes_data(conn, data)
        
        # Insert global statements
        if 'global_statements' in data and not data['global_statements'].empty:
            print("Inserting global statements into Snowflake...")
            insert_global_statements_data(conn, data['global_statements'])
        
        print("Data successfully loaded into Snowflake.")
    except Exception as e:
        print(f"Error loading Python data to Snowflake: {str(e)}")
        raise
    finally:
        close_connection(conn)
