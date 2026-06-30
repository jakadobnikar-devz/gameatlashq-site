# obfuscate.py  (Updated version for existing sites)
import os
import json
import shutil
import random
import string

def generate_random_id(length=12):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def main():
    print("🚀 Starting obfuscation for existing site...")

    os.makedirs("src/images", exist_ok=True)

    with open("future_blogs.json", "r", encoding="utf-8") as f:
        blogs = json.load(f)

    for blog in blogs:
        # Get original slug from current content_file
        if "real_slug" not in blog:
            content_filename = os.path.basename(blog.get("content_file", ""))
            blog["real_slug"] = os.path.splitext(content_filename)[0]

        if "internal_id" not in blog:
            random_id = generate_random_id()
            blog["internal_id"] = random_id
            blog["content_file"] = f"{random_id}.dat"
            blog["image"] = f"{random_id}.bak"

        # Copy files
        real_slug = blog["real_slug"]
        random_id = blog["internal_id"]

        old_content = os.path.join("content", f"{real_slug}.html")
        old_image = os.path.join("images", f"{real_slug}.jpg")

        new_content = os.path.join("src", blog["content_file"])
        new_image = os.path.join("src/images", blog["image"])

        if os.path.exists(old_content):
            shutil.copy2(old_content, new_content)
            print(f"✅ {real_slug}.html → {blog['content_file']}")
        else:
            print(f"⚠️ Missing: {old_content}")

        if os.path.exists(old_image):
            shutil.copy2(old_image, new_image)
            print(f"✅ {real_slug}.jpg → {blog['image']}")
        else:
            print(f"⚠️ Missing image: {old_image}")

    # Save updated JSON
    with open("future_blogs.json", "w", encoding="utf-8") as f:
        json.dump(blogs, f, ensure_ascii=False, indent=2)

    print("\n✅ Obfuscation completed!")
    print("   All existing entries now have mapping (real_slug + internal_id)")
    print("   Raw files copied to src/ with .dat and .bak extensions")

if __name__ == "__main__":
    main()