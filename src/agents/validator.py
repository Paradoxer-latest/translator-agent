import ast, os
from config import llm
from langchain.prompts import ChatPromptTemplate

def validate_python_file(file_path):
    errors = []
    try:
        with open(file_path) as f:
            code = f.read()
        ast.parse(code)
    except SyntaxError as e:
        errors.append(f"Syntax error in {file_path}: {e}")
    return errors

def validate_project(dst_dir):
    errors = []
    for root, _, files in os.walk(dst_dir):
        for f in files:
            if f.endswith(".py"):
                fpath = os.path.join(root, f)
                errors.extend(validate_python_file(fpath))
    return errors

def fix_code_with_llm(py_code, error_report):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Python developer. Fix the code."),
        ("user", f"Here is the code:\n{py_code}\n\nErrors found:\n{error_report}")
    ])
    response = llm.invoke(prompt.format_messages())
    return response.content.strip()
