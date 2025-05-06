#!/usr/bin/env python3
import os
import shutil
import logging
from datetime import datetime, date
import frontmatter
import markdown
from jinja2 import Template

# ─── CONFIG ───────────────────────────────────────────────────────────────────
CONTENT_DIR   = "content/post"        # where your markdown lives
OUTPUT_DIR    = "public"              # output directory
STATIC_DIR    = "static"              # static assets
TEMPLATE_DIR  = "templates"           # HTML templates folder

BASE_URL      = os.getenv("BASE_URL", "https://alrimco.web.app")
GA_ID         = os.getenv("GA_MEASUREMENT_ID", "G-EF7SY2WX3S")

# ─── LOAD TEMPLATES ────────────────────────────────────────────────────────────
with open(os.path.join(TEMPLATE_DIR, "mainpage.html"), encoding="utf-8") as f:
    MAIN_TPL = Template(f.read())

with open(os.path.join(TEMPLATE_DIR, "postpage.html"), encoding="utf-8") as f:
    POST_TPL = Template(f.read())

# ─── GOOGLE ANALYTICS SNIPPET ─────────────────────────────────────────────────
GA_SNIPPET = f"""<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
</script>
"""

# ─── OPTIONAL NAV HEADER ──────────────────────────────────────────────────────
HEADER_HTML = """
<nav class="site-nav">
  <a href="/">Home</a>
  <a href="/deals/">Deals</a>
  <a href="/guides/">Guides</a>
  <a href="/blog/">Blog</a>
  <a href="/contact/">Contact</a>
</nav>
"""

# ─── SETUP LOGGING ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ─── LOAD POSTS ─────────────────────────────────────────────────────────────────
def load_posts():
    posts = []
    for fname in os.listdir(CONTENT_DIR):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(CONTENT_DIR, fname)
        fm   = frontmatter.load(path)
        html = markdown.markdown(fm.content, extensions=["tables"])
        slug = os.path.splitext(fname)[0]

        # parse and stringify date
        raw_date = fm.metadata.get("date")
        if isinstance(raw_date, datetime):
            date_str = raw_date.isoformat()
        elif isinstance(raw_date, date):
            date_str = datetime.combine(raw_date, datetime.min.time()).isoformat()
        else:
            date_str = str(raw_date) if raw_date else datetime.utcnow().isoformat()

        # description fallback
        desc = fm.metadata.get("description", "").strip()
        if not desc:
            desc = fm.content.strip().replace("\n", " ")[:150] + "…"

        posts.append({
            "slug":         slug,
            "title":        fm.metadata.get("title", slug.replace("-", " ").title()),
            "date":         date_str,
            "description":  desc,
            "html":         html,
            "affiliate_url": fm.metadata.get("affiliate_url", "")
        })

    posts.sort(key=lambda x: x["date"], reverse=True)
    return posts

# ─── RENDER INDEX ──────────────────────────────────────────────────────────────
def render_index(posts):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "index.html")
    logging.info("Writing index page: %s", out_path)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(MAIN_TPL.render(
            posts      = posts,
            ga_snippet = GA_SNIPPET,
            base_url   = BASE_URL,
            header     = HEADER_HTML,
            now        = datetime.utcnow()
        ))

# ─── RENDER POSTS ──────────────────────────────────────────────────────────────
def render_posts(posts):
    for post in posts:
        dest = os.path.join(OUTPUT_DIR, post["slug"])
        os.makedirs(dest, exist_ok=True)
        out_path = os.path.join(dest, "index.html")
        logging.info("Writing post page: %s", out_path)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(POST_TPL.render(
                post       = post,
                ga_snippet = GA_SNIPPET,
                base_url   = BASE_URL,
                header     = HEADER_HTML,
                now        = datetime.utcnow()
            ))

# ─── COPY STATIC ───────────────────────────────────────────────────────────────
def copy_static():
    if not os.path.isdir(STATIC_DIR):
        logging.warning("No static directory found; skipping.")
        return
    dest = os.path.join(OUTPUT_DIR, "static")
    if os.path.exists(dest):
        shutil.rmtree(dest)
    logging.info("Copying static assets: %s → %s", STATIC_DIR, dest)
    shutil.copytree(STATIC_DIR, dest)

# ─── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    if os.path.exists(OUTPUT_DIR):
        logging.info("Removing old output: %s", OUTPUT_DIR)
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    posts = load_posts()
    render_index(posts)
    render_posts(posts)
    copy_static()

    logging.info("Build complete: %d posts → %s", len(posts), OUTPUT_DIR)

if __name__ == "__main__":
    main()
