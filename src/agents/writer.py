import os

def write_file(path, code):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(code)

def generate_requirements(dependencies, package_map, dst_dir):
    mapped = [package_map.get(dep, f"# unknown: {dep}") for dep in dependencies.keys()]
    reqs = "\n".join(sorted(set(mapped)))
    with open(os.path.join(dst_dir, "requirements.txt"), "w") as f:
        f.write(reqs)
