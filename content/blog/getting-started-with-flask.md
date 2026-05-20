---
title: "Getting Started with Flask: Build Your First Web App"
date: 2025-05-01
tags: ["Python", "Flask", "Web Development"]
excerpt: "Flask is a lightweight Python web framework that makes it incredibly easy to build web applications. In this post, we'll walk through creating your first Flask app from scratch."
cover_image: ""
---

## What is Flask?

Flask is a micro web framework for Python. Unlike Django, Flask is minimal by design — it gives you the tools you need without making decisions for you.

## Installation

```bash
pip install flask
```

## Your First App

Create a file called `app.py`:

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Hello, World!</h1>"

if __name__ == "__main__":
    app.run(debug=True)
```

Run it:

```bash
python app.py
```

Open your browser to `http://localhost:5000` and you'll see your first Flask app.

## Adding Templates

Flask uses Jinja2 for templating. Create a `templates/` directory and add `index.html`:

```html
<!DOCTYPE html>
<html>
  <body>
    <h1>Hello, {{ name }}!</h1>
  </body>
</html>
```

Then update your route:

```python
from flask import render_template

@app.route("/")
def home():
    return render_template("index.html", name="World")
```

## What's Next?

- Learn about Flask Blueprints for organizing larger apps
- Explore SQLAlchemy for database integration
- Look into Flask-Login for authentication

Flask's simplicity makes it perfect for APIs, small web apps, and prototypes. Happy coding!
