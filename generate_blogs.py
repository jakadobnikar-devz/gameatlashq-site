# generate_blogs.py - POPRAVLJENA VERZIJA (Brez IndentationError)
import os
import json
import shutil
import sys
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
detail_template = env.get_template('blog-detail.html')

def main(mode="obfuscated"):
    print(f"🚀 Generating blog posts... (mode: {mode})")

    # Zagotovimo obstoj potrebnih map
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

        if date_str > today_str:
            print(f"⏳ Skipping future post: {title} ({date_str})")
            continue

        real_slug = blog.get("real_slug")
        if not real_slug:
            content_file = blog.get("content_file", "")
            real_slug = os.path.splitext(os.path.basename(content_file))[0]

        print(f"Processing: {title} ({date_str}) - slug: {real_slug}")

        # Nastavimo poti do virov glede na način delovanja (zamegljeno ali surovo)
        if mode == "obfuscated" and "internal_id" in blog:
            content_src = os.path.join("src", blog["content_file"])
            image_src = os.path.join("src/images", blog["image"])
        else:
            content_src = os.path.join("content", f"{real_slug}.html")
            image_src = os.path.join("images", f"{real_slug}.jpg")

        if not os.path.exists(content_src):
            print(f"⚠️ Content file not found: {content_src}")
            continue

        with open(content_src, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except:
            date_obj = today

        blog_filename = f"{real_slug}.html"
        output_path = os.path.join("blogs", blog_filename)

        # Izris Jinja2 predloge (Kategorija se uspešno črpa iz JSON-a)
        rendered = detail_template.render(
            post={
                "title": title,
                "date": date_obj,
                "image": real_slug + ".jpg",
                "excerpt": blog.get("excerpt", ""),
                "content": content,
                "meta": blog.get("meta", ""),
                "category": blog.get("category", "Zdravstvena politika"),
                "slug": real_slug
            }
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)

        public_image = os.path.join("images", real_slug + ".jpg")
        if os.path.exists(image_src):
            shutil.copy2(image_src, public_image)

        posts.append({
            "title": title,
            "date": date_str,
            "excerpt": blog.get("excerpt", ""),
            "image": real_slug + ".jpg",
            "url": f"blogs/{real_slug}.html",
            "slug": real_slug,
            "category": blog.get("category", "Potrošniška tehnologija")
        })

        print(f"✅ Generated: blogs/{blog_filename}")
        published += 1

    with open("data/posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"🎉 Process finished. Successfully generated {published} visible posts inside data/posts.json")

if __name__ == "__main__":
    # Privzeto deluje v zamegljenem (obfuscated) načinu
    mode_arg = sys.argv[1] if len(sys.argv) > 1 else "obfuscated"
    main(mode_arg)