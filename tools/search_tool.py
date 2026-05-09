import subprocess

search_tools = [
    {
        "type": "function",
        "function": {
            "name": "search_codebase",
            "description": "Search for a regex pattern in files (grep)",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern":      {"type": "string"},
                    "file_pattern": {"type": "string", "description": "Glob like *.py"},
                    "path":         {"type": "string", "default": "."},
                },
                "required": ["pattern"],
            },
        },
    },
]

async def handle_search_tool(args: dict) -> str:
    pattern = args.get("pattern", "")
    file_pat = args.get("file_pattern", "*")
    directory = args.get("path", ".")

    if not isinstance(pattern, str) or len(pattern) > 500:
        return "Error: invalid pattern"

    result = subprocess.run(
        ["grep", "-rn", f"--include={file_pat}", pattern, directory],
        capture_output=True,
        text=True,
        timeout=10,
    )

    if result.returncode == 1:
        return "No matches found"
    if result.returncode != 0:
        return f"grep exited with code {result.returncode}"

    return (result.stdout or "No matches found")[:10000]
