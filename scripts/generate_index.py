import os
import re
from datetime import datetime

root = "build/pages"
pdf_root = "build/pdf"

entries = []

for name in sorted(os.listdir(".")):
    if re.match(r"\d{2}-\d{2}-\d{4}", name) and os.path.isdir(name):
        readme = os.path.join(name, "README.md")
        title = name
        desc = ""
        if os.path.exists(readme):
            with open(readme, encoding="utf-8") as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith("# "):
                    title = line[2:].strip()
                    if i + 1 < len(lines):
                        desc = lines[i + 1].strip()
                    break
        date_obj = datetime.strptime(name, "%d-%m-%Y")
        entries.append((date_obj, name, title, desc))

entries.sort(reverse=True)

html_items = ""
for _, folder, title, desc in entries:
    html_items += f"""
    <div class="talk">
      <h2>{title}</h2>
      <p class="date">{folder}</p>
      <p>{desc}</p>
      <div class="links">
        <a href="{folder}/">Slides</a>
        <a href="{folder}.pdf">PDF</a>
      </div>
    </div>
    """

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Talks</title>
<style>
body{{font-family:monospace, system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:900px;margin:40px auto;padding:0 20px;background:#0f1115;color:#e6e6e6}}
h1{{font-size:2.2rem;margin-bottom:2rem}}
.talk{{margin-bottom:2.5rem;padding-bottom:1.5rem;border-bottom:1px solid #2a2d34}}
.date{{opacity:.6;font-size:.9rem}}
.links a{{margin-right:15px;text-decoration:none;color:#6ab0ff}}
.links a:hover{{text-decoration:underline}}
</style>
</head>
<body>
<h1>Public Talks</h1>
{html_items}
</body>
</html>"""

os.makedirs(root, exist_ok=True)

with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

for file in os.listdir(pdf_root):
    src = os.path.join(pdf_root, file)
    dst = os.path.join(root, file)
    if os.path.isfile(src):
        with open(src, "rb") as s, open(dst, "wb") as d:
            d.write(s.read())
