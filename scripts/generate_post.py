#!/usr/bin/env python3
import os
import sys
import logging
from datetime import datetime
import pandas as pd
import openai
from slugify import slugify
from dotenv import load_dotenv

# ——— CONFIGURATION —————————————————————————————————————————————————

# Path to your keywords CSV
CSV_PATH = "data/keywords.csv"

# Where to write your Markdown posts
OUTPUT_DIR = "content/post"

# Default OpenAI model; override with OPENAI_MODEL env var if desired
DEFAULT_MODEL = "gpt-4.1-nano"

# Length of each post in words
POST_LENGTH = 800

# ——— FUNCTIONS ———————————————————————————————————————————————————

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def load_api_key():
    load_dotenv()  # look for a .env file
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        logging.error("OPENAI_API_KEY not set. Exiting.")
        sys.exit(1)
    openai.api_key = key

def read_keywords(csv_path=CSV_PATH):
    if not os.path.exists(csv_path):
        logging.error(f"Keywords CSV not found at {csv_path}")
        sys.exit(1)
    return pd.read_csv(csv_path)

def build_prompt(keyword, affiliate_url, length=POST_LENGTH):
    return (
        f"You are an expert product reviewer. Write an {length}-word, SEO-optimized blog post on \"{keyword}\".\n"
        "- Use H2 headings (##)\n"
        "- Include a Pros & Cons table\n"
        f"- End with a call-to-action linking to {affiliate_url}\n"
    )

def generate_content(prompt, model):
    logging.info("Calling OpenAI with model=%s", model)
    resp = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content

def save_markdown(keyword, content, out_dir=OUTPUT_DIR):
    slug = slugify(keyword)
    filename = os.path.join(out_dir, f"{slug}.md")
    os.makedirs(out_dir, exist_ok=True)

    # pull first paragraph or first 150 chars as a description
    first_para = content.strip().split("\n\n")[0]
    description = first_para[:150].replace("\n", " ") + "..."

    frontmatter = [
        "---",
        f'title: "{keyword.title()}"',
        f'date: {datetime.utcnow().isoformat()}Z',
        f'description: "{description}"',
        f'slug: "{slug}"',
        "---\n",
    ]

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(frontmatter))
        f.write(content)

    logging.info("Saved post: %s", filename)

# ——— MAIN ———————————————————————————————————————————————————————

def main():
    setup_logging()
    load_api_key()

    df = read_keywords()
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    for _, row in df.iterrows():
        kw = row.keyword
        url = row.affiliate_url
        logging.info("Generating post for keyword: %s", kw)
        try:
            prompt = build_prompt(kw, url, POST_LENGTH)
            content = generate_content(prompt, model)
            save_markdown(kw, content)
        except Exception as e:
            logging.exception("Failed to generate post for %s: %s", kw, e)

if __name__ == "__main__":
    main()
