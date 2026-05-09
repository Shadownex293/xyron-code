import json
from .file_ops import file_tools as FILE_TOOLS, handle_file_tool
from .shell_tool import shell_tools as SHELL_TOOLS, handle_shell_tool
from .search_tool import search_tools as SEARCH_TOOLS, handle_search_tool
from .web_fetch import web_fetch_tools as WEB_TOOLS, handle_web_fetch_tool

ALL_TOOLS = [*FILE_TOOLS, *SHELL_TOOLS, *SEARCH_TOOLS, *WEB_TOOLS]


async def execute_tool(tool_call: dict, context: dict) -> str:
    name = tool_call["function"]["name"]
    try:
        args = json.loads(tool_call["function"].get("arguments", "{}"))
    except Exception as e:
        return f"Error: Invalid JSON arguments: {e}"

    try:
        if name in ("read_file", "write_file", "list_directory"):
            return await handle_file_tool(name, args, context)
        if name == "execute_command":
            return await handle_shell_tool(args, context)
        if name == "search_codebase":
            return await handle_search_tool(args)
        if name in ("web_search", "web_fetch"):
            return await handle_web_fetch_tool(name, args)
        return f"Unknown tool: {name}"
    except Exception as e:
        return f"Tool execution error: {e}"
