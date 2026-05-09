import os
import httpx

TAVILY_BASE = "https://api.tavily.com"

web_fetch_tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for up-to-date information using Tavily. Use for current news, docs, recent releases, or anything post-training.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query":          {"type": "string"},
                    "search_depth":   {"type": "string", "enum": ["basic", "advanced"]},
                    "max_results":    {"type": "integer", "minimum": 1, "maximum": 10},
                    "include_answer": {"type": "boolean"},
                    "include_domains":{"type": "array", "items": {"type": "string"}},
                    "exclude_domains":{"type": "array", "items": {"type": "string"}},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Fetch clean text from URLs using Tavily Extract. Up to 20 URLs per call.",
            "parameters": {
                "type": "object",
                "properties": {
                    "urls":          {"type": "array", "items": {"type": "string"}, "maxItems": 20},
                    "extract_depth": {"type": "string", "enum": ["basic", "advanced"]},
                },
                "required": ["urls"],
            },
        },
    },
]

async def handle_web_fetch_tool(name: str, args: dict) -> str:
    api_key = os.environ.get("TAVILY_API_KEY", "")
    if not api_key:
        return (
            "Error: TAVILY_API_KEY not set.\n"
            "Add to .env: TAVILY_API_KEY=tvly-...\n"
            "Free key (1000 searches/month): https://app.tavily.com"
        )
    try:
        if name == "web_search":
            return await _search(api_key, args)
        if name == "web_fetch":
            return await _extract(api_key, args)
        return f"Unknown web tool: {name}"
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return "Error: Invalid Tavily API key."
        if e.response.status_code == 429:
            return "Error: Tavily rate limit hit. Free = 1000/month."
        return f"Web tool error: {e}"
    except Exception as e:
        return f"Web tool error: {e}"

async def _search(api_key: str, args: dict) -> str:
    query = args.get("query", "").strip()
    if not query:
        return "Error: query must be non-empty"
    if len(query) > 400:
        return "Error: query too long (max 400 chars)"

    body = {
        "api_key": api_key,
        "query": query,
        "search_depth": args.get("search_depth", "basic"),
        "max_results": min(max(1, args.get("max_results", 5)), 10),
        "include_answer": args.get("include_answer", False),
        "include_raw_content": False,
    }
    if args.get("include_domains"):
        body["include_domains"] = args["include_domains"]
    if args.get("exclude_domains"):
        body["exclude_domains"] = args["exclude_domains"]

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{TAVILY_BASE}/search", json=body)
        r.raise_for_status()
        data = r.json()

    if not data.get("results"):
        return f'No results for: "{query}"'

    lines = []
    if args.get("include_answer") and data.get("answer"):
        lines.append(f"## Answer\n{data['answer']}\n")
    lines.append(f"## Search Results ({len(data['results'])}) — \"{query}\"\n")
    for i, res in enumerate(data["results"]):
        lines.append(f"### {i+1}. {res.get('title', 'Untitled')}")
        lines.append(f"URL: {res.get('url', '')}")
        if res.get("published_date"):
            lines.append(f"Date: {res['published_date']}")
        if res.get("content"):
            snippet = res["content"][:800] + "..." if len(res["content"]) > 800 else res["content"]
            lines.append(f"\n{snippet}")
        lines.append("")
    return "\n".join(lines)

async def _extract(api_key: str, args: dict) -> str:
    urls = args.get("urls", [])
    if not urls:
        return "Error: urls must be non-empty array"
    valid = []
    for u in urls[:20]:
        try:
            from urllib.parse import urlparse
            p = urlparse(u)
            if p.scheme and p.netloc:
                valid.append(u)
        except Exception:
            pass
    if not valid:
        return "Error: no valid URLs"

    body = {"api_key": api_key, "urls": valid, "extract_depth": args.get("extract_depth", "basic")}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{TAVILY_BASE}/extract", json=body)
        r.raise_for_status()
        data = r.json()

    lines = []
    for res in data.get("results", []):
        lines.append(f"## {res.get('url', '')}\n")
        content = res.get("raw_content", "")
        if content:
            lines.append(content[:4000] + "\n\n[... truncated ...]" if len(content) > 4000 else content)
        else:
            lines.append("(no content extracted)")
        lines.append("\n---\n")
    for f in data.get("failed_results", []):
        lines.append(f"- {f.get('url', '')}: {f.get('error', 'failed')}")

    return "\n".join(lines) if lines else "No content extracted."
