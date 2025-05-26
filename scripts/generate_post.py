#!/usr/bin/env python3
import os
import sys
import logging
from datetime import datetime
import pandas as pd
import requests
import io
import openai
from slugify import slugify
from dotenv import load_dotenv

# ——— CONFIGURATION ———————————————————————————————————————————————————

# URL to your published Google Sheet CSV export
SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "11vrnE62rZgQ-4tPzb-_diM9EbDIkBT8Fh6-khEIetMA"
    "/export?format=csv"
)

# Where to write your Markdown posts
OUTPUT_DIR = "content/post"

DEFAULT_MODEL = "gpt-4.1-nano"

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

def read_latest_keyword():
    try:
        resp = requests.get(SHEET_CSV_URL)
        resp.raise_for_status()
    except Exception as e:
        logging.error("Failed to fetch sheet: %s", e)
        sys.exit(1)

    df = pd.read_csv(io.StringIO(resp.text))

    # Rename columns if needed
    if "affiliate_link" in df.columns:
        df = df.rename(columns={"affiliate_link": "affiliate_url"})

    # Check if the essential columns exist
    if df.empty:
        logging.error("No data found in sheet; exiting.")
        sys.exit(1)
    if not {"keyword", "affiliate_url", "images"}.issubset(df.columns):
        logging.error("Sheet must have 'keyword', 'affiliate_url', and 'images' columns.")
        sys.exit(1)

    # Get the image URL, use a placeholder if it's empty
    image_url = df['images'].iloc[0] if pd.notna(df['images'].iloc[0]) else "E:/Coding/Alrim/placehorder/placeh.png"

    # Pick only the last row (newest entry)
    return df.tail(1).iloc[0], image_url

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

def save_markdown(keyword, affiliate_url, image_url, content, out_dir=OUTPUT_DIR):
    slug = slugify(keyword)
    filename = os.path.join(out_dir, f"{slug}.md")
    os.makedirs(out_dir, exist_ok=True)

    # Pull first paragraph or first 150 chars as a description
    first_para = content.strip().split("\n\n")[0]
    description = first_para[:150].replace("\n", " ") + "..."

    frontmatter = [
        "---",
        f'title: "{keyword}"',
        f'date: {datetime.utcnow().isoformat()}Z',
        f'description: "{description}"',
        f'slug: "{slug}"',
        f'affiliate_url: "{affiliate_url}"',
        f'image_url: "{image_url}"',  # Add the image_url to the frontmatter
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

    row, image_url = read_latest_keyword()  # Get both the row and image URL
    kw = row["keyword"]
    url = row["affiliate_url"]

    logging.info("Generating post for latest keyword: %s", kw)
    try:
        prompt = build_prompt(kw, url, POST_LENGTH)
        content = generate_content(prompt, os.getenv("OPENAI_MODEL", DEFAULT_MODEL))
        save_markdown(kw, url, image_url, content)  # Pass image_url to save_markdown
    except Exception as e:
        logging.exception("Failed to generate post for %s: %s", kw, e)
        sys.exit(1)

if __name__ == "__main__":
    main()
