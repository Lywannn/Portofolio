import json
import os
import time
from datetime import datetime
from pathlib import Path

import frontmatter
import markdown2
import requests
from flask import Flask, abort, render_template, request, url_for
from datetime import date as date_type

import config

app = Flask(__name__)

CACHE_FILE = Path("static/data/github_cache.json")
CACHE_TTL = 3600  # 1 hour


def fetch_github_data():
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

    if CACHE_FILE.exists():
        age = time.time() - CACHE_FILE.stat().st_mtime
        if age < CACHE_TTL:
            with open(CACHE_FILE) as f:
                return json.load(f)

    try:
        headers = {"Accept": "application/vnd.github.v3+json"}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"

        resp = requests.get(
            f"https://api.github.com/users/{config.GITHUB_USERNAME}/repos",
            params={"per_page": 100, "sort": "updated"},
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        repos = resp.json()

        resp2 = requests.get(
            f"https://api.github.com/users/{config.GITHUB_USERNAME}",
            headers=headers,
            timeout=10,
        )
        resp2.raise_for_status()
        user = resp2.json()

        data = {"repos": repos, "user": user, "fetched_at": time.time()}
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)
        return data

    except Exception:
        if CACHE_FILE.exists():
            with open(CACHE_FILE) as f:
                return json.load(f)
        return {"repos": [], "user": {}, "fetched_at": 0}


def process_repos(repos):
    filtered = []
    for r in repos:
        if r["name"] in config.EXCLUDED_REPOS:
            continue
        if not config.SHOW_FORKS and r.get("fork"):
            continue
        filtered.append(r)

    pinned, rest = [], []
    for r in filtered:
        if r["name"] in config.PINNED_REPOS:
            pinned.append(r)
        else:
            rest.append(r)

    pinned.sort(key=lambda r: config.PINNED_REPOS.index(r["name"]))
    rest.sort(key=lambda r: r.get("stargazers_count", 0), reverse=True)
    return pinned + rest


def get_language_stats(repos):
    lang_counts = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
    total = sum(lang_counts.values()) or 1
    return sorted(
        [{"name": k, "count": v, "pct": round(v / total * 100)} for k, v in lang_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:8]


def get_blog_posts():
    posts = []
    blog_dir = Path("content/blog")
    if not blog_dir.exists():
        return posts

    for md_file in sorted(blog_dir.glob("*.md"), reverse=True):
        post = frontmatter.load(md_file)
        slug = md_file.stem
        date = post.metadata.get("date", "")
        if isinstance(date, (datetime, date_type)):
            date_str = date.strftime("%B %d, %Y")
            date_iso = date.strftime("%Y-%m-%d")
        else:
            date_str = str(date)
            date_iso = str(date)

        words = len(post.content.split())
        reading_time = max(1, round(words / 200))

        posts.append({
            "slug": slug,
            "title": post.metadata.get("title", slug),
            "date": date_str,
            "date_iso": date_iso,
            "tags": post.metadata.get("tags", []),
            "excerpt": post.metadata.get("excerpt", post.content[:160].strip() + "…"),
            "cover": post.metadata.get("cover_image", ""),
            "reading_time": reading_time,
        })
    return posts


def render_blog_post(slug):
    md_file = Path(f"content/blog/{slug}.md")
    if not md_file.exists():
        return None

    post = frontmatter.load(md_file)
    date = post.metadata.get("date", "")
    if isinstance(date, datetime):
        date_str = date.strftime("%B %d, %Y")
    else:
        date_str = str(date)

    html = markdown2.markdown(
        post.content,
        extras=["fenced-code-blocks", "tables", "header-ids", "toc", "strike", "task_list"],
    )
    words = len(post.content.split())
    return {
        "slug": slug,
        "title": post.metadata.get("title", slug),
        "date": date_str,
        "tags": post.metadata.get("tags", []),
        "cover": post.metadata.get("cover_image", ""),
        "reading_time": max(1, round(words / 200)),
        "html": html,
        "toc": getattr(html, "toc_html", ""),
    }


def get_work_projects():
    return getattr(config, "WORK_PROJECTS", [])


@app.context_processor
def inject_globals():
    return {
        "config": config,
        "current_year": datetime.now().year,
        "nav_links": [
            ("Home", "/"),
            ("Projects", "/projects/"),
            ("Blog", "/blog/"),
            ("About", "/about/"),
        ],
    }


@app.route("/")
def index():
    data = fetch_github_data()
    repos = process_repos(data["repos"])
    featured = [r for r in repos if r["name"] in config.PINNED_REPOS] or repos[:6]
    lang_stats = get_language_stats(data["repos"])
    total_stars = sum(r.get("stargazers_count", 0) for r in data["repos"])
    total_forks = sum(r.get("forks_count", 0) for r in data["repos"])
    posts = get_blog_posts()[:3]
    work_projects = get_work_projects()
    return render_template(
        "index.html",
        repos=featured,
        lang_stats=lang_stats,
        total_stars=total_stars,
        total_forks=total_forks,
        total_repos=len(data["repos"]),
        user=data.get("user", {}),
        posts=posts,
        work_projects=work_projects,
    )


@app.route("/projects/")
def projects():
    data = fetch_github_data()
    repos = process_repos(data["repos"])
    languages = sorted(set(r["language"] for r in repos if r.get("language")))
    work_projects = get_work_projects()
    return render_template("projects.html", repos=repos, languages=languages, work_projects=work_projects)


@app.route("/work/<slug>/")
def work_detail(slug):
    wp = next((p for p in get_work_projects() if p["slug"] == slug), None)
    if not wp:
        abort(404)
    return render_template("work_detail.html", project=wp)


@app.route("/projects/<slug>/")
def project_detail(slug):
    data = fetch_github_data()
    repo = next((r for r in data["repos"] if r["name"] == slug), None)
    if not repo:
        abort(404)

    readme_html = ""
    try:
        headers = {"Accept": "application/vnd.github.v3+json"}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"
        resp = requests.get(
            f"https://api.github.com/repos/{config.GITHUB_USERNAME}/{slug}/readme",
            headers=headers,
            timeout=10,
        )
        if resp.ok:
            import base64
            content = base64.b64decode(resp.json()["content"]).decode("utf-8")
            readme_html = markdown2.markdown(
                content,
                extras=["fenced-code-blocks", "tables", "strike"],
            )
    except Exception:
        pass

    return render_template("project_detail.html", repo=repo, readme_html=readme_html)


@app.route("/blog/")
def blog():
    posts = get_blog_posts()
    all_tags = sorted(set(tag for p in posts for tag in p["tags"]))
    return render_template("blog.html", posts=posts, all_tags=all_tags)


@app.route("/blog/<slug>/")
def blog_post(slug):
    post = render_blog_post(slug)
    if not post:
        abort(404)
    posts = get_blog_posts()
    related = [p for p in posts if p["slug"] != slug and set(p["tags"]) & set(post["tags"])][:3]
    return render_template("blog_post.html", post=post, related=related)


@app.route("/about/")
def about():
    certifications = getattr(config, "CERTIFICATIONS", [])
    return render_template("about.html", certifications=certifications)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
