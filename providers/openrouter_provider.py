import json
import httpx
from .base import BaseProvider


class OpenRouterProvider(BaseProvider):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "openrouter"
        self.base_url = "https://openrouter.ai/api/v1"
        self.supports_thinking = False
        self.supports_tool_calling = True
        self.default_model = "google/gemini-2.5-flash"

    async def validate(self) -> bool:
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set")
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            if r.status_code != 200:
                raise ValueError(f"Invalid OpenRouter key: {r.status_code}")
            return True

    async def stream(self, messages, tools=None, model=None, temperature=0.7, max_tokens=8000, thinking="off"):
        model = model or self.default_model
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        tool_buffer = {}
        full_content = ""

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://xyroncodex.dev",
                    "X-Title": "Xyron Codex",
                },
                json=payload,
                timeout=120,
            ) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    yield {"type": "text", "content": f"\nOpenRouter Error {resp.status_code}: {body.decode()}"}
                    return

                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                    except Exception:
                        continue

                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    if delta.get("content"):
                        full_content += delta["content"]
                        yield {"type": "text", "content": delta["content"]}
                    if delta.get("tool_calls"):
                        for tc in delta["tool_calls"]:
                            idx = tc.get("index", 0)
                            if idx not in tool_buffer:
                                tool_buffer[idx] = {"id": tc.get("id", ""), "type": "function", "function": {"name": "", "arguments": ""}}
                            if tc.get("function", {}).get("name"):
                                tool_buffer[idx]["function"]["name"] += tc["function"]["name"]
                            if tc.get("function", {}).get("arguments"):
                                tool_buffer[idx]["function"]["arguments"] += tc["function"]["arguments"]

        final_tools = [v for v in tool_buffer.values() if v["function"]["name"]]
        if final_tools:
            yield {"type": "tool_calls", "content": final_tools, "full_content": full_content}

    async def list_models(self) -> list:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10,
                )
                data = r.json()
                return [{"id": m["id"], "owned_by": m.get("owned_by", "openrouter"), "context_window": m.get("context_length")} for m in data.get("data", [])]
        except Exception:
            return [{"id": m, "owned_by": "openrouter", "context_window": None} for m in self.get_recommended_models()]

    def get_recommended_models(self) -> list:
        return [
            "google/gemini-2.5-flash",
            "google/gemini-2.5-pro",
            "anthropic/claude-sonnet-4-5",
            "deepseek/deepseek-r1",
            "meta-llama/llama-3.3-70b-instruct",
            "qwen/qwen3-235b-a22b",
        ]

    def get_system_prompt_appendix(self) -> str:
        return "\n## OPENROUTER\n500+ models via one key. Model routing active."
