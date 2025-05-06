# scripts/generate_post.py

import os
import pandas as pd
import openai
from slugify import slugify
from dotenv import load_dotenv

# 1. Load API key from .env
load_dotenv()                       
openai.api_key = os.getenv("OPENAI_API_KEY")

# 2. Read your keywords CSV
df = pd.read_csv("data/keywords.csv")

# 3. Loop over each keyword and generate a post
for _, row in df.iterrows():
    prompt = (
        f"You are an expert reviewer. Write an 800-word, SEO-optimized blog post on \"{row.keyword}\". "
        "Use H2 headings, include a Pros & Cons table, and finish with a call-to-action linking to "
        f"{row.affiliate_url}."
    )

    # ← Updated API call here:
    resp = openai.chat.completions.create(
        model="gpt-4.1-nano",            # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}]
    )

    content = resp.choices[0].message.content

    # 4. Write out the Markdown file
    slug = slugify(row.keyword)
    out_dir = os.path.join("content", "post")  # ensure this folder exists
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{slug}.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"title: \"{row.keyword.title()}\"\n")
        f.write(f"date: {pd.Timestamp.now().isoformat()}\n")
        f.write("---\n\n")
        f.write(content)

    print("Generated:", out_file)
