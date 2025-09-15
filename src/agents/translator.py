import json
from config import llm
from langchain.prompts import ChatPromptTemplate


def translate_project(all_js_code, dependencies_with_versions, package_map, structure_map, target_framework="FastAPI"):
    """
    Translate the entire Node.js project to Python in one LLM call.
    Fully safe against curly braces in code or JSON examples.
    Returns a dict of {file_path: python_code}.
    """
    dep_list_str = "\n".join([
        f"{dep} (Node.js {ver}) -> {package_map.get(dep, 'unknown')}"
        for dep, ver in dependencies_with_versions.items()
    ])

    structure_context = "\n".join([f"{js} -> {py}" for js, py in structure_map.items()])

    # JSON example with doubled braces
    json_example = """
        {{
        "models/user.py": "...python code...",
        "controllers/auth.py": "...python code..."
        }}
    """

    # Escape braces in JS code
    safe_code = all_js_code.replace("{", "{{").replace("}", "}}")

    # Build prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
            You are an expert full-stack engineer. Convert this entire Node.js project to {target_framework} Python code.

            Rules:
            - Use the following mapping for Node.js -> Python dependencies:
            {dep_list_str}

            - Follow this project structure:
            {structure_context}

            - Generate consistent imports across all files.
            - Do NOT invent module names. Only use those in the structure map.
            - Convert EJS views into Jinja2 templates.
            - Use latest stable APIs, avoid deprecated libraries.

            Return the result as a JSON dictionary with file paths as keys and Python code as values.
            Example:
            {json_example}
            """),
        ("user", "{all_js_code}")
    ], template_format="f-string")  # 🔹 no allow_unused_kwargs

    # Invoke LLM
    response = llm.invoke(prompt.format_messages(all_js_code=safe_code))

    # Parse JSON
    try:
        files = json.loads(response.content)
    except Exception as e:
        raise ValueError(f"LLM did not return valid JSON: {e}\nContent:\n{response.content}")

    return files
