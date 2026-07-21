# AxisDigitalArchive.github.io

The GitHub Pages **organisation site** — it owns the `www.jeskridge.com` domain
and serves the landing page at the root.

Because this repo holds the custom domain (via `CNAME`), every *project* site in
the AxisDigitalArchive organisation is automatically served underneath it:

| Repo | URL |
|---|---|
| `AxisDigitalArchive.github.io` | https://www.jeskridge.com/ |
| `contact-improv-book` | https://www.jeskridge.com/contact-improv-book/ |

To add a project: enable Pages on that repo, build its site with links rooted at
`/<repo-name>/`, and add a card to `index.html` here. Project repos must **not**
carry their own `CNAME` — only this one does.

## DNS

`www.jeskridge.com` is a CNAME to `axisdigitalarchive.github.io`.
The apex `jeskridge.com` uses GitHub's A records so it redirects to `www`.
