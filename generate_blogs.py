import os
import json
import shutil
import sys
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

SITE_NAME = "GameAtlas HQ"
VALID_CATEGORIES = {
    "Gaming News",
    "Guides",
    "Tips & Tricks",
    "Best Games",
    "Reviews",
    "Gaming Gear",
}

env = Environment(loader=FileSystemLoader("templates"))
detail_template = env.get_template("blog-detail.html")


def display_date(date_obj):
    return f"{date_obj.day} {date_obj.strftime('%B %Y')}"


def main(mode="obfuscated"):
    print(f"Generating blog posts... (mode: {mode})")

    os.makedirs("blogs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    with open("future_blogs.json", "r", encoding="utf-8") as f:
        future_blogs = json.load(f)

    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    posts = []
    published = 0

    for blog in future_blogs:
        date_str = blog.get("date")
        title = blog.get("title", "Untitled")
        category = blog.get("category")

        if not date_str:
            raise ValueError(f"Missing publication date for: {title}")
        if not category or category not in VALID_CATEGORIES:
            raise ValueError(f"Missing or invalid category for '{title}': {category!r}")
        if date_str > today_str:
            print(f"Skipping future post: {title} ({date_str})")
            continue

        real_slug = blog.get("real_slug")
        if not real_slug:
            content_file = blog.get("content_file", "")
            real_slug = os.path.splitext(os.path.basename(content_file))[0]
        if not real_slug:
            raise ValueError(f"Missing slug for: {title}")

        print(f"Processing: {title} ({date_str}) - slug: {real_slug}")

        if mode == "obfuscated" and "internal_id" in blog:
            content_src = os.path.join("src", blog["content_file"])
            image_src = os.path.join("src/images", blog["image"])
        else:
            content_src = os.path.join("content", f"{real_slug}.html")
            image_src = os.path.join("images", f"{real_slug}.jpg")

        if not os.path.exists(content_src):
            raise FileNotFoundError(f"Content file not found: {content_src}")

        with open(content_src, "r", encoding="utf-8") as f:
            content = f.read()

        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        seo_title = blog.get("seo_title") or f"{title} | {SITE_NAME}"

        blog_filename = f"{real_slug}.html"
        output_path = os.path.join("blogs", blog_filename)

        rendered = detail_template.render(
            post={
                "title": title,
                "seo_title": seo_title,
                "date": date_obj,
                "date_str": date_str,
                "date_display": display_date(date_obj),
                "image": real_slug + ".jpg",
                "excerpt": blog.get("excerpt", ""),
                "content": content,
                "meta": blog.get("meta", ""),
                "category": category,
                "slug": real_slug,
            }
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)

        public_image = os.path.join("images", real_slug + ".jpg")
        if not os.path.exists(image_src):
            raise FileNotFoundError(f"Image file not found: {image_src}")
        shutil.copy2(image_src, public_image)

        posts.append({
            "title": title,
            "seo_title": seo_title,
            "date": date_str,
            "excerpt": blog.get("excerpt", ""),
            "image": real_slug + ".jpg",
            "url": f"blogs/{real_slug}.html",
            "slug": real_slug,
            "category": category,
        })

        print(f"Generated: blogs/{blog_filename}")
        published += 1

    with open("data/posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"Process finished. Generated {published} visible posts.")


if __name__ == "__main__":
    mode_arg = sys.argv[1] if len(sys.argv) > 1 else "obfuscated"
    main(mode_arg)
