import pandas as pd
from data_load.process_github_repo.processors.python_processor import extract_python_structures 


def process_python_files(library_name: str, **kwargs):
    """
    Process a list of Python files to extract global statements, standalone functions, and class methods.

    Args:
        library_name (str): The name of the library to add to the DataFrames
        py_files (list): List of Python file paths to process

    Returns:
        dict: Dictionary containing DataFrames for extracted structures
    """
    ti = kwargs['ti']
    
    # Pull the list of Python files from the 'list_files' task
    py_files = ti.xcom_pull(task_ids='list_files', key=None)['py_files']
    
    if not py_files:
        print("No Python files to process.")
        return {
            'global_statements': pd.DataFrame(),
            'standalone_functions': pd.DataFrame(),
            'class_methods': pd.DataFrame(),
        }

    all_global_statements = []
    all_standalone_functions = []
    all_class_methods = []

    for py_file in py_files:
        try:
            structures = extract_python_structures(py_file)
            global_statements = structures.get('global_statements', [])
            for statement in global_statements:
                statement['library_name'] = library_name 
            all_global_statements.extend(global_statements)

            standalone_functions = structures.get('standalone_functions', [])
            for function in standalone_functions:
                function['library_name'] = library_name
            all_standalone_functions.extend(standalone_functions)

            for cls in structures.get('classes', []):
                methods = cls.get('methods', [])
                for method in methods:
                    method['library_name'] = library_name
                all_class_methods.extend(methods)
        except Exception as e:
            print(f"Error processing Python file {py_file}: {e}")

    # Convert to DataFrames
    results = {
        'global_statements': pd.DataFrame(all_global_statements) if all_global_statements else pd.DataFrame(),
        'standalone_functions': pd.DataFrame(all_standalone_functions) if all_standalone_functions else pd.DataFrame(),
        'class_methods': pd.DataFrame(all_class_methods) if all_class_methods else pd.DataFrame(),
    }

    print(f'Total number of global statements: {len(results["global_statements"])}')
    print(f'Total number of standalone functions: {len(results["standalone_functions"])}')
    print(f'Total number of class methods: {len(results["class_methods"])}')


    ti.xcom_push(key='python_processing_results', value=results)

    return results
