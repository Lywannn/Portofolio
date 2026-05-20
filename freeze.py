from pathlib import Path
from app import app, fetch_github_data, get_blog_posts, get_work_projects
from flask_frozen import Freezer
import config

app.config["FREEZER_DESTINATION"] = "build"
app.config["FREEZER_RELATIVE_URLS"] = True
app.config["FREEZER_IGNORE_MIMETYPE_WARNINGS"] = True

freezer = Freezer(app)


@freezer.register_generator
def project_detail():
    data = fetch_github_data()
    for repo in data["repos"]:
        if repo["name"] not in config.EXCLUDED_REPOS:
            yield {"slug": repo["name"]}


@freezer.register_generator
def blog_post():
    for post in get_blog_posts():
        yield {"slug": post["slug"]}


@freezer.register_generator
def work_detail():
    for wp in get_work_projects():
        yield {"slug": wp["slug"]}


if __name__ == "__main__":
    print("Freezing Flask app to static files...")
    freezer.freeze()
    print(f"Done! Static files generated in: {Path('build').resolve()}")
