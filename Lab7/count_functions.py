import ast

def count_functions_in_file(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())
    
    # Count the number of function definitions in the file
    function_count = sum(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
    
    return function_count

#Replace 'your_file.py' with the path to the file you want to check
#print("Number of functions:", count_functions_in_file("/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/passwords.py"))
