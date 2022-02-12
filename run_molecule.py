import os
import sys
from git import Repo

REPO = Repo("./")
GIT = REPO.git


def current_branch() -> str:
    """
    Get current branch
    """
    return GIT.name_rev("--name-only", "HEAD")


def run_test(role) -> int:
    """
    Run test for role
    """
    exit_code = os.system("cd roles/" + role + " && molecule test")

    if not exit_code == 0:
        exit_code = 1
    sys.exit(exit_code)


def evaluate(role) -> None:
    """
    Main func
    """
    if current_branch() == "master":
        run_test(role)
    else:
        print("Not running tests for: " + role)


if __name__ == "__main__":
    evaluate(os.environ["ROLE"])
