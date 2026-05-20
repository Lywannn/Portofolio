---
title: "How to Make Your First Open Source Contribution"
date: 2025-03-20
tags: ["Open Source", "Git", "GitHub", "Career"]
excerpt: "Contributing to open source can feel intimidating at first. This guide breaks it down into simple, actionable steps that anyone can follow — even on your very first day."
cover_image: ""
---

## Why Contribute to Open Source?

- Learn from experienced developers
- Build a public portfolio
- Give back to tools you use
- Make connections in the community

## Step 1: Find the Right Project

Start small. Look for repositories with:

- A `good first issue` or `beginner friendly` label
- Active maintainers who respond to PRs
- A clear `CONTRIBUTING.md` file
- A codebase in a language you know

Good places to look:
- GitHub Explore
- `goodfirstissue.dev`
- `up-for-grabs.net`

## Step 2: Fork & Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR-USERNAME/project-name.git
cd project-name

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL-OWNER/project-name.git
```

## Step 3: Create a Branch

```bash
git checkout -b fix/typo-in-readme
```

Always work on a feature branch, never on `main`.

## Step 4: Make Your Changes

Fix the issue. Keep your changes focused and minimal. Don't refactor unrelated code.

## Step 5: Commit with a Good Message

```bash
git add README.md
git commit -m "fix: correct typo in installation section"
```

Good commit messages use the imperative mood: "fix", "add", "update", not "fixed", "added".

## Step 6: Push & Open a PR

```bash
git push origin fix/typo-in-readme
```

Then go to GitHub and open a Pull Request. In your PR description:

- Explain **what** you changed
- Explain **why**
- Reference the issue: `Closes #42`

## Tips for a Good First PR

1. **Start with documentation** — typos, unclear wording, missing examples
2. **Be patient** — maintainers are often volunteers
3. **Accept feedback gracefully** — it's about the code, not you
4. **Keep it small** — one focused change per PR

## What Counts as a Contribution?

- Bug fixes
- Documentation improvements
- Test coverage
- Translations
- Issue triage
- Reviewing other PRs

Your first contribution doesn't have to be a major feature. A single typo fix is a real, valuable contribution. Start there.
