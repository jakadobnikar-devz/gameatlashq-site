import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates"))

CATEGORIES = [
    "best-games",
    "gaming-gear",
    "gaming-news",
    "guides",
    "reviews",
    "tips-tricks",
]


def display_date(date_obj):
    return f"{date_obj.day} {date_obj.strftime('%B %Y')}"


def main():
    print("Building HTML pages...")

    with open("data/posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    for post in posts:
        date_str = post.get("date")
        if not date_str:
            continue
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        post["date"] = date_obj
        post["date_str"] = date_str
        post["date_display"] = display_date(date_obj)

    visible_posts = [p for p in posts if p.get("date") and p["date"] <= today]
    visible_posts.sort(key=lambda x: x["date"], reverse=True)

    index_template = env.get_template("index-template.html")
    rendered_index = index_template.render(posts=visible_posts, today=today_str)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(rendered_index)
    print("index.html built")

    for cat_page in CATEGORIES:
        cat_template = env.get_template(f"{cat_page}.html")
        rendered_cat = cat_template.render(posts=visible_posts, today=today_str)
        with open(f"{cat_page}.html", "w", encoding="utf-8") as f:
            f.write(rendered_cat)
        print(f"{cat_page}.html built")

    print(f"Build complete with {len(visible_posts)} visible posts.")


if __name__ == "__main__":
    main()
