# AutoDocs

AutoDocs automatically keeps your project's documentation up to date. On every push to `main`, it:

- Scans your repository (languages, frameworks, entry points, dependencies)
- Extracts functions, call graphs, and API routes (Flask/FastAPI, Python only for now)
- Generates an architecture diagram (Mermaid)
- Writes `README.md` — updating only its own generated sections, never touching content you wrote yourself
- Commits the changes to a dedicated branch, opens a pull request, and auto-merges it if there are no conflicts

You add one small workflow file to your project. Everything else happens automatically.

---

## Quick start

### 1. Add the workflow file

In your project, create `.github/workflows/docs.yml`:

```yaml
name: Docs

on:
  push:
    branches: [main]

jobs:
  docs:
    uses: TANISHQ1204/autodocs/.github/workflows/autodocs.yml@main
    secrets:
      github-token: ${{ secrets.GITHUB_TOKEN }}
    permissions:
      contents: write
      pull-requests: write
```

If your project already has a workflow file, don't edit it — just add this as a **new**, separate file (e.g. `docs.yml`) alongside it. Multiple workflow files run independently with no conflict.

### 2. Enable one repository setting (required, one-time)

GitHub blocks Actions from creating pull requests by default. You need to turn this on once, per repository:

1. Go to your repository → **Settings** → **Actions** → **General**
2. Scroll to **Workflow permissions**
3. Select **"Read and write permissions"**
4. Check **"Allow GitHub Actions to create and approve pull requests"**
5. Click **Save**

Without this step, AutoDocs will fail with a `403 Forbidden` error when it tries to open a pull request.

### 3. Push

```bash
git add .github/workflows/docs.yml
git commit -m "add autodocs"
git push
```

Check the **Actions** tab on GitHub — you should see a "Docs" workflow run. Once it completes, check the **Pull requests** tab: if the update applied cleanly, it's already merged into `main`. If there was a conflict, the PR is left open for you to review and merge manually.

---

## Important: pulling after AutoDocs runs

AutoDocs commits its changes to a separate branch (`autodocs/docs-update`) and merges that branch into `main` through a pull request — it never pushes directly to your local checkout.

This means: **after AutoDocs merges a docs update, your local `main` is behind the remote `main`.** If you keep working locally and then try to push, git will reject the push until you pull first. This is normal git behavior, not a bug — the same thing happens any time a teammate pushes to a shared branch while you're working.

Before your next push, run:

```bash
git pull origin main
```

If you use `git pull` on a branch with a different default merge strategy (e.g. rebase), that works too:

```bash
git pull --rebase origin main
```

Either way, this is a one-time step before your *next* push after AutoDocs has run — not something that blocks or breaks your existing work.

---

## What gets generated

AutoDocs writes three sections into `README.md`, each wrapped in HTML comment markers:

```markdown
<!-- AUTODOCS:OVERVIEW:START -->
...
<!-- AUTODOCS:OVERVIEW:END -->

<!-- AUTODOCS:API:START -->
...
<!-- AUTODOCS:API:END -->

<!-- AUTODOCS:ARCHITECTURE:START -->
...
<!-- AUTODOCS:ARCHITECTURE:END -->
```

Only the content *between* these markers is regenerated on each run. Anything you write outside them — a hand-written introduction, a license section, contributing guidelines — is never touched or overwritten.

If your project doesn't have a `README.md` yet, AutoDocs creates one automatically on the first run.

---

## Requirements

- Your project's default branch is `main` (or set `base_branch` in `.autodocs.yml` if different)
- Python-based projects are supported today (Flask/FastAPI route detection, Python call-graph analysis). JavaScript/TypeScript support is planned.
- No API keys required — AutoDocs only uses the `GITHUB_TOKEN` GitHub provides automatically to every workflow run.

---

## How it works, briefly

1. **Scan** — walks the repository, detects languages, frameworks, entry points, and dependencies.
2. **Analyze** — parses Python files to extract functions, an internal call graph, and API routes.
3. **Diagram** — builds a Mermaid diagram from the call graph and routes.
4. **Render** — turns the scan results into Markdown sections.
5. **Write** — inserts or updates those sections in `README.md`, preserving everything else.
6. **Commit safely** — pushes to a dedicated bot branch, retrying automatically if another push landed at the same time.
7. **Open a PR** — and auto-merges it if there's no conflict with `main`; otherwise leaves it for manual review.
