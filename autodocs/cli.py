import click
from .scanner.repo_scanner import RepoScanner
from .diagram.mermaid_builder import build_call_graph_diagram
from .pipeline.workflow_generator import generate_workflow_yaml
from pathlib import Path
from .writer.section_writer import write_sections
from .writer.markdown_templates import render_overview_section, render_api_section
from .gitops.committer import commit_and_push_docs_safely
from .gitops.pull_request import create_or_update_pr, merge_pr_if_clean
from .config import load_config

@click.group()
def main():
    pass

@main.command()
@click.argument("path", default=".")
def generate(path):
    """Run the full AutoDocs pipeline: scan, generate docs, commit, and open/merge a PR."""
    config = load_config(path)

    ignore_dirs = set(RepoScanner("").ignore_dirs) | set(config["extra_ignore_dirs"])
    scanner = RepoScanner(path, ignore_dirs=ignore_dirs)
    result = scanner.scan()
    scan_data = result.to_dict()

    diagram_text = build_call_graph_diagram(scan_data["functions"], scan_data["routes"])

    sections = {
        "OVERVIEW": render_overview_section(scan_data),
        "API": render_api_section(scan_data["routes"]),
        "ARCHITECTURE": "```mermaid\n" + diagram_text + "\n```",
    }

    readme_path = Path(path) / "README.md"
    write_sections(readme_path, sections)
    click.echo("README.md updated.")

    pushed = commit_and_push_docs_safely(path, ["README.md"])
    if not pushed:
        click.echo("No changes to commit. Done.")
        return

    pr = create_or_update_pr(base_branch=config["base_branch"], head_branch="autodocs/docs-update")
    click.echo(f"PR: {pr['html_url']}")

    result_status = merge_pr_if_clean(pr["number"])
    click.echo(f"Merge result: {result_status}")

@main.command()
@click.argument("path",default=".")
def scan(path):
    scanner=RepoScanner(path)
    result=scanner.scan()
    click.echo(result.to_json())

@main.command()
@click.argument("path",default=".")
def diagram(path):
    scanner=RepoScanner(path)
    result=scanner.scan()
    output=build_call_graph_diagram(result.funtions,result.routes)

    click.echo("```mermaid")
    click.echo(output)
    click.echo("```")

@main.command()
@click.argument("path", default=".")
def init_pipeline(path):
    scanner=RepoScanner(path)
    result=scanner.scan()
    yaml_content=generate_workflow_yaml(result.primary_language)
    workflow_dir=Path(path) / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    output_path = workflow_dir / "ci.yml"
    output_path.write_text(yaml_content, encoding="utf-8")
    click.echo(f"Created {output_path}")
    click.echo("Remember: add an ANTHROPIC_API_KEY or GEMINI_API_KEY secret if you enable LLM features later.")

if __name__=="__main__":
    main()