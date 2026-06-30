# build.py - FINAL WORKING VERSION WITH CATEGORIES
import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))

def main():
    print("🏗️  Building HTML pages...")

    with open("data/posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    # Prepare posts for template
    for post in posts:
        date_str = post.get("date")
        if isinstance(date_str, str):
            try:
                post["date"] = datetime.strptime(date_str, "%Y-%m-%d")
            except:
                post["date"] = today
        post["date_str"] = date_str or today_str

    # Filter and sort
    visible_posts = [p for p in posts if p.get("date") and p["date"] <= today]
    visible_posts.sort(key=lambda x: x["date"], reverse=True)

    # 1. Zgradi glavno vstopno stran (index.html)
    index_template = env.get_template('index-template.html')
    rendered_index = index_template.render(posts=visible_posts, today=today_str)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(rendered_index)
    print("✅ index.html built")

    # 2. Zgradi vse kategorijske strani
    categories_pages = [
        "best-games",
        "gaming-gear",
        "gaming-news",
        "guides",
        "reviews",
        "tips-tricks"
    ]

    for cat_page in categories_pages:
        try:
            cat_template = env.get_template(f'{cat_page}.html')
            rendered_cat = cat_template.render(posts=visible_posts, today=today_str)
            with open(f"{cat_page}.html", "w", encoding="utf-8") as f:
                f.write(rendered_cat)
            print(f"✅ {cat_page}.html built")
        except Exception as e:
            print(f"⚠️ Could not build {cat_page}.html: Please ensure {cat_page}.html is inside templates/ folder.")

    print(f"🏗️  Build complete with {len(visible_posts)} visible posts.")

if __name__ == "__main__":
    main()