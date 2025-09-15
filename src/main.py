import os
import json
from pathlib import Path
from dotenv import load_dotenv
from agents.translator import translate_project
from constants import PACKAGE_MAP

load_dotenv()
SRC_DIR = Path("node_app")
DST_DIR = Path("pythonapp_translated")


def collect_js_files(SRC_DIR: Path):
    js_files = []
    for path in SRC_DIR.rglob("*.js"):
        js_files.append(path)
    return js_files

def build_structure_map(js_files):
    structure_map = {}
    for f in js_files:
        rel = f.relative_to(SRC_DIR).as_posix()
        py_path = rel.replace(".js", ".py")
        module_path = py_path.replace("/", ".").rstrip(".py")
        structure_map[rel] = module_path
    return structure_map

def main():
    js_files = collect_js_files(SRC_DIR)
    structure_map = build_structure_map(js_files)

    all_js_code = ""
    for f in js_files:
        with open(f, "r") as infile:
            rel_path = f.relative_to(SRC_DIR).as_posix()
            all_js_code += f"# FILE: {rel_path}\n" + infile.read() + "\n\n"

    package_json = json.loads(open(SRC_DIR / "package.json").read())
    dependencies_with_versions = package_json.get("dependencies", {})

    python_files = translate_project(
        all_js_code,
        dependencies_with_versions,
        PACKAGE_MAP,
        structure_map,
        target_framework="FastAPI"
    )

    for path, code in python_files.items():
        target_path = DST_DIR / path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w") as outfile:
            outfile.write(code)

    print(f"Project translated successfully into {DST_DIR}")

if __name__ == "__main__":
    main()
