import os, re

def convert_ejs_to_jinja2(content):
    content = re.sub(r"<%=\s*(.*?)\s*%>", r"{{ \1 }}", content)
    content = re.sub(r"<%\s*if\s*\((.*?)\)\s*{?\s*%>", r"{% if \1 %}", content)
    content = re.sub(r"<%\s*}?\s*else\s*{?\s*%>", r"{% else %}", content)
    content = re.sub(r"<%\s*for\s*\((.*?)\)\s*{?\s*%>", r"{% for \1 %}", content)
    content = re.sub(r"<%\s*end\s*%>", r"{% endfor %}", content)
    content = re.sub(r"<%\s*}%>", r"{% endif %}", content)
    return content

def process_views(src_dir, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)
    for root, _, files in os.walk(src_dir):
        for f in files:
            if f.endswith(".ejs"):
                with open(os.path.join(root, f)) as src:
                    content = src.read()
                converted = convert_ejs_to_jinja2(content)
                new_name = f.replace(".ejs", ".html")
                with open(os.path.join(dst_dir, new_name), "w") as out:
                    out.write(converted)
