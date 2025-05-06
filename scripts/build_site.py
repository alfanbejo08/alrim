#!/usr/bin/env python3
import os
import shutil
import logging
from datetime import datetime
import frontmatter
import markdown
from jinja2 import Template

# ─── CONFIG ───────────────────────────────────────────────────────────────────
CONTENT_DIR   = "content/post"               # where your markdown lives
OUTPUT_DIR    = "public"                      # where to output generated files
STATIC_DIR    = "static"                      # your css/js/images go here
TEMPLATE_DIR  = "templates"                   # your two html templates here

BASE_URL      = os.getenv("BASE_URL", "https://alrimco.web.app")
GA_ID         = os.getenv("GA_MEASUREMENT_ID", "G-EF7SY2WX3S")

# ─── LOAD TEMPLATES ────────────────────────────────────────────────────────────
with open(os.path.join(TEMPLATE_DIR, "mainpage.html"), encoding="utf-8") as f:
    MAIN_TPL = Template(f.read())

with open(os.path.join(TEMPLATE_DIR, "postpage.html"), encoding="utf-8") as f:
    POST_TPL = Template(f.read())

# ─── GA SNIPPET ─────────────────────────────────────────────────────────────────
GA_SNIPPET = f"""<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
</script>
"""

# ─── OPTIONAL HEADER HTML ──────────────────────────────────────────────────────
# If you want a consistent header, or you can bake it into your templates
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

# ─── BUILD HELPERS ─────────────────────────────────────────────────────────────

def load_posts():
    posts = []
    for fn in os.listdir(CONTENT_DIR):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(CONTENT_DIR, fn)
        fm   = frontmatter.load(path)
        html = markdown.markdown(fm.content, extensions=["tables"])
        slug = os.path.splitext(fn)[0]

        # build a description fallback
        desc = fm.metadata.get("description", "")
        if not desc:
            desc = fm.content.strip().replace("\n"," ")[:150] + "…"

        posts.append({
            "slug": slug,
            "meta": {
                "title":       fm.metadata.get("title", slug.replace("-", " ").title()),
                "date":        fm.metadata.get("date", datetime.utcnow().isoformat()+"Z"),
                "description": desc,
                "slug":        slug,
            },
            "html": html,
        })

    # newest first
    posts.sort(key=lambda x: x["meta"]["date"], reverse=True)
    return posts

def render_index(posts):
    """Render the landing page from mainpage.html template."""
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

def render_posts(posts):
    """Render each post at public/<slug>/index.html using postpage.html template."""
    for p in posts:
        dest_dir = os.path.join(OUTPUT_DIR, p["slug"])
        os.makedirs(dest_dir, exist_ok=True)
        out_path = os.path.join(dest_dir, "index.html")
        logging.info("Writing post: %s", out_path)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(POST_TPL.render(
                meta       = p["meta"],
                content    = p["html"],
                ga_snippet = GA_SNIPPET,
                base_url   = BASE_URL,
                header     = HEADER_HTML,
                now        = datetime.utcnow()
            ))

def copy_static():
    """Copy everything under static/ to public/static/."""
    if not os.path.isdir(STATIC_DIR):
        logging.warning("No static directory found, skipping.")
        return
    target = os.path.join(OUTPUT_DIR, "static")
    if os.path.exists(target):
        shutil.rmtree(target)
    logging.info("Copying %s → %s", STATIC_DIR, target)
    shutil.copytree(STATIC_DIR, target)

# ─── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    # clean
    if os.path.exists(OUTPUT_DIR):
        logging.info("Removing old output: %s", OUTPUT_DIR)
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    posts = load_posts()
    render_index(posts)
    render_posts(posts)
    copy_static()

    logging.info("Done! %d posts → %s", len(posts), OUTPUT_DIR)

if __name__ == "__main__":
    main()
