from git import Repo
import os
import sys


def get_git_root(path):
    git_repo = Repo(path, search_parent_directories=True)
    return git_repo.git.rev_parse("--show-toplevel")


def add_to_sys_path(local_repo_folder="nbs"):
    project_root = get_git_root(local_repo_folder)
    sys.path.append(os.path.abspath(os.path.join(project_root, local_repo_folder)))
