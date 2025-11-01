import os
import re
import sys
import random
from datetime import datetime
from github import Github, Auth, UnknownObjectException

POSTS_DIR = 'posts'
REPO_NAME = os.environ.get("GITHUB_REPOSITORY")
TOC_ISSUE_NUMBER = 1
TOC_TITLE = "Blog Table of Contents"
TOC_IGNORE_POST_IDS = []
POST_ID_TAG_REGEX = re.compile(r"<!-- post-id: ([a-z0-9]{6}) -->")

def get_remote_issues(repo):
    issue_map = {}
    for issue in repo.get_issues(state='open'):
        if issue.number == TOC_ISSUE_NUMBER: continue
        match = POST_ID_TAG_REGEX.search(issue.body)
        if match:
            issue_map[match.group(1)] = issue
    return issue_map

def get_local_posts():
    local_posts = []
    for dir_name in os.listdir(POSTS_DIR):
        post_dir = os.path.join(POSTS_DIR, dir_name)
        index_file = os.path.join(post_dir, 'index.md')
        if not os.path.isdir(post_dir) or not os.path.exists(index_file):
            continue
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        fm_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not fm_match: continue
        front_matter = fm_match.group(1)
        title = re.search(r'^\s*title:\s*(.*)', front_matter, re.MULTILINE)
        date = re.search(r'^\s*date:\s*(\d{4}-\d{2}-\d{2})', front_matter, re.MULTILINE)
        label = re.search(r'^\s*label:\s*(.*)', front_matter, re.MULTILINE)
        post_id = re.search(r'^\s*id:\s*([a-z0-9]{6})', front_matter, re.MULTILINE)
        if title and date and post_id:
            local_posts.append({
                'id': post_id.group(1).strip(), 'title': title.group(1).strip(),
                'date': date.group(1).strip(), 'body': content[fm_match.end():].strip(),
                'labels': [label.group(1).strip()] if label else [],
                'slug': dir_name
            })
    return local_posts

def convert_image_paths(body, slug, repo_name):
    base_url = f"https://raw.githubusercontent.com/{repo_name}/main/{POSTS_DIR}/{slug}/"
    return re.sub(r'(assets/[^)\s]+)', lambda m: base_url + m.group(1), body)

def sync_issues(repo, local_posts, remote_issues, repo_labels):
    local_posts.sort(key=lambda p: datetime.strptime(p['date'], '%Y-%m-%d'))
    final_issue_map = remote_issues.copy()
    processed_post_ids = set()

    for post in local_posts:
        post_id, slug = post['id'], post['slug']
        processed_post_ids.add(post_id)
        labels_to_apply = []
        for name in post['labels']:
            if name not in repo_labels:
                print(f"Label '{name}' not found. Creating it...")
                color = f"{random.randint(0, 0xFFFFFF):06x}"
                new_label = repo.create_label(name=name, color=color)
                repo_labels[name] = new_label
            labels_to_apply.append(repo_labels[name])
        
        body_with_urls = convert_image_paths(post['body'], slug, REPO_NAME)
        body_with_id = body_with_urls + f"\n\n<!-- post-id: {post_id} -->"
        
        if post_id in remote_issues:
            issue = remote_issues[post_id]
            clean_remote_body = POST_ID_TAG_REGEX.sub('', issue.body).strip()
            current_labels = {l.name for l in issue.labels}
            new_labels = {l.name for l in labels_to_apply}
            if issue.title != post['title'] or clean_remote_body != body_with_urls or current_labels != new_labels:
                print(f"Updating issue for post id: {post_id}")
                issue.edit(title=post['title'], body=body_with_id, labels=list(new_labels))
        else:
            print(f"Creating issue for new post id: {post_id}")
            new_issue = repo.create_issue(title=post['title'], body=body_with_id, labels=labels_to_apply)
            final_issue_map[post_id] = new_issue
    
    deleted_ids = set(remote_issues.keys()) - processed_post_ids
    for post_id in deleted_ids:
        print(f"Closing issue for deleted post id: {post_id}")
        remote_issues[post_id].edit(state='closed')
        
    return final_issue_map

def update_toc_issue(repo, posts, issue_map):
    try:
        toc_issue = repo.get_issue(number=TOC_ISSUE_NUMBER)
    except UnknownObjectException:
        print("Issue #1 not found. Creating a new Table of Contents.")
        toc_issue = repo.create_issue(title=TOC_TITLE, body="")
    else:
        print("Found Table of Contents at Issue #1.")

    display_posts = sorted(posts, key=lambda p: datetime.strptime(p['date'], '%Y-%m-%d'), reverse=True)
    toc_lines = []
    for post in display_posts:
        if post['id'] in TOC_IGNORE_POST_IDS: continue
        issue = issue_map.get(post['id'])
        if issue:
            toc_lines.append(f"- [{post['title']}]({issue.html_url}) / {post['date']}")
    toc_body = "\n".join(toc_lines)
    if toc_issue.body != toc_body:
        print("Updating Table of Contents...")
        toc_issue.edit(body=toc_body)
    else:
        print("Table of Contents is already up to date.")

if __name__ == "__main__":
    if not REPO_NAME:
        print("Error: GITHUB_REPOSITORY environment variable not found.")
        sys.exit(1)
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable not found.")
        sys.exit(1)

    auth = Auth.Token(token)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)
    all_repo_labels = {label.name: label for label in repo.get_labels()}
    remote_issue_map = get_remote_issues(repo)
    local_posts_list = get_local_posts()
    final_issue_map = sync_issues(repo, local_posts_list, remote_issue_map, all_repo_labels)
    update_toc_issue(repo, local_posts_list, final_issue_map)
    print("Blog update process finished.")