import pandas as pd
from typing import Dict
import snowflake.connector
from data_load.process_github_repo.snowflake_loaders.db_connection import snowflake_connection, close_connection

def create_tables(conn: snowflake.connector.SnowflakeConnection) -> None:
    """
    Create the necessary tables in Snowflake if they don't exist
    """
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS GITHUB_MARKDOWN_DOCS (
            doc_id NUMBER AUTOINCREMENT,
            file_path VARCHAR(500),
            file_name VARCHAR(255),
            folder_name VARCHAR(255),
            full_content TEXT,
            total_sections INTEGER,
            is_empty BOOLEAN,
            has_valid_structure BOOLEAN,
            library_name VARCHAR(255),
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (doc_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS GITHUB_MARKDOWN_SECTIONS (
            section_id NUMBER AUTOINCREMENT,
            doc_id NUMBER,
            header VARCHAR(500),
            content TEXT,
            header_level INTEGER,
            section_order INTEGER,
            library_name VARCHAR(255),
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (section_id),
            FOREIGN KEY (doc_id) REFERENCES GITHUB_MARKDOWN_DOCS(doc_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS GITHUB_NOTEBOOK_CELLS (
            cell_id NUMBER AUTOINCREMENT,
            file_path VARCHAR(500),
            file_name VARCHAR(255),
            folder_name VARCHAR(255),
            cell_number INTEGER,
            code TEXT,
            markdown_above TEXT,
            markdown_below TEXT,
            library_name VARCHAR(255),
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (cell_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS GITHUB_GLOBAL_STATEMENTS (
            statement_id NUMBER AUTOINCREMENT,
            statement_type VARCHAR(50),
            filepath VARCHAR(500),
            filename VARCHAR(255),
            code TEXT,
            library_name VARCHAR(255),
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (statement_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS GITHUB_CLASSES (
            class_id NUMBER AUTOINCREMENT,
            class_name VARCHAR(255),
            filepath VARCHAR(500),
            filename VARCHAR(255),
            code TEXT,
            library_name VARCHAR(255),
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (class_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS GITHUB_FUNCTIONS (
            function_id NUMBER AUTOINCREMENT,
            function_name VARCHAR(255),
            class_name VARCHAR(255),
            filepath VARCHAR(500),
            filename VARCHAR(255),
            code TEXT,
            library_name VARCHAR(255),
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (function_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS GITHUB_CONSOLIDATED_NOTEBOOKS (
            notebook_id NUMBER AUTOINCREMENT,
            file_path VARCHAR(500),
            file_name VARCHAR(255),
            folder_name VARCHAR(255),
            notebook_html TEXT,
            library_name VARCHAR(255),
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (notebook_id)
        )
        """)

        conn.commit()
    finally:
        cursor.close()

def insert_markdown_data(conn: snowflake.connector.SnowflakeConnection,
                         markdown_docs_df: pd.DataFrame,
                         batch_size: int = 1000) -> None:
    """
    Insert markdown documents and their sections into Snowflake
    """
    cursor = conn.cursor()

    try:
        markdown_sections_data = []

        for _, row in markdown_docs_df.iterrows():
            cursor.execute("""
            INSERT INTO GITHUB_MARKDOWN_DOCS (
                file_path, file_name, folder_name, full_content,
                total_sections, is_empty, has_valid_structure, library_name
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['file_path'],
                row['file_name'],
                row['folder_name'],
                row['full_content'],
                row['total_sections'],
                row['is_empty'],
                row['has_valid_structure'],
                row['library_name']
            ))

            cursor.execute("SELECT MAX(doc_id) FROM GITHUB_MARKDOWN_DOCS")
            doc_id = cursor.fetchone()[0]

            if not row['is_empty'] and 'sections' in row:
                for section_idx, section in enumerate(row['sections']):
                    markdown_sections_data.append((
                        doc_id,
                        section['header'],
                        section['content'],
                        section['header_level'],
                        section_idx + 1,
                        row['library_name']
                    ))

                    if len(markdown_sections_data) >= batch_size:
                        cursor.executemany("""
                        INSERT INTO GITHUB_MARKDOWN_SECTIONS (
                            doc_id, header, content, header_level, section_order, library_name
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """, markdown_sections_data)
                        markdown_sections_data = []

        if markdown_sections_data:
            cursor.executemany("""
            INSERT INTO GITHUB_MARKDOWN_SECTIONS (
                doc_id, header, content, header_level, section_order, library_name
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """, markdown_sections_data)

        conn.commit()
    finally:
        cursor.close()

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
                row['code'],
                row['library_name']
            ))

            if len(all_functions_data) >= batch_size:
                cursor.executemany("""
                INSERT INTO GITHUB_FUNCTIONS (function_name, class_name, filepath, filename, code, library_name)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, all_functions_data)
                all_functions_data = []

        if all_functions_data:
            cursor.executemany("""
            INSERT INTO GITHUB_FUNCTIONS (function_name, class_name, filepath, filename, code, library_name)
            VALUES (%s, %s, %s, %s, %s, %s)
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
        if 'class_methods' in structures:
            class_methods_df = structures['class_methods']
            unique_classes = class_methods_df.groupby(['class_name', 'filepath', 'filename']).first().reset_index()

            for _, row in unique_classes.iterrows():
                class_methods = class_methods_df[class_methods_df['class_name'] == row['class_name']]
                methods_code = '\n'.join(class_methods['code'])

                classes_data.append((
                    row['class_name'],
                    row['filepath'],
                    row['filename'],
                    f"class {row['class_name']}:\n{methods_code}",
                    row['library_name']
                ))

                if len(classes_data) >= batch_size:
                    cursor.executemany("""
                    INSERT INTO GITHUB_CLASSES (class_name, filepath, filename, code, library_name)
                    VALUES (%s, %s, %s, %s, %s)
                    """, classes_data)
                    classes_data = []

        if classes_data:
            cursor.executemany("""
            INSERT INTO GITHUB_CLASSES (class_name, filepath, filename, code, library_name)
            VALUES (%s, %s, %s, %s, %s)
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
                row['code'],
                row['library_name']
            ))

            if len(statements_data) >= batch_size:
                cursor.executemany("""
                INSERT INTO GITHUB_GLOBAL_STATEMENTS (statement_type, filepath, filename, code, library_name)
                VALUES (%s, %s, %s, %s, %s)
                """, statements_data)
                statements_data = []

        if statements_data:
            cursor.executemany("""
            INSERT INTO GITHUB_GLOBAL_STATEMENTS (statement_type, filepath, filename, code, library_name)
            VALUES (%s, %s, %s, %s, %s)
            """, statements_data)

        conn.commit()
    finally:
        cursor.close()

def insert_notebook_cells_data(conn: snowflake.connector.SnowflakeConnection,
                                notebook_cells_df: pd.DataFrame,
                                batch_size: int = 1000) -> None:
    """
    Insert Jupyter notebook cells data into Snowflake
    """
    cursor = conn.cursor()

    try:
        notebook_cells_data = []

        for _, row in notebook_cells_df.iterrows():
            notebook_cells_data.append((
                row['file_path'],
                row['file_name'],
                row['folder_name'],
                row['cell_number'],
                row['code'],
                row['markdown_above'],
                row['markdown_below'],
                row['library_name']
            ))

            if len(notebook_cells_data) >= batch_size:
                cursor.executemany("""
                INSERT INTO GITHUB_NOTEBOOK_CELLS (
                    file_path, file_name, folder_name, cell_number,
                    code, markdown_above, markdown_below, library_name
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, notebook_cells_data)
                notebook_cells_data = []

        if notebook_cells_data:
            cursor.executemany("""
            INSERT INTO GITHUB_NOTEBOOK_CELLS (
                file_path, file_name, folder_name, cell_number,
                code, markdown_above, markdown_below, library_name
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, notebook_cells_data)

        conn.commit()
    finally:
        cursor.close()

def insert_consolidated_notebooks_data(conn: snowflake.connector.SnowflakeConnection,
                                       consolidated_notebooks_df: pd.DataFrame,
                                       batch_size: int = 1000) -> None:
    """
    Insert consolidated notebook data into Snowflake
    """
    cursor = conn.cursor()

    try:
        notebooks_data = []

        for _, row in consolidated_notebooks_df.iterrows():
            notebooks_data.append((
                row['file_path'],
                row['file_name'],
                row['folder_name'],
                row['notebook_html'],
                row['library_name']
            ))

            if len(notebooks_data) >= batch_size:
                cursor.executemany("""
                INSERT INTO GITHUB_CONSOLIDATED_NOTEBOOKS (
                    file_path, file_name, folder_name, notebook_html, library_name
                )
                VALUES (%s, %s, %s, %s, %s)
                """, notebooks_data)
                notebooks_data = []

        if notebooks_data:
            cursor.executemany("""
            INSERT INTO GITHUB_CONSOLIDATED_NOTEBOOKS (
                file_path, file_name, folder_name, notebook_html, library_name
            )
            VALUES (%s, %s, %s, %s, %s)
            """, notebooks_data)

        conn.commit()
    finally:
        cursor.close()

def load_github_data_to_snowflake(data: Dict[str, pd.DataFrame]) -> None:
    """
    Main function to load all GitHub data into Snowflake
    """
    try:
        conn = snowflake_connection()
        if not conn:
            raise ConnectionError("Failed to establish Snowflake connection")

        create_tables(conn)

        if 'standalone_functions' in data:
            insert_functions_data(conn, data['standalone_functions'])

        if 'class_methods' in data:
            insert_functions_data(conn, data['class_methods'])
            insert_classes_data(conn, data)

        if 'global_statements' in data:
            insert_global_statements_data(conn, data['global_statements'])

        if 'notebook_cells' in data:
            insert_notebook_cells_data(conn, data['notebook_cells'])

        if 'markdown_docs' in data:
            insert_markdown_data(conn, data['markdown_docs'])

    except Exception as e:
        print(f"Error loading data to Snowflake: {str(e)}")
        raise
    finally:
        close_connection(conn)
