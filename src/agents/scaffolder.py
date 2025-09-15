import os

def create_scaffold(dst_dir):
    folders = ["routes", "controllers", "models", "config", "templates", "static"]
    os.makedirs(dst_dir, exist_ok=True)
    for f in folders:
        os.makedirs(os.path.join(dst_dir, f), exist_ok=True)
