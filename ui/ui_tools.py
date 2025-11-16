from git import Repo
from git.exc import InvalidGitRepositoryError
import os
import sys


def get_git_root(path):
    """Get the git repository root, or fallback to parent directory if not in a git repo (e.g., Docker)."""
    try:
        git_repo = Repo(path, search_parent_directories=True)
        return git_repo.git.rev_parse("--show-toplevel")
    except InvalidGitRepositoryError:
        # Not in a git repository (e.g., running in Docker)
        # Assume we're in /app and the nbs folder is at /app/nbs
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up from /app/ui to /app
        return os.path.dirname(current_dir)


def add_to_sys_path(local_repo_folder="nbs"):
    project_root = get_git_root(local_repo_folder)
    sys.path.append(os.path.abspath(os.path.join(project_root, local_repo_folder)))
