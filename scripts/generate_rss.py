import os, glob, datetime
import frontmatter
from xml.sax.saxutils import escape

SITE_URL = "https://alrimco.web.app"

def make_rss():
    items = []
    for md in glob.glob("content/post/*.md"):
        post = frontmatter.load(md)
        slug = os.path.basename(md).replace(".md","")
        url = f"{SITE_URL}/posts/{slug}/"
        title = escape(post['title'])
        date = post['date']
        description = escape(post.content[:150] + "…")
        items.append((date, title, url, description))

    # sort by date descending
    items.sort(reverse=True)

    rss_items = "\n".join(f"""
    <item>
      <title>{t}</title>
      <link>{u}</link>
      <pubDate>{datetime.datetime.fromisoformat(d).strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
      <description>{desc}</description>
    </item>""" for d,t,u,desc in items)

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>AlrimCo Blog</title>
  <link>{SITE_URL}</link>
  <description>Latest posts from AlrimCo affiliate blog</description>
  {rss_items}
</channel>
</rss>"""

    os.makedirs("public", exist_ok=True)
    with open("public/rss.xml","w",encoding="utf-8") as f:
        f.write(rss)

if __name__=="__main__":
    make_rss()
