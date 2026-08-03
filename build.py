#!/usr/bin/env python3
"""Generate the jeskridge.com hub site.

GitHub Pages serves the ROOT of this repo at https://www.jeskridge.com/.
Source lives in src/ ; generated pages are written to the repo root.

    python build.py            # build
    python build.py --serve    # build, then preview at http://localhost:8000

Adding content:
  - Edit the intro of a section in  src/sections/<slug>.md  (plain Markdown).
  - Photography sections auto-build a gallery from images in  media/<slug>/ .
  - Project sections (engineering, light, music, drumming) render their Markdown
    body as-is: add a project by adding a `## Project name` heading and a
    paragraph. No code changes needed.
  - Re-run this script and commit.

Media:
  IMG_BASE points at where gallery images are served from. It is "/media" now
  (images committed to this repo). When a section's photo library outgrows that,
  set IMG_BASE to the Cloudflare R2 domain (e.g. "https://img.jeskridge.com")
  and serve the files from there instead — no other change required.
"""
import argparse
import html
import pathlib
import re
import shutil

import markdown

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src"
STATIC = SRC / "static"
SECTIONS_DIR = SRC / "sections"
MEDIA = ROOT / "media"

SITE_TITLE = "Justin Eskridge"
SITE_TAGLINE = "Engineering, photography, and things that glow and go bang."
SITE_DESC = ("The work of Justin Eskridge — electrical engineering, nature and tech "
             "photography, light installations, music, and drumming.")

# Set to an email to turn on the contact button, or leave "" (a form can be wired later).
CONTACT_EMAIL = ""

# Where gallery images are served from. Local now; a Cloudflare R2 domain later.
IMG_BASE = "/media"

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif")

# ---------------------------------------------------------------- sections

class Section:
    def __init__(self, slug, title, group, tagline, kind):
        self.slug = slug
        self.title = title
        self.group = group
        self.tagline = tagline
        self.kind = kind          # "gallery" | "projects"
        self.url = f"/{slug}/"

    @property
    def intro_file(self):
        return SECTIONS_DIR / f"{self.slug}.md"

    @property
    def media_dir(self):
        return MEDIA / self.slug


SECTIONS = [
    Section("electrical-engineering", "Electrical Engineering", "Engineering",
            "Contract design, prototypes, and things I build to find out whether they can be built.",
            "projects"),
    Section("nature-photography", "Nature Photography", "Photography",
            "The world outside, slowed down.", "gallery"),
    Section("tech-photography", "Tech Photography", "Photography",
            "Circuits, machines, and the quiet geometry of made things.", "gallery"),
    Section("light-projects", "Light Projects", "Light & Sound",
            "LED art and installations — the controllers, the code, and the glow.", "projects"),
    Section("music-projects", "Music Projects", "Light & Sound",
            "Recordings, instruments, and sound experiments.", "projects"),
    Section("drumming", "Drumming", "Light & Sound",
            "Rhythm, kit, and hands.", "projects"),
]

GROUP_ORDER = ["Engineering", "Photography", "Light & Sound", "Writing"]

# A hand-linked entry for the book, which lives in the other repo at /contact-improv-book/.
BOOK = {
    "title": "The Rolling Point of Contact",
    "group": "Writing",
    "tagline": "A facilitator's guidebook & games manual for Contact Improvisation.",
    "url": "/contact-improv-book/",
}

# ---------------------------------------------------------------- helpers

def md(text):
    return markdown.markdown(text, extensions=["extra", "sane_lists"])


def load_intro(section):
    if section.intro_file.exists():
        return section.intro_file.read_text(encoding="utf-8-sig")
    return ""


def gallery_images(section):
    if not section.media_dir.exists():
        return []
    files = sorted(p for p in section.media_dir.iterdir()
                   if p.suffix.lower() in IMAGE_EXTS)
    out = []
    for p in files:
        # Optional caption: a sidecar .txt with the same stem.
        cap = p.with_suffix(".txt")
        caption = cap.read_text(encoding="utf-8").strip() if cap.exists() else ""
        out.append((f"{IMG_BASE}/{section.slug}/{p.name}", caption))
    return out

# ---------------------------------------------------------------- template

def page(title, body, *, active="", description=SITE_DESC):
    nav = '<a href="/"%s>Home</a>' % (" class='active'" if active == "home" else "")
    for s in SECTIONS:
        cls = " class='active'" if active == s.slug else ""
        nav += f'<a href="{s.url}"{cls}>{s.title}</a>'

    full_title = title if title == SITE_TITLE else f"{title} · {SITE_TITLE}"
    contact = ""
    if CONTACT_EMAIL:
        contact = (f'<a class="contact-link" href="mailto:{html.escape(CONTACT_EMAIL)}">'
                   f'Get in touch</a>')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{html.escape(description, quote=True)}">
<meta property="og:title" content="{html.escape(full_title, quote=True)}">
<meta property="og:description" content="{html.escape(description, quote=True)}">
<meta property="og:type" content="website">
<link rel="stylesheet" href="/assets/style.css">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="bar">
    <a class="brand" href="/"><span class="mark" aria-hidden="true"></span>Justin&nbsp;Eskridge</a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
    <nav id="site-nav">{nav}
      <button class="theme-toggle" aria-label="Toggle dark mode" title="Toggle dark mode"></button>
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer" id="contact">
  <div class="foot-inner">
    <p class="foot-title">{SITE_TITLE}</p>
    <p class="foot-sub">{SITE_TAGLINE}</p>
    {contact}
    <nav class="foot-nav">
      <a href="/contact-improv-book/">The Rolling Point of Contact</a>
      <a href="https://github.com/AxisDigitalArchive">GitHub</a>
    </nav>
  </div>
</footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""


def write(relpath, content):
    path = ROOT / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path

# ---------------------------------------------------------------- pages

def build_home():
    groups = {}
    for s in SECTIONS:
        groups.setdefault(s.group, []).append(
            dict(title=s.title, tagline=s.tagline, url=s.url, slug=s.slug))
    groups.setdefault(BOOK["group"], []).append(
        dict(title=BOOK["title"], tagline=BOOK["tagline"], url=BOOK["url"], slug="book"))

    blocks = ""
    for group in GROUP_ORDER:
        items = groups.get(group)
        if not items:
            continue
        cards = ""
        for it in items:
            cards += f"""
        <a class="tile" href="{it['url']}">
          <h3>{it['title']}</h3>
          <p>{it['tagline']}</p>
          <span class="tile-go">View →</span>
        </a>"""
        blocks += f"""
    <section class="group">
      <h2 class="group-title">{group}</h2>
      <div class="tile-grid">{cards}</div>
    </section>"""

    body = f"""
<section class="hero">
  <div class="hero-inner">
    <h1>Justin <em>Eskridge</em></h1>
    <p class="lede">{SITE_DESC}</p>
  </div>
</section>
<div class="wrap">
{blocks}
</div>
"""
    write("index.html", page(SITE_TITLE, body, active="home"))


def build_section(section):
    intro_html = md(load_intro(section)) if load_intro(section) else ""

    if section.kind == "gallery":
        images = gallery_images(section)
        if images:
            tiles = "".join(
                f'<button class="shot" data-full="{src}" '
                f'aria-label="{html.escape(cap or section.title, quote=True)}">'
                f'<img loading="lazy" src="{src}" alt="{html.escape(cap, quote=True)}">'
                f'{f"<span>{html.escape(cap)}</span>" if cap else ""}</button>'
                for src, cap in images)
            content = f'<div class="gallery">{tiles}</div>'
        else:
            content = ('<div class="coming-soon"><p>Photographs are on the way. '
                       'This gallery will fill in as images are added.</p></div>')
    else:
        content = (f'<article class="prose">{intro_html}</article>'
                   if intro_html else
                   '<div class="coming-soon"><p>Write-ups are on the way.</p></div>')

    lead = f'<p class="lede">{section.tagline}</p>'
    # For galleries the intro prose sits above the grid; for projects it IS the content.
    intro_block = (f'<div class="wrap narrow"><article class="prose">{intro_html}</article></div>'
                   if section.kind == "gallery" and intro_html else "")

    body = f"""
<div class="page-head">
  <div class="wrap narrow">
    <p class="eyebrow"><a href="/">Home</a> · {section.group}</p>
    <h1>{section.title}</h1>
    {lead}
  </div>
</div>
{intro_block}
<div class="wrap">
{content}
</div>
"""
    write(f"{section.slug}/index.html",
          page(section.title, body, active=section.slug, description=section.tagline))


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#14161a"/>
<circle cx="25" cy="32" r="13" fill="none" stroke="#E4572E" stroke-width="4"/>
<circle cx="41" cy="32" r="13" fill="none" stroke="#f2f0ec" stroke-width="4"/>
<circle cx="33" cy="32" r="3.5" fill="#E4572E"/>
</svg>
"""

# ---------------------------------------------------------------- main

def build():
    # Targeted clean: only the paths this script owns. Never touch src/, media/, .git.
    for s in SECTIONS:
        d = ROOT / s.slug
        if d.exists():
            shutil.rmtree(d)
    assets = ROOT / "assets"
    if assets.exists():
        shutil.rmtree(assets)

    build_home()
    for s in SECTIONS:
        build_section(s)

    assets.mkdir(exist_ok=True)
    for name in ("style.css", "site.js"):
        shutil.copy(STATIC / name, assets / name)
    (assets / "favicon.svg").write_text(FAVICON, encoding="utf-8")

    # Ensure gallery media folders exist so contributors know where photos go.
    for s in SECTIONS:
        if s.kind == "gallery":
            s.media_dir.mkdir(parents=True, exist_ok=True)
            keep = s.media_dir / ".gitkeep"
            if not keep.exists():
                keep.write_text("", encoding="utf-8")

    # GitHub Pages plumbing (root-served user site).
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    (ROOT / "CNAME").write_text("www.jeskridge.com\n", encoding="utf-8")

    pages = 1 + len(SECTIONS)
    print(f"Built {pages} pages -> {ROOT}")
    for s in SECTIONS:
        n = len(gallery_images(s)) if s.kind == "gallery" else "—"
        print(f"  {s.slug:24s} {s.kind:9s} images: {n}")
    print(f"  contact: {CONTACT_EMAIL or '(unset)'}   img base: {IMG_BASE}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--serve", action="store_true", help="preview on localhost after building")
    args = ap.parse_args()
    build()
    if args.serve:
        import functools, http.server, socketserver
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
        with socketserver.TCPServer(("", 8000), handler) as httpd:
            print("Preview: http://localhost:8000   (Ctrl+C to stop)")
            httpd.serve_forever()


if __name__ == "__main__":
    main()
