import os, shutil
import frontmatter, markdown
from jinja2 import Template

CONTENT = "content/post"
OUTPUT  = "public"

POST_TMPL = Template("""
<!DOCTYPE html><html><head><meta charset="utf-8">
<title>{{meta.title}}</title></head><body>
<h1>{{meta.title}}</h1><p><em>{{meta.date}}</em></p>{{content|safe}}
</body></html>
""")

INDEX_TMPL = Template("""
<!DOCTYPE html><html><head><meta charset="utf-8">
<title>All Posts</title></head><body>
<h1>All Posts</h1><ul>
{% for p in posts %}
  <li><a href="./{{p.slug}}/index.html">{{p.meta.title}}</a></li>
{% endfor %}
</ul></body></html>
""")

def build():
    if os.path.exists(OUTPUT):
        shutil.rmtree(OUTPUT)
    os.makedirs(OUTPUT)
    posts = []
    for fn in os.listdir(CONTENT):
        if not fn.endswith(".md"): continue
        path = os.path.join(CONTENT, fn)
        fm = frontmatter.load(path)
        html = markdown.markdown(fm.content, extensions=["tables"])
        slug = os.path.splitext(fn)[0]
        posts.append({"slug":slug,"meta":fm.metadata,"html":html})
    # sort by date desc
    posts.sort(key=lambda x: x["meta"]["date"], reverse=True)

    for p in posts:
        d = os.path.join(OUTPUT, p["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d,"index.html"), "w", encoding="utf-8") as f:
            f.write(POST_TMPL.render(meta=p["meta"], content=p["html"]))

    with open(os.path.join(OUTPUT,"index.html"), "w", encoding="utf-8") as f:
        f.write(INDEX_TMPL.render(posts=posts))

    print(f"Built {len(posts)} posts to {OUTPUT}/")

if __name__=="__main__":
    build()
