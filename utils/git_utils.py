import subprocess
import os


def _run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

def is_git_repo(cwd):
    code, _, _ = _run(["git", "rev-parse", "--is-inside-work-tree"], cwd)
    return code == 0

def git_status(cwd):
    _, out, _ = _run(["git", "status", "--short"], cwd)
    return out

def git_add_commit(filepath, message, cwd):
    _run(["git", "add", filepath], cwd)
    code, out, err = _run(["git", "commit", "-m", message], cwd)
    return code == 0, out or err

def git_log(cwd, n=5):
    _, out, _ = _run(["git", "log", f"-{n}", "--oneline"], cwd)
    return out

def git_diff_file(filepath, cwd):
    _, out, _ = _run(["git", "diff", "HEAD", "--", filepath], cwd)
    return out
