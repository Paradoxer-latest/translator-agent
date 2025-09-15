import os, json, glob

def get_dependencies_with_versions(package_json_path):
    with open(package_json_path) as f:
        pkg = json.load(f)
    return pkg.get("dependencies", {})

def list_js_files(src_dir):
    return glob.glob(f"{src_dir}/**/*.js", recursive=True)

def find_entry_file(src_dir):
    candidates = ["app.js", "server.js", "index.js"]
    for f in candidates:
        path = os.path.join(src_dir, f)
        if os.path.exists(path):
            return path
    return None

def summarize_structure(src_dir):
    folders = [d for d in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, d))]
    summary = "Project structure:\n"
    for f in folders:
        summary += f"- {f}/\n"
    summary += """
    Imports should follow this pattern:
    - from models.user import User
    - from controllers.auth import login
    - from routes.auth import router as auth_router
    - templates/ for Jinja2 views
    - static/ for public assets
    """
    return summary
