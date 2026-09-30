import json
import shutil
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

SITE_URL = "https://gameatlashq.com"
ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"

STATIC_PUBLIC = [
    "index.html",
    "about-GAHQ.html",
    "editorial-policy.html",
    "gaming-glossary.html",
    "tos-privacy.html",
    "best-games.html",
    "gaming-gear.html",
    "gaming-news.html",
    "guides.html",
    "reviews.html",
    "tips-tricks.html",
    "404.html",
]

INDEXABLE_STATIC = [
    "/",
    "/about-GAHQ.html",
    "/editorial-policy.html",
    "/gaming-glossary.html",
]

CATEGORY_FILES = {
    "Best Games": "best-games.html",
    "Gaming Gear": "gaming-gear.html",
    "Gaming News": "gaming-news.html",
    "Guides": "guides.html",
    "Reviews": "reviews.html",
    "Tips & Tricks": "tips-tricks.html",
}


def copy_required(src, dst):
    if not src.exists():
        raise FileNotFoundError(f"Required publish file missing: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main():
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    (PUBLIC / "blogs").mkdir(parents=True)
    (PUBLIC / "images").mkdir(parents=True)

    with open(ROOT / "data/posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    for filename in STATIC_PUBLIC:
        copy_required(ROOT / filename, PUBLIC / filename)

    copy_required(ROOT / "images/main-logo.webp", PUBLIC / "images/main-logo.webp")

    seen_slugs = set()
    for post in posts:
        slug = post["slug"]
        if slug in seen_slugs:
            raise ValueError(f"Duplicate published slug: {slug}")
        seen_slugs.add(slug)
        copy_required(ROOT / "blogs" / f"{slug}.html", PUBLIC / "blogs" / f"{slug}.html")
        copy_required(ROOT / "images" / post["image"], PUBLIC / "images" / post["image"])

    category_counts = Counter(post["category"] for post in posts)

    sitemap_urls = list(INDEXABLE_STATIC)
    for category, filename in CATEGORY_FILES.items():
        if category_counts.get(category, 0) > 0:
            sitemap_urls.append(f"/{filename}")

    blog_entries = [(f"/{post['url']}", post["date"]) for post in posts]

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for path in sitemap_urls:
        lines.append(f"  <url><loc>{escape(SITE_URL + path)}</loc></url>")
    for path, date in blog_entries:
        lines.append(
            f"  <url><loc>{escape(SITE_URL + path)}</loc>"
            f"<lastmod>{escape(date)}</lastmod></url>"
        )
    lines.append("</urlset>")

    sitemap_path = PUBLIC / "sitemap.xml"
    sitemap_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    robots_path = PUBLIC / "robots.txt"
    robots_path.write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://gameatlashq.com/sitemap.xml\n",
        encoding="utf-8",
    )

    (PUBLIC / ".nojekyll").touch()

    if not sitemap_path.is_file() or sitemap_path.stat().st_size == 0:
        raise RuntimeError("sitemap.xml was not created")
    if not robots_path.is_file() or robots_path.stat().st_size == 0:
        raise RuntimeError("robots.txt was not created")

    print(f"Prepared safe public artifact with {len(posts)} live posts.")
    print(f"Sitemap contains {len(sitemap_urls) + len(blog_entries)} indexable URLs.")
    print(f"Created: {sitemap_path}")
    print(f"Created: {robots_path}")


if __name__ == "__main__":
    main()
