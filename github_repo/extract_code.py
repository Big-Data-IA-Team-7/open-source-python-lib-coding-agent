import ast
import pandas as pd
from pathlib import Path

def extract_python_structures(filepath):
    """
    Extract classes, functions, and global statements from a Python file with detailed context.
    
    Args:
        filepath (str or Path): Path to the Python file
    
    Returns:
        dict: A dictionary containing extracted code structures
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            source_code = file.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return {}
    
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        print(f"Syntax error in file {filepath}: {e}")
        return {}
    
    # Convert filepath to Path object for consistent handling
    filepath_obj = Path(filepath)
    filename = filepath_obj.name
    
    # Extract global statements
    global_statements = []
    for node in tree.body:
        try:
            # Capture import statements, global variable declarations, etc.
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign)):
                statement_code = ast.unparse(node)
                global_statements.append({
                    'code': statement_code,
                    'type': type(node).__name__,
                    'filepath': str(filepath),
                    'filename': filename
                })
        except Exception as e:
            print(f"Error extracting global statement in {filepath}: {e}")
    
    # Find standalone functions
    standalone_functions = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            try:
                func_code = ast.unparse(node)
                standalone_functions.append({
                    'code': func_code,
                    'function_name': node.name,
                    'filepath': str(filepath),
                    'filename': filename,
                    'class_name': None
                })
            except Exception as e:
                print(f"Error extracting standalone function in {filepath}: {e}")
    
    # Class extraction logic
    class ClassVisitor(ast.NodeVisitor):
        def __init__(self):
            self.classes = []
        
        def visit_ClassDef(self, node):
            # Extract class-level information
            class_name = node.name
            
            # Find methods within the class
            class_methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    try:
                        # Extract method code using ast.unparse
                        method_code = ast.unparse(item)
                        
                        class_methods.append({
                            'code': method_code,
                            'function_name': item.name,
                            'filepath': str(filepath),
                            'filename': filename,
                            'class_name': class_name
                        })
                    except Exception as e:
                        print(f"Error extracting method in {filepath}: {e}")
            
            # Extract class code
            try:
                class_code = ast.unparse(node)
                
                self.classes.append({
                    'code': class_code,
                    'class_name': class_name,
                    'filepath': str(filepath),
                    'filename': filename,
                    'methods': class_methods
                })
            except Exception as e:
                print(f"Error extracting class in {filepath}: {e}")
            
            # Continue traversing
            self.generic_visit(node)
    
    # Visit and extract classes
    class_visitor = ClassVisitor()
    class_visitor.visit(tree)
    
    # Prepare final extraction dictionary
    extracted_structures = {
        'global_statements': global_statements,
        'standalone_functions': standalone_functions,
        'classes': [cls for cls in class_visitor.classes]
    }
    
    return extracted_structures

def extract_structures_from_repo(code_root):
    """
    Extract all Python classes, functions, and global statements from the repository.
    
    Args:
        code_root (str or Path): Root directory of the repository
    
    Returns:
        dict: Dictionary of DataFrames with extracted code structures
    """
    code_root = Path(code_root)
    code_files = list(code_root.glob('**/*.py'))
    num_files = len(code_files)
    print(f'Total number of .py files: {num_files}')
    
    if num_files == 0:
        print('Verify repo exists and code_root is set correctly.')
        return None
    
    # Extract structures from all Python files
    all_global_statements = []
    all_standalone_functions = []
    all_class_methods = []
    
    for code_file in code_files:
        try:
            structures = extract_python_structures(str(code_file))
            
            # Extend respective lists
            all_global_statements.extend(structures.get('global_statements', []))
            all_standalone_functions.extend(structures.get('standalone_functions', []))
            
            # Extract and extend class methods
            for cls in structures.get('classes', []):
                all_class_methods.extend(cls.get('methods', []))
        except Exception as e:
            print(f"Error processing file {code_file}: {e}")
    
    # Convert to DataFrames
    global_statements_df = pd.DataFrame(all_global_statements)
    standalone_functions_df = pd.DataFrame(all_standalone_functions)
    class_methods_df = pd.DataFrame(all_class_methods)
    
    # Print summaries
    print(f'Total number of global statements: {len(global_statements_df)}')
    print(f'Total number of standalone functions: {len(standalone_functions_df)}')
    print(f'Total number of class methods: {len(class_methods_df)}')
    
    return {
        'global_statements': global_statements_df,
        'standalone_functions': standalone_functions_df,
        'class_methods': class_methods_df
    }