import base64
import html
import os
import re
import shutil
from datetime import datetime

root = "build/pages"
pdf_root = "build/pdf"

with open("assets/alchemmist-logo.svg", "rb") as file:
    logo = base64.b64encode(file.read()).decode("ascii")


def read_metadata(name: str) -> tuple[str, str]:
    readme = os.path.join(name, "README.md")
    if not os.path.exists(readme):
        return name, ""

    with open(readme, encoding="utf-8") as file:
        lines = file.readlines()

    for index, line in enumerate(lines):
        if not line.startswith("# "):
            continue

        title = line[2:].strip()
        description = ""
        for candidate in lines[index + 1 :]:
            candidate = candidate.strip()
            if candidate.startswith("#"):
                break
            if candidate:
                description = candidate
                break
        return title, description

    return name, ""


entries = []

for name in sorted(os.listdir(".")):
    if not re.fullmatch(r"\d{2}-\d{2}-\d{4}", name) or not os.path.isdir(name):
        continue

    date = datetime.strptime(name, "%d-%m-%Y")
    title, description = read_metadata(name)
    entries.append((date, name, title, description))

entries.sort(reverse=True)

items = []
for date, folder, title, description in entries:
    safe_folder = html.escape(folder, quote=True)
    safe_title = html.escape(title)
    safe_description = html.escape(description)
    description_html = f'<p class="description">{safe_description}</p>' if safe_description else ""
    items.append(
        f"""
        <article class="talk">
          <div class="talk-heading">
            <h2><a href="{safe_folder}/">{safe_title}</a></h2>
            <time datetime="{date:%Y-%m-%d}">{date:%d %B %Y}</time>
          </div>
          {description_html}
          <nav class="talk-links" aria-label="Materials for {safe_title}">
            <a href="{safe_folder}/">[Slides]</a>
            <a href="{safe_folder}.pdf">[PDF]</a>
          </nav>
        </article>
        """
    )

talks = "\n".join(items)

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="Slide decks from Anton Grishin's public talks." />
  <title>Talks · alchemmist</title>
  <style>
    @font-face {{
      font-family: "CourierCyr";
      src: url("https://cdn.jsdelivr.net/gh/alchemmist/personal-site@main/site/static/assets/fonts/couriercyrps.woff2") format("woff2");
      font-display: swap;
      font-style: normal;
      font-weight: normal;
    }}

    @font-face {{
      font-family: "CourierCyr";
      src: url("https://cdn.jsdelivr.net/gh/alchemmist/personal-site@main/site/static/assets/fonts/couriercyrps_bold.woff2") format("woff2");
      font-display: swap;
      font-style: normal;
      font-weight: bold;
    }}

    * {{
      box-sizing: border-box;
    }}

    html {{
      background: #fafafa;
      min-height: 100%;
    }}

    body {{
      background: #fff;
      color: #000;
      display: flex;
      flex-direction: column;
      font-family: "CourierCyr", "Courier New", monospace;
      line-height: 1.45;
      margin: 0;
      min-height: 100vh;
    }}

    ::selection {{
      background: rgb(0 0 0 / 10%);
    }}

    a {{
      color: #0d47a1;
      text-decoration: underline;
      text-underline-offset: 0.12em;
    }}

    a:hover {{
      color: #082d68;
    }}

    .page {{
      flex: 1;
      margin: 0 auto;
      max-width: 40rem;
      padding: 3rem 1.25rem 4rem;
      width: 100%;
    }}

    .site-header {{
      align-items: center;
      display: flex;
      justify-content: space-between;
      margin-bottom: 4rem;
    }}

    .brand {{
      align-items: center;
      color: #000;
      display: inline-flex;
      font-size: 1.55rem;
      font-weight: bold;
      gap: 0.45rem;
      text-decoration: none;
    }}

    .brand:hover {{
      color: #000;
      text-decoration: none;
    }}

    .brand-logo {{
      height: 2rem;
      width: 2rem;
    }}

    .source-link {{
      font-size: 0.9rem;
    }}

    h1 {{
      font-size: 1.65rem;
      margin: 0;
    }}

    .intro > p {{
      color: #555;
      margin: 0.45rem 0 0;
    }}

    .talk-list {{
      margin-top: 2.8rem;
    }}

    .talk {{
      border-top: 1px solid #e8e8e8;
      padding: 1.5rem 0 1.7rem;
    }}

    .talk:last-child {{
      border-bottom: 1px solid #e8e8e8;
    }}

    .talk-heading {{
      align-items: baseline;
      display: flex;
      gap: 1.5rem;
      justify-content: space-between;
    }}

    h2 {{
      font-size: 1.12rem;
      margin: 0;
    }}

    h2 a {{
      color: #000;
      text-decoration-color: rgb(0 0 0 / 35%);
      text-decoration-style: dotted;
    }}

    h2 a:hover {{
      color: #000;
      text-decoration-style: solid;
    }}

    time {{
      color: #777;
      flex: none;
      font-size: 0.82rem;
    }}

    .description {{
      color: #333;
      margin: 0.65rem 0 0;
    }}

    .talk-links {{
      display: flex;
      gap: 0.7rem;
      margin-top: 0.8rem;
    }}

    footer {{
      align-items: center;
      background: #fafafa;
      color: #777;
      display: flex;
      font-size: 0.82rem;
      justify-content: space-between;
      padding: 1.35rem max(1.25rem, calc((100vw - 40rem) / 2));
    }}

    footer nav {{
      display: flex;
      gap: 1.4rem;
    }}

    footer a {{
      color: #777;
      text-decoration: none;
    }}

    footer a:hover {{
      color: #000;
      text-decoration: underline;
    }}

    @media (max-width: 640px) {{
      .page {{
        padding-top: 1.5rem;
      }}

      .site-header {{
        margin-bottom: 2.8rem;
      }}

      .talk-heading {{
        align-items: flex-start;
        flex-direction: column;
        gap: 0.35rem;
      }}

      footer {{
        align-items: flex-start;
        flex-direction: column;
        gap: 0.7rem;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <header class="site-header">
      <a class="brand" href="https://alchemmist.xyz">
        <img class="brand-logo" src="data:image/svg+xml;base64,{logo}" alt="" />
        <span>alchemmist</span>
      </a>
      <a class="source-link" href="https://github.com/alchemmist/talks">GitHub</a>
    </header>
    <section class="intro">
      <h1>Talks</h1>
      <p>Slide decks from my public talks.</p>
    </section>
    <section class="talk-list" aria-label="Public talks">
      {talks}
    </section>
  </main>
  <footer>
    <span>© 2026 alchemmist.xyz</span>
    <nav aria-label="Footer links">
      <a href="https://alchemmist.xyz">Blog</a>
      <a href="https://github.com/alchemmist">GitHub</a>
    </nav>
  </footer>
</body>
</html>
"""

os.makedirs(root, exist_ok=True)

with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as file:
    file.write(page)

for filename in os.listdir(pdf_root):
    source = os.path.join(pdf_root, filename)
    destination = os.path.join(root, filename)
    if os.path.isfile(source):
        shutil.copyfile(source, destination)
