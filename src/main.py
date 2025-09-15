import os, shutil
from agents.project_analyzer import get_dependencies_with_versions, list_js_files, find_entry_file, summarize_structure
from agents.translator import translate_code
from agents.scaffolder import create_scaffold
from agents.writer import write_file, generate_requirements
from agents.views_translator import process_views
from agents.validator import validate_project, fix_code_with_llm
from agents.memory_store import add_to_memory
from constants import PACKAGE_MAP
from utils import determine_python_path

SRC_DIR = "node_app"
DST_DIR = "pythonapp_translated"
TARGET_FRAMEWORK = "FastAPI"

# Step 1: Create Python project folders
create_scaffold(DST_DIR)

# Step 2: Analyze project
dependencies_with_versions = get_dependencies_with_versions(os.path.join(SRC_DIR, "package.json"))
js_files = list_js_files(SRC_DIR)
entry_file = find_entry_file(SRC_DIR)
project_summary = summarize_structure(SRC_DIR)

# Step 3: Translate entry file
if entry_file:
    with open(entry_file) as f:
        js_code = f.read()
    py_code = translate_code(js_code, dependencies_with_versions, PACKAGE_MAP, project_summary, entry_file, TARGET_FRAMEWORK, is_entry=True)
    out_path = os.path.join(DST_DIR, "main.py")
    write_file(out_path, py_code)
    add_to_memory(entry_file, py_code)

# Step 4: Translate other files
for fpath in js_files:
    if fpath == entry_file:
        continue
    with open(fpath) as f:
        js_code = f.read()
    py_code = translate_code(js_code, dependencies_with_versions, PACKAGE_MAP, project_summary, fpath, TARGET_FRAMEWORK)
    out_path = determine_python_path(fpath, SRC_DIR, DST_DIR)
    write_file(out_path, py_code)
    add_to_memory(fpath, py_code)

# Step 5: Translate EJS views → Jinja2
SRC_VIEWS_DIR = os.path.join(SRC_DIR, "views")
DST_TEMPLATES_DIR = os.path.join(DST_DIR, "templates")
if os.path.exists(SRC_VIEWS_DIR):
    process_views(SRC_VIEWS_DIR, DST_TEMPLATES_DIR)

# Step 6: Copy static files
SRC_PUBLIC_DIR = os.path.join(SRC_DIR, "public")
DST_STATIC_DIR = os.path.join(DST_DIR, "static")
if os.path.exists(SRC_PUBLIC_DIR):
    shutil.copytree(SRC_PUBLIC_DIR, DST_STATIC_DIR, dirs_exist_ok=True)

# Step 7: Generate requirements.txt
generate_requirements(dependencies_with_versions, PACKAGE_MAP, DST_DIR)

# Step 8: Validation pass
errors = validate_project(DST_DIR)
if errors:
    print("Validation errors found, fixing...")
    for root, _, files in os.walk(DST_DIR):
        for f in files:
            if f.endswith(".py"):
                fpath = os.path.join(root, f)
                with open(fpath) as src:
                    code = src.read()
                fixed_code = fix_code_with_llm(code, "\n".join(errors))
                write_file(fpath, fixed_code)
                add_to_memory(fpath, fixed_code)
