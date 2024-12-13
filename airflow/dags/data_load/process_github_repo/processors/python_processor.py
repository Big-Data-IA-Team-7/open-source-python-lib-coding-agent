import ast
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