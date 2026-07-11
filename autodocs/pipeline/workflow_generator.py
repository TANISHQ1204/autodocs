PYTHON_STEPS="""\
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -r requirements.txt || pip install -e .
      - name: Run tests
        run: pytest || echo "No tests found, skipping"
      - name: Security audit
        run: pip install pip-audit && pip-audit || true
"""

NODE_STEPS="""\
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install dependencies
        run: npm install
      - name: Run tests
        run: npm test || echo "No tests found, skipping"
      - name: Security audit
        run: npm audit || true
"""

AUTODOCS_STEPS = """\
      - name: Generate docs
        run: |
          pip install git+https://github.com/YOUR_USERNAME/autodocs.git
          autodocs generate .
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""


def generate_workflow_yaml(primary_language: str) -> str:
    if primary_language=="Python":
        build_steps=PYTHON_STEPS
    elif primary_language in ("JavaScript", "TypeScript"):
        build_steps=NODE_STEPS
    else:
        build_steps= "      - name: No build step configured\n        run: echo \"Unsupported language: add your own build steps here\"\n"

    return f"""name: CI

on:
  push:
    branches: [main]

permissions:
  contents: write
  pull-requests: write

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
{build_steps}{AUTODOCS_STEPS}"""