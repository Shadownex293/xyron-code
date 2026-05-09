import json
import httpx
from typing import AsyncGenerator
from .base import BaseProvider


class GroqProvider(BaseProvider):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "groq"
        self.base_url = "https://api.groq.com/openai/v1"
        self.supports_thinking = False
        self.supports_tool_calling = True
        self.default_model = "llama-3.3-70b-versatile"

    async def validate(self) -> bool:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set")
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            if r.status_code != 200:
                raise ValueError(f"Invalid Groq API key: {r.status_code}")
            return True

    async def stream(self, messages, tools=None, model=None, temperature=0.7, max_tokens=8000, thinking="off") -> AsyncGenerator:
        model = model or self.default_model
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        tool_supported = any(k in model.lower() for k in ["llama", "qwen", "kimi"])
        if tools and tool_supported:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        tool_buffer = {}
        full_content = ""
        in_think = False

        def strip_think(raw: str) -> str:
            nonlocal in_think
            out = ""
            i = 0
            while i < len(raw):
                if in_think:
                    end = raw.find("</think>", i)
                    if end != -1:
                        in_think = False
                        i = end + 8
                    else:
                        break
                else:
                    start = raw.find("<think>", i)
                    if start != -1:
                        out += raw[i:start]
                        in_think = True
                        i = start + 7
                    else:
                        out += raw[i:]
                        break
            return out

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=120,
            ) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    yield {"type": "text", "content": f"\nGroq Error {resp.status_code}: {body.decode()}"}
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
                        clean = strip_think(delta["content"])
                        if clean:
                            full_content += clean
                            yield {"type": "text", "content": clean}

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
                return [{"id": m["id"], "owned_by": m.get("owned_by", "groq"), "context_window": m.get("context_window")} for m in data.get("data", [])]
        except Exception:
            return [{"id": m, "owned_by": "groq", "context_window": None} for m in self.get_recommended_models()]

    def get_recommended_models(self) -> list:
        return [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "qwen-3-32b",
            "moonshotai/kimi-k2-instruct",
            "meta-llama/llama-4-scout-17b-16e-instruct",
        ]

    def get_system_prompt_appendix(self) -> str:
        return f"\n## GROQ\nLPU inference. Model: {self.default_model}. 128K context."
