from autodocs.gitops.committer import commit_and_push_docs_safely
from autodocs.gitops.pull_request import create_or_update_pr, merge_pr_if_clean

REPO_PATH = r"C:\Users\Tanishk Rastogi\Downloads\AutoDocs\autodocs-test-local"  

# simulate a doc change
with open(REPO_PATH + r"\README.md", "a", encoding="utf-8") as f:
    f.write("\n<!-- AUTODOCS:OVERVIEW:START -->\nTest content\n<!-- AUTODOCS:OVERVIEW:END -->\n")

pushed = commit_and_push_docs_safely(REPO_PATH, ["README.md"])
print("Pushed:", pushed)

if pushed:
    pr = create_or_update_pr(base_branch="main", head_branch="autodocs/docs-update")
    print("PR number:", pr["number"], "URL:", pr["html_url"])

    result = merge_pr_if_clean(pr["number"])
    print("Merge result:", result)