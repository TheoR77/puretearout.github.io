#!/usr/bin/env python3
"""Builds the Pure Tearout site: every texts/*.md becomes a page in _site/."""

import html
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).parent
TEXTS = ROOT / "texts"
OUT = ROOT / "_site"
SITE_NAME = "Pure Tearout"
FORMAT = yaml.safe_load((ROOT / "format.yml").read_text(encoding="utf-8"))

PAGE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}style.css">
<style>{format_css}</style>
</head>
<body>
<header><a href="{root}index.html">{site}</a></header>
<main>
{body}
</main>
</body>
</html>
"""


def added_date(path: Path) -> datetime:
    """Date the file was first committed; falls back to its mtime if uncommitted."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%aI", "--", str(path)],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.split()
        if out:
            return datetime.fromisoformat(out[-1])
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def title_of(path: Path, source: str) -> str:
    for line in source.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").replace("_", " ").capitalize()


def format_css() -> str:
    """Turns format.yml into CSS custom properties consumed by style.css."""
    groups = {k: v for k, v in FORMAT.items() if isinstance(v, dict)}
    props = "".join(
        f"--{group}-{key.replace('_', '-')}:{value};"
        for group, values in groups.items()
        for key, value in values.items()
        if key != "text"
    )
    return f":root{{{props}}}"


def footer_html() -> str:
    text = str(FORMAT.get("footer", {}).get("text") or "").strip()
    if not text:
        return ""
    inner = markdown.markdown(text).removeprefix("<p>").removesuffix("</p>")
    return f'\n<footer class="note">{inner}</footer>'


def render(title: str, body: str, root: str) -> str:
    return PAGE.format(
        title=html.escape(title), site=SITE_NAME, body=body, root=root,
        lang=FORMAT.get("language", "en"), format_css=format_css(),
    )


def main() -> None:
    shutil.rmtree(OUT, ignore_errors=True)
    (OUT / "texts").mkdir(parents=True)
    shutil.copy(ROOT / "style.css", OUT / "style.css")

    entries = []
    for path in sorted(TEXTS.glob("*.md")):
        source = path.read_text(encoding="utf-8")
        title = title_of(path, source)
        date = added_date(path)
        body = markdown.markdown(source, extensions=["extra", "sane_lists"])
        body = f'<article>\n{body}\n</article>\n<p class="date">{date:%Y-%m-%d %H:%M}</p>' + footer_html()
        (OUT / "texts" / f"{path.stem}.html").write_text(
            render(f"{title} — {SITE_NAME}", body, "../"), encoding="utf-8"
        )
        entries.append((date, title, f"texts/{path.stem}.html"))

    entries.sort(reverse=True)
    items = "\n".join(
        f'<li><time datetime="{d.isoformat()}">{d:%Y-%m-%d %H:%M}</time>'
        f'<a href="{href}">{html.escape(t)}</a></li>'
        for d, t, href in entries
    )
    index = f'<h1>{SITE_NAME}</h1>\n<ul class="list">\n{items}\n</ul>'
    (OUT / "index.html").write_text(render(SITE_NAME, index, ""), encoding="utf-8")
    print(f"Built {len(entries)} text(s) into {OUT}")


if __name__ == "__main__":
    main()
