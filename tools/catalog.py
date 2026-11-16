#!/usr/bin/env python3
"""The catalog's upkeep (GitHub runs these; they work by hand too).

  tools/catalog.py validate      every entry has what it needs, and docs/catalog.md matches
  tools/catalog.py doc           write docs/catalog.md from the catalog
  tools/catalog.py sources       every entry's download is still there (a report, in Markdown)
  tools/catalog.py candidates    projects that look like ports and aren't in the catalog (a
                                 report, in Markdown): to look at, not to install
"""
import importlib.machinery
import importlib.util
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CATALOG = os.path.join(ROOT, "catalog.json")
DOC = os.path.join(ROOT, "docs/catalog.md")
FIELDS = ("id", "name", "plays", "system", "kind", "source", "needs", "page")
KINDS = ("decomp", "recomp", "source port", "reimplementation", "fan game")

# the program itself, for its download rules
_loader = importlib.machinery.SourceFileLoader("ports", os.path.join(ROOT, "nekozame-ports"))
ports = importlib.util.module_from_spec(importlib.util.spec_from_loader("ports", _loader))
_loader.exec_module(ports)

# where new ones are looked for
GITHUB_SEARCHES = ["topic:n64recomp", "topic:recompilation", "topic:static-recompilation",
                   "topic:decompilation topic:pc-port", "topic:pc-port", "recomp in:name", "decomp port in:description",
                   "topic:source-port"]
FLATHUB_SEARCHES = ["source port", "recompiled", "decompilation", "port of", "reimplementation", "engine recreation"]
LOOKS_LIKE_PORT = re.compile(r"(?i)\b(port|recomp\w*|decomp\w*|reimplement\w*|source port|native pc|native linux|recreation)\b")
NOT_GAMES = re.compile(r"(?i)\b(list|awesome|catalog|tools?|toolkit|library|launcher|hub|decompiler|template|framework|sdk|editor|map editor)\b")
MIN_STARS = 25


def load():
    return json.load(open(CATALOG))["ports"]


def doc(entries):
    rows = ["# Catalog", "",
            "Every port nekozame-ports installs. Each one was looked at before it was added.", "",
            "- **From:** Flathub ports are sandboxed. GitHub ports come from the project's own releases and run unsandboxed.",
            "- **Needs:** what you need to play it. Most ports need your own copy of the game.", "",
            "| Port | Plays | Kind | From | Needs |", "|---|---|---|---|---|"]
    for p in sorted(entries, key=lambda p: (p["system"] == "PC", p["system"], p["name"].lower())):
        frm = "Flathub" if p["source"].startswith("flathub:") else "GitHub"
        plays = p["plays"] + (f" ({p['system']})" if p["system"] != "PC" else "")
        rows.append(f"| [{p['name']}]({p['page']}) | {plays} | {p['kind']} | {frm} | {p['needs']} |")
    rows += ["", "This page is written from [`catalog.json`](../catalog.json) by `tools/catalog.py doc`.", ""]
    return "\n".join(rows)


def validate(entries):
    problems = []
    ids = set()
    for p in entries:
        missing = [f for f in FIELDS if not p.get(f)]
        if missing:
            problems.append(f"{p.get('id', '?')}: missing {', '.join(missing)}")
        if p.get("id") in ids:
            problems.append(f"{p['id']}: the id is used twice")
        ids.add(p.get("id"))
        if not re.match(r"^(github:[\w.-]+/[\w.-]+|flathub:[\w.-]+)$", p.get("source", "")):
            problems.append(f"{p.get('id')}: source should be github:OWNER/REPO or flathub:APP.ID")
        if p.get("kind") not in KINDS:
            problems.append(f"{p.get('id')}: kind should be one of {', '.join(KINDS)}")
    if not os.path.exists(DOC) or open(DOC).read() != doc(entries):
        problems.append("docs/catalog.md doesn't match the catalog: run tools/catalog.py doc")
    return problems


def flathub_app(app):
    try:
        return ports.get(f"https://flathub.org/api/v2/appstream/{app}")
    except (OSError, ValueError):
        return None


def flathub_search(q):
    req = urllib.request.Request("https://flathub.org/api/v2/search", data=json.dumps({"query": q}).encode(),
                                 headers={**ports.UA, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("hits", [])


def sources(entries):
    """each entry's download, today: a Markdown report, and whether anything is broken"""
    lines, broken = [], []
    for p in entries:
        frm, ref = p["source"].split(":", 1)
        if frm == "flathub":
            ok = flathub_app(ref) is not None
            lines.append(f"| {p['name']} | Flathub `{ref}` | {'✓' if ok else '✗ not on Flathub'} |")
        else:
            try:
                tag, asset = ports.github_release(ref, p.get("asset"))
                ok = asset is not None
                lines.append(f"| {p['name']} | GitHub `{ref}` {tag} | {'✓ ' + asset['name'] if ok else '✗ no GNU/Linux build'} |")
            except (OSError, ports.Wait) as err:
                ok = False
                lines.append(f"| {p['name']} | GitHub `{ref}` | ✗ {err} |")
        if not ok:
            broken.append(p["name"])
    report = ["| Port | Source | Today |", "|---|---|---|"] + lines
    return "\n".join(report), broken


def candidates(entries):
    have = {p["source"] for p in entries}
    found = []
    for q in FLATHUB_SEARCHES:
        try:
            hits = flathub_search(q)
        except OSError:
            continue
        for h in hits:
            key = "flathub:" + h["app_id"]
            text = f"{h.get('name', '')} {h.get('summary', '')}"
            if key in have or any(f["key"] == key for f in found) or not LOOKS_LIKE_PORT.search(text) \
                    or NOT_GAMES.search(text) or "game" not in str(h.get("main_categories", "")).lower():
                continue
            found.append({"key": key, "name": h.get("name", h["app_id"]), "about": h.get("summary", ""),
                          "page": f"https://flathub.org/apps/{h['app_id']}", "linux": "Flathub"})
    for q in GITHUB_SEARCHES:
        try:
            items = ports.get("https://api.github.com/search/repositories?" + urllib.parse.urlencode(
                {"q": f"{q} stars:>={MIN_STARS} fork:false archived:false", "sort": "updated", "per_page": 30})).get("items", [])
        except OSError:
            continue
        time.sleep(2)
        for it in items:
            key = "github:" + it["full_name"]
            desc = it.get("description") or ""
            if key in have or any(f["key"] == key for f in found) or not LOOKS_LIKE_PORT.search(f"{it['name']} {desc}") \
                    or NOT_GAMES.search(f"{it['name']} {desc}"):
                continue
            try:
                tag, asset = ports.github_release(it["full_name"])
            except ports.Wait:
                break
            except OSError:
                continue
            if not asset:
                continue
            found.append({"key": key, "name": it["full_name"], "about": desc[:140], "page": it["html_url"],
                          "linux": asset["name"], "stars": it["stargazers_count"], "since": it["created_at"][:10]})
    found.sort(key=lambda f: -f.get("stars", 10 ** 6))
    rows = ["Projects that look like ports and have a GNU/Linux build, not in the catalog. Look at each one "
            "before adding it to `catalog.json`: is it a real port, does it work, does it need the game?", "",
            "| Project | About | Build | Stars, since |", "|---|---|---|---|"]
    for f in found:
        rows.append(f"| [{f['name']}]({f['page']}) | {f['about'].replace('|', '/')} | {f['linux']} | "
                    f"{('★' + str(f['stars']) + ', ' + f['since']) if f.get('stars') else 'Flathub'} |")
    return "\n".join(rows), len(found)


def main(argv):
    entries = load()
    cmd = argv[0] if argv else ""
    if cmd == "doc":
        open(DOC, "w").write(doc(entries))
        print(f"docs/catalog.md: {len(entries)} ports")
        return 0
    if cmd == "validate":
        problems = validate(entries)
        for p in problems:
            print(p)
        print(f"{len(entries)} ports, {len(problems)} problems")
        return 1 if problems else 0
    if cmd == "sources":
        report, broken = sources(entries)
        print(report)
        print(f"\nbroken: {', '.join(broken) if broken else 'none'}", file=sys.stderr)
        return 1 if broken else 0
    if cmd == "candidates":
        report, n = candidates(entries)
        print(report)
        print(f"\n{n} candidates", file=sys.stderr)
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
