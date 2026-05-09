import os
from pathlib import Path

file_tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the full contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to file"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or overwrite a file with new content",
            "parameters": {
                "type": "object",
                "properties": {
                    "path":    {"type": "string"},
                    "content": {"type": "string", "description": "Complete file content"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path":      {"type": "string", "default": "."},
                    "recursive": {"type": "boolean", "default": False},
                },
            },
        },
    },
]

def _assert_safe_path(cwd: str, input_path: str) -> str:
    resolved = os.path.realpath(os.path.join(cwd, input_path))
    cwd_real  = os.path.realpath(cwd)
    rel = os.path.relpath(resolved, cwd_real)
    if rel.startswith("..") or os.path.isabs(rel):
        raise PermissionError(f"Path traversal denied: {input_path}")
    return resolved

async def handle_file_tool(action: str, args: dict, context: dict) -> str:
    cwd = context.get("cwd", os.getcwd())
    safe = _assert_safe_path(cwd, args.get("path", "."))

    if action == "read_file":
        return Path(safe).read_text(encoding="utf-8", errors="replace")

    if action == "write_file":
        Path(safe).parent.mkdir(parents=True, exist_ok=True)
        Path(safe).write_text(args["content"], encoding="utf-8")
        return f"Written: {args['path']} ({len(args['content'])} chars)"

    if action == "list_directory":
        entries = []
        p = Path(safe)
        if args.get("recursive"):
            for item in sorted(p.rglob("*")):
                if "node_modules" in str(item) or ".git" in str(item):
                    continue
                kind = "DIR " if item.is_dir() else "FILE"
                entries.append(f"{kind}  {item.relative_to(p)}")
        else:
            for item in sorted(p.iterdir()):
                kind = "DIR " if item.is_dir() else "FILE"
                entries.append(f"{kind}  {item.name}")
        return "\n".join(entries)

    raise ValueError(f"Unknown file action: {action}")
