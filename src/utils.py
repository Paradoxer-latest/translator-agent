import os

FOLDER_MAP = {
    "controllers": "controllers",
    "routes": "routes",
    "models": "models",
    "config": "config",
    "views": "templates",
    "public": "static"
}

def determine_python_path(js_file_path, src_dir, dst_dir):
    relative_path = os.path.relpath(js_file_path, src_dir)
    parts = relative_path.split(os.sep)
    top_folder = parts[0]

    if top_folder in FOLDER_MAP:
        python_folder = FOLDER_MAP[top_folder]
        mapped_parts = [python_folder] + parts[1:]
    else:
        mapped_parts = parts

    mapped_parts[-1] = mapped_parts[-1].replace(".js", ".py")
    return os.path.join(dst_dir, *mapped_parts)
