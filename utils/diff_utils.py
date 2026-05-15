import difflib
import os


def make_diff(old_content, new_content, filename="file"):
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    diff = list(difflib.unified_diff(old_lines, new_lines, fromfile=f"a/{filename}", tofile=f"b/{filename}", lineterm=""))
    return "\n".join(diff)


def print_diff(diff_text):
    if not diff_text.strip():
        print("  (no changes)")
        return
    for line in diff_text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            print(f"\033[32m{line}\033[0m")
        elif line.startswith("-") and not line.startswith("---"):
            print(f"\033[31m{line}\033[0m")
        elif line.startswith("@@"):
            print(f"\033[36m{line}\033[0m")
        else:
            print(f"\033[2m{line}\033[0m")


def confirm_apply(automode=False):
    if automode:
        return True
    try:
        ans = input("\n  Apply? [Y/n] ").strip().lower()
        return ans in ("", "y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False
