import asyncio
import re

shell_tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Run a shell command in the project directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "workdir": {"type": "string", "description": "Working directory (relative to project root)"},
                },
                "required": ["command"],
            },
        },
    },
]

BLOCKED_PATTERNS = [
    re.compile(r'rm\s+-rf\s+/'),
    re.compile(r'sudo\s+rm'),
    re.compile(r'mkfs'),
    re.compile(r'dd\s+if='),
    re.compile(r'>\s*/dev/sd'),
    re.compile(r':\s*\(\s*\)\s*\{'),
    re.compile(r'chmod\s+[0-7]*7\s+/'),
    re.compile(r'curl[^|]+\|\s*(ba)?sh'),
    re.compile(r'wget[^|]+\|\s*(ba)?sh'),
]

async def handle_shell_tool(args: dict, context: dict) -> str:
    import os
    cmd = args.get("command", "")
    cwd = context.get("cwd", os.getcwd())
    if args.get("workdir"):
        cwd = os.path.join(cwd, args["workdir"])

    for pat in BLOCKED_PATTERNS:
        if pat.search(cmd):
            return f"Command blocked (dangerous pattern): {cmd}"

    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
        out = stdout.decode(errors="replace")
        err = stderr.decode(errors="replace")
        return out or err or "(no output)"
    except asyncio.TimeoutError:
        return "Command timed out after 30s"
    except Exception as e:
        return f"Error: {e}"
