#!/usr/bin/env python3
# builds the docs into github pages (a small site) or the github wiki, from the
# same markdown files, so they're only written once: in the repo.
#
#   build.py pages OUT          html pages in OUT, with style.css
#   build.py wiki OUT           markdown pages for the wiki repo in OUT
#
# the pages and their order are in pages.txt next to this file: "file  title" per line.
import html
import os
import re
import shutil
import sys

import markdown

HERE = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # the repo, from .github/site
REPO = os.environ.get("GITHUB_REPOSITORY", "")
BLOB = f"https://github.com/{REPO}/blob/main"


def pages():
    out = []
    for line in open(os.path.join(HERE, "pages.txt")):
        if line.strip() and not line.startswith("#"):
            path, title = line.split(None, 1)
            out.append((path, title.strip()))
    return out


def name(path, title, mode):
    if path == "README.md":
        return "index.html" if mode == "pages" else "Home"
    if mode == "wiki":
        return re.sub(r"\s+", "-", title.strip())
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") + ".html"


def relink(text, src, names, mode):
    # links between the docs go to their page; links to anything else in the repo go to github
    def fix(m):
        label, target = m.group(1), m.group(2)
        if re.match(r"[a-z]+:|#", target):
            return m.group(0)
        path, _, anchor = target.partition("#")
        full = os.path.normpath(os.path.join(os.path.dirname(src), path))
        anchor = f"#{anchor}" if anchor else ""
        if full in names:
            return f"[{label}]({names[full]}{anchor})"
        return f"[{label}]({BLOB}/{full}{anchor})"
    text = re.sub(r"\[([^\]]*)\]\(([^)\s]+)\)", fix, text)
    # images and links in html tags, like the logo
    return re.sub(r'(src|href)="(?![a-z]+:|#)([^"]+)"',
                  lambda m: f'{m.group(1)}="{BLOB}/{os.path.normpath(os.path.join(os.path.dirname(src), m.group(2)))}?raw=true"',
                  text)


def summary(text):
    """the first paragraph, as plain text, for link previews"""
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if para and not para.startswith(("#", "<", "|", "```", "-", ">", "!")):
            para = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", para)
            para = re.sub(r"[`*_]", "", " ".join(para.split()))
            return para if len(para) <= 200 else para[:para.rfind(" ", 0, 197)] + "..."
    return ""


def build(mode, out):
    os.makedirs(out, exist_ok=True)
    items = pages()
    names = {path: name(path, title, mode) for path, title in items}
    project = REPO.split("/")[-1] or os.path.basename(ROOT)
    for path, title in items:
        text = relink(open(os.path.join(ROOT, path)).read(), path, names, mode)
        if mode == "wiki":
            open(os.path.join(out, names[path] + ".md"), "w").write(text)
            continue
        body = markdown.markdown(text, extensions=["tables", "fenced_code", "toc", "sane_lists"])
        menu = "".join(f'<a href="{names[p]}"{" class=here" if p == path else ""}>{html.escape(t)}</a>'
                       for p, t in items)
        page = open(os.path.join(HERE, "page.html")).read()
        owner, _, project_name = REPO.partition("/")
        site = f"https://{owner}.github.io/{project_name}/"
        page = (page.replace("{{description}}", html.escape(summary(text), quote=True)).replace("{{site}}", site)
                    .replace("{{url}}", site + ("" if names[path] == "index.html" else names[path])))
        page = (page.replace("{{title}}", html.escape(title if path != "README.md" else project))
                    .replace("{{project}}", html.escape(project)).replace("{{menu}}", menu)
                    .replace("{{repo}}", f"https://github.com/{REPO}").replace("{{body}}", body))
        open(os.path.join(out, names[path]), "w").write(page)
    if mode == "pages":
        shutil.copy(os.path.join(HERE, "style.css"), out)
        shutil.copy(os.path.join(HERE, "preview.jpg"), out)
    else:
        side = "\n".join(f"- [{t}]({names[p]})" for p, t in items)
        open(os.path.join(out, "_Sidebar.md"), "w").write(f"**{project}**\n\n{side}\n")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
