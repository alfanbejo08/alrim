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

def parse_date(raw):
    """Turn strings or dates into a tz-naive UTC datetime."""
    # 1) If it’s already a datetime
    if isinstance(raw, datetime.datetime):
        dt = raw
    # 2) If it’s a date
    elif isinstance(raw, datetime.date):
        dt = datetime.datetime.combine(raw, datetime.time())
    # 3) Otherwise try parsing ISO strings
    else:
        s = (raw or "").rstrip("Z")
        try:
            dt = datetime.datetime.fromisoformat(s)
        except Exception:
            dt = datetime.datetime.utcnow()
    # 4) If it has tzinfo, convert → UTC and drop tzinfo
    if dt.tzinfo is not None:
        dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    return dt

def make_rss():
    entries = []
    # 1) Gather all posts
    for md_path in glob.glob("content/post/*.md"):
        post = frontmatter.load(md_path)
        slug = os.path.splitext(os.path.basename(md_path))[0]
        url = f"{SITE_URL}/{slug}/"

        title = escape(post.metadata.get("title",
                          slug.replace("-", " ").title()))
        description = escape(post.content.strip()[:150] + "…")

        raw_date = post.metadata.get("date")
        dt = parse_date(raw_date)

        entries.append({
            "dt": dt,
            "title": title,
            "link": url,
            "descr": description,
        })

    # 2) Sort by descending date
    entries.sort(key=lambda e: e["dt"], reverse=True)

    # 3) Build <item> blocks
    items_xml = []
    for e in entries:
        pub_date = e["dt"].strftime("%a, %d %b %Y %H:%M:%S GMT")
        items_xml.append(f"""
  <item>
    <title>{e['title']}</title>
    <link>{e['link']}</link>
    <pubDate>{pub_date}</pubDate>
    <description>{e['descr']}</description>
  </item>""")

    # 4) Wrap in RSS and write
    rss_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>AlrimCo Blog</title>
  <link>{SITE_URL}</link>
  <description>Latest posts from AlrimCo</description>
{''.join(items_xml)}
</channel>
</rss>"""

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(rss_feed)

    print(f"✔️  Generated RSS at {OUT_FILE}")

if __name__ == "__main__":
    make_rss()
