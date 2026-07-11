import subprocess
import time

BOT_BRANCH="autodocs/docs-update"
BOT_NAME="autodocs-bot"
BOT_EMAIL="autodocs-bot@users.noreply.github.com"

def _run(command:list)->subprocess.CompletedProcess:
    return subprocess.run(command,check=True,capture_output=True,text=True,encoding="utf-8")

def commit_and_push_docs_safely(repo_path:str,changed_files:list,max_retries:int=3)->bool:
    for attempt in range(1,max_retries+1):
        _run(["git", "-C", repo_path, "config", "user.name", BOT_NAME])
        _run(["git", "-C", repo_path, "config", "user.email", BOT_EMAIL])
        _run(["git", "-C", repo_path, "fetch", "origin"])

        try:
            _run(["git", "-C", repo_path, "checkout", "-B", BOT_BRANCH, f"origin/{BOT_BRANCH}"])
        except subprocess.CalledProcessError:
            _run(["git", "-C", repo_path, "checkout", "-B", BOT_BRANCH])

        _run(["git", "-C", repo_path, "add"]+changed_files)
        status = _run(["git", "-C", repo_path, "status", "--porcelain"])
        if not status.stdout.strip():
            return False

        _run([
            "git", "-C", repo_path, "commit",
            "-m", "docs: update README, API docs, and architecture diagram [skip ci]"
        ])

        try:
            _run(["git", "-C", repo_path, "push", "origin", BOT_BRANCH])
            return True
        except subprocess.CalledProcessError:
            if attempt==max_retries:
                raise
            time.sleep(2 * attempt)   
            continue

    return False

