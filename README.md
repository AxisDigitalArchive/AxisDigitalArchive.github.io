# AxisDigitalArchive.github.io — www.jeskridge.com

The GitHub Pages **organisation site**. It owns the `www.jeskridge.com` domain
(via `CNAME`) and serves the hub at the domain root. Project sites in the
organisation are served underneath it, e.g. the book at
`www.jeskridge.com/contact-improv-book/`. Project repos must **not** carry their
own `CNAME` — only this one does.

## Structure

```
build.py              the generator — run it to (re)build the site
src/
  sections/*.md       the intro prose for each section (edit these)
  static/style.css    shared stylesheet
  static/site.js      theme toggle, mobile nav, gallery lightbox
media/<section>/      gallery images (photography sections)
index.html            generated — do not edit by hand
<section>/index.html  generated — do not edit by hand
assets/               generated — do not edit by hand
CNAME, .nojekyll      generated
```

## Building

```
python build.py            # regenerate the site
python build.py --serve    # regenerate, then preview at http://localhost:8000
```

## Adding content

- **Edit a section's intro:** change `src/sections/<slug>.md` (plain Markdown), rebuild.
- **Add a project** (engineering, light, music, drumming): add a `## Project name`
  heading and a paragraph to that section's `.md` file. Rebuild.
- **Add photographs** (nature, tech): drop optimised images into
  `media/<slug>/`. An optional `<image>.txt` sidecar adds a caption. Rebuild.
- **New top-level section:** add a `Section(...)` to the list in `build.py` and a
  matching `src/sections/<slug>.md`.

`index.html`, the section folders, and `assets/` are regenerated every build —
never edit them directly.

## Media at scale

Gallery images are served from `/media` (committed to this repo) via the
`IMG_BASE` setting in `build.py`. When a photo library outgrows what belongs in
git (roughly a gigabyte, or any video), point `IMG_BASE` at a Cloudflare R2
domain (e.g. `https://img.jeskridge.com`) and serve the files from there. No
other change is required.

## DNS

`www.jeskridge.com` is a CNAME to `axisdigitalarchive.github.io`.
The apex `jeskridge.com` uses GitHub's A records so it redirects to `www`.
