from config import llm
from langchain.prompts import ChatPromptTemplate
from agents.memory_store import retrieve_memory


def translate_code(
    js_code,
    dependencies_with_versions,
    package_map,
    project_summary,
    file_path,
    target_framework="FastAPI",
    is_entry=False
):
    """
    Translate a single Node.js file to Python using LangChain.
    Uses vector store memory for context and escapes curly braces safely.
    file_path is included in prompts and memory retrieval for context.
    """
    dep_list_str = "\n".join([
        f"{dep} (Node.js {ver}) -> {package_map.get(dep, 'unknown')}"
        for dep, ver in dependencies_with_versions.items()
    ])
    
    role = "root entry file" if is_entry else f"module file ({file_path})"

    # Retrieve relevant previously translated modules
    memory_context = retrieve_memory(file_path, k=3)

    # Escape curly braces to not conflict with vectorstore parsing
    safe_project_summary = project_summary.replace("{", "{{").replace("}", "}}")
    safe_memory_context = memory_context.replace("{", "{{").replace("}", "}}")

    # Build prompt with f-string template format
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
You are an expert full-stack engineer. Convert Node.js ({role}) to {target_framework} Python code.

Rules:
- Use consistent imports across all files.
- Use the latest stable APIs of Python libraries.
- Do NOT use deprecated classes or methods.
- Node.js dependencies with versions mapped to Python packages:
{dep_list_str}

Project summary:
{safe_project_summary}

Previously translated modules relevant to this file:
{safe_memory_context}
"""),
        ("user", "{js_code}")
    ], template_format="f-string")  # 🔹 f-string to safely handle {}

    # Escape curly braces in the JS code
    safe_js_code = js_code.replace("{", "{{").replace("}", "}}")

    response = llm.invoke(prompt.format_messages(js_code=safe_js_code))
    return response.content.strip()