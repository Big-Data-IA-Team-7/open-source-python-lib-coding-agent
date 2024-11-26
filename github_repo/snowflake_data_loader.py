import pandas as pd
from typing import Dict
import snowflake.connector
from db_connection import snowflake_connection, close_connection

def insert_functions_data(conn: snowflake.connector.SnowflakeConnection, 
                         functions_df: pd.DataFrame,
                         batch_size: int = 1000) -> None:
    """
    Insert functions data into Snowflake
    """
    cursor = conn.cursor()
    
    try:
        all_functions_data = []
        
        for _, row in functions_df.iterrows():
            all_functions_data.append((
                row['function_name'],
                row['class_name'] if 'class_name' in row else None,
                row['filepath'],
                row['filename'],
                row['code']
            ))
            
            if len(all_functions_data) >= batch_size:
                cursor.executemany("""
                INSERT INTO GITHUB_FUNCTIONS (function_name, class_name, filepath, filename, code)
                VALUES (%s, %s, %s, %s, %s)
                """, all_functions_data)
                all_functions_data = []
        
        if all_functions_data:
            cursor.executemany("""
            INSERT INTO GITHUB_FUNCTIONS (function_name, class_name, filepath, filename, code)
            VALUES (%s, %s, %s, %s, %s)
            """, all_functions_data)
        
        conn.commit()
    finally:
        cursor.close()

def insert_classes_data(conn: snowflake.connector.SnowflakeConnection,
                       structures: Dict[str, pd.DataFrame],
                       batch_size: int = 1000) -> None:
    """
    Insert classes data into Snowflake
    """
    cursor = conn.cursor()
    
    try:
        classes_data = []
        # Get unique classes from class_methods DataFrame
        if 'class_methods' in structures:
            class_methods_df = structures['class_methods']
            unique_classes = class_methods_df.groupby(['class_name', 'filepath', 'filename']).first().reset_index()
            
            for _, row in unique_classes.iterrows():
                # Get all methods for this class
                class_methods = class_methods_df[class_methods_df['class_name'] == row['class_name']]
                # Combine all method codes to reconstruct class code
                methods_code = '\n'.join(class_methods['code'])
                
                classes_data.append((
                    row['class_name'],
                    row['filepath'],
                    row['filename'],
                    f"class {row['class_name']}:\n{methods_code}"  # Reconstructing class code
                ))
                
                if len(classes_data) >= batch_size:
                    cursor.executemany("""
                    INSERT INTO GITHUB_CLASSES (class_name, filepath, filename, code)
                    VALUES (%s, %s, %s, %s)
                    """, classes_data)
                    classes_data = []
        
        if classes_data:
            cursor.executemany("""
            INSERT INTO GITHUB_CLASSES (class_name, filepath, filename, code)
            VALUES (%s, %s, %s, %s)
            """, classes_data)
        
        conn.commit()
    finally:
        cursor.close()

def insert_global_statements_data(conn: snowflake.connector.SnowflakeConnection,
                                statements_df: pd.DataFrame,
                                batch_size: int = 1000) -> None:
    """
    Insert global statements data into Snowflake
    """
    cursor = conn.cursor()
    
    try:
        statements_data = []
        for _, row in statements_df.iterrows():
            statements_data.append((
                row['type'],
                row['filepath'],
                row['filename'],
                row['code']
            ))
            
            if len(statements_data) >= batch_size:
                cursor.executemany("""
                INSERT INTO GITHUB_GLOBAL_STATEMENTS (statement_type, filepath, filename, code)
                VALUES (%s, %s, %s, %s)
                """, statements_data)
                statements_data = []
        
        if statements_data:
            cursor.executemany("""
            INSERT INTO GITHUB_GLOBAL_STATEMENTS (statement_type, filepath, filename, code)
            VALUES (%s, %s, %s, %s)
            """, statements_data)
        
        conn.commit()
    finally:
        cursor.close()

def load_github_data_to_snowflake(data: Dict[str, pd.DataFrame]) -> None:
    """
    Main function to load all GitHub data into Snowflake
    """
    try:
        # Establish connection
        conn = snowflake_connection()
        if not conn:
            raise ConnectionError("Failed to establish Snowflake connection")
        
        # Create tables
        # create_tables(conn)
        
        # Insert data
        if 'standalone_functions' in data:
            insert_functions_data(conn, data['standalone_functions'])
        
        if 'class_methods' in data:
            insert_functions_data(conn, data['class_methods'])
            # Pass the entire data dictionary to insert_classes_data
            insert_classes_data(conn, data)
            
        if 'global_statements' in data:
            insert_global_statements_data(conn, data['global_statements'])
            
    except Exception as e:
        print(f"Error loading data to Snowflake: {str(e)}")
        raise
    finally:
        close_connection(conn)