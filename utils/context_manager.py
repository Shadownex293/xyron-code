import os
import subprocess
from pathlib import Path
from .tokenizer import estimate_tokens


class ContextManager:
    def __init__(self):
        self.max_tokens = 8000
        self.priority_files = ["package.json", "pyproject.toml", "requirements.txt", "README.md", "tsconfig.json"]

    def get_relevant_files(self, user_query: str) -> list:
        files = set()
        cwd = Path.cwd()

        for f in self.priority_files:
            if (cwd / f).exists():
                files.add(f)

        try:
            check = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True, text=True, timeout=3, cwd=str(cwd)
            )
            if check.returncode == 0:
                diff = subprocess.run(
                    ["git", "diff", "--name-only", "HEAD~1"],
                    capture_output=True, text=True, timeout=5, cwd=str(cwd)
                )
                if diff.stdout:
                    for f in diff.stdout.strip().split("\n"):
                        if f:
                            files.add(f)
        except Exception:
            pass

        lower = user_query.lower()
        if any(k in lower for k in ["api", "route", "server", "endpoint"]):
            for pat in ["**/*.py", "**/*.js", "**/*.ts"]:
                try:
                    matched = list(cwd.glob(pat))[:5]
                    for f in matched:
                        if "node_modules" not in str(f) and "__pycache__" not in str(f):
                            files.add(str(f.relative_to(cwd)))
                except Exception:
                    pass

        return list(files)

    def read_files(self, paths: list) -> str:
        content = ""
        tokens_used = 0
        cwd = Path.cwd()

        for file_path in paths:
            p = cwd / file_path if not Path(file_path).is_absolute() else Path(file_path)
            if not p.exists():
                continue
            try:
                file_content = p.read_text(encoding="utf-8", errors="replace")
                ftokens = estimate_tokens(file_content)
                if tokens_used + ftokens > self.max_tokens:
                    content += f'\n<file path="{file_path}" truncated="token_limit" />\n'
                    break
                content += f'\n<file path="{file_path}">\n{file_content}\n</file>'
                tokens_used += ftokens
            except Exception:
                pass

        return content
