#!/usr/bin/env python3
import os
import glob
import datetime
import frontmatter
from xml.sax.saxutils import escape

# Base URL for your site
SITE_URL = os.getenv("BASE_URL", "https://alrimco.web.app")

# Where to write the RSS file
OUT_FILE = "public/rss.xml"

def make_rss():
    items = []
    # 1) Gather all posts
    for md_path in glob.glob("content/post/*.md"):
        post = frontmatter.load(md_path)
        slug = os.path.splitext(os.path.basename(md_path))[0]
        url = f"{SITE_URL}/{slug}/"

        # Title & description
        title = escape(post.metadata.get("title", slug.replace("-", " ").title()))
        description = escape(post.content.strip()[:150] + "…")

        # Date metadata (could be str or datetime)
        date_meta = post.metadata.get("date")
        items.append((date_meta, title, url, description))

    # 2) Sort by date descending
    items.sort(key=lambda x: x[0], reverse=True)

    # 3) Build <item> blocks
    rss_items = []
    for date_meta, title, url, description in items:
        # Parse date_meta into a datetime
        if isinstance(date_meta, str):
            # strip trailing Z if present
            _s = date_meta.rstrip("Z")
            try:
                dt = datetime.datetime.fromisoformat(_s)
            except ValueError:
                dt = datetime.datetime.utcnow()
        elif isinstance(date_meta, datetime.datetime):
            dt = date_meta
        elif isinstance(date_meta, datetime.date):
            dt = datetime.datetime.combine(date_meta, datetime.time())
        else:
            dt = datetime.datetime.utcnow()

        pub_date = dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

        rss_items.append(f"""
  <item>
    <title>{title}</title>
    <link>{url}</link>
    <pubDate>{pub_date}</pubDate>
    <description>{description}</description>
  </item>""")

    # 4) Wrap in RSS & write file
    rss_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>AlrimCo Blog</title>
  <link>{SITE_URL}</link>
  <description>Latest posts from AlrimCo</description>
{''.join(rss_items)}
</channel>
</rss>"""

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(rss_feed)

    print(f"✔️  Generated RSS at {OUT_FILE}")

if __name__ == "__main__":
    make_rss()
