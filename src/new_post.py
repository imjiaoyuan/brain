import os
import re
import random
import string
from datetime import datetime

POSTS_DIR = '_posts'

def generate_alternating_id():
    return "".join(random.choice(string.ascii_lowercase) + random.choice(string.digits) for _ in range(3))

def create_new_post():
    title = input("Enter post title: ")
    if not title:
        print("\nError: Title cannot be empty. Aborted.")
        return

    label = input("Enter post label (default: uncategorized): ") or 'uncategorized'
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    slug = re.sub(r'[\s-]+', '-', re.sub(r'[^a-z0-9\s-]', '', title.lower())).strip('-')
    
    post_dir = os.path.join(POSTS_DIR, slug)
    if os.path.exists(post_dir):
        print(f"\nError: Directory '{post_dir}' already exists.")
        return
        
    assets_dir = os.path.join(post_dir, 'assets')
    os.makedirs(assets_dir)
    
    file_path = os.path.join(post_dir, 'index.md')
    front_matter = f"""---
title: {title}
date: {current_date}
label: {label}
id: {generate_alternating_id()}
---

"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(front_matter)
        
    print(f"\nSuccessfully created new post structure in: {post_dir}")
    print(f"  - Markdown file: {file_path}")
    print(f"  - Assets folder: {assets_dir}")

if __name__ == "__main__":
    create_new_post()