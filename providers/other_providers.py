import json
import httpx
from .base import BaseProvider


class _OpenAICompatProvider(BaseProvider):

    async def validate(self) -> bool:
        if not self.api_key:
            raise ValueError(f"{self.name.upper()}_API_KEY not set")
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base_url}/models",
                headers=self._headers(),
                timeout=10,
            )
            if r.status_code != 200:
                raise ValueError(f"Auth failed for {self.name}: {r.status_code}")
            return True

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def stream(self, messages, tools=None, model=None, temperature=0.7, max_tokens=8000, thinking="off"):
        model = model or self.default_model
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if tools and self.supports_tool_calling:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        tool_buffer  = {}
        full_content = ""

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
                timeout=120,
            ) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    yield {"type": "text", "content": f"\n{self.name} Error {resp.status_code}: {body.decode()[:200]}"}
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
                r = await client.get(f"{self.base_url}/models", headers=self._headers(), timeout=10)
                data = r.json()
                return [{"id": m["id"], "owned_by": m.get("owned_by", self.name), "context_window": m.get("context_window")} for m in data.get("data", [])]
        except Exception:
            return [{"id": m, "owned_by": self.name, "context_window": None} for m in self.get_recommended_models()]


class GeminiProvider(_OpenAICompatProvider):
    def __init__(self, config):
        super().__init__(config)
        self.name              = "gemini"
        self.base_url          = "https://generativelanguage.googleapis.com/v1beta/openai"
        self.supports_tool_calling = True
        self.default_model     = "gemini-2.5-flash"

    def get_recommended_models(self):
        return ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]

    def get_system_prompt_appendix(self):
        return "\n## GEMINI\nGoogle AI. 1M context. Free: 1500 req/day."


class NvidiaProvider(_OpenAICompatProvider):
    def __init__(self, config):
        super().__init__(config)
        self.name              = "nvidia"
        self.base_url          = "https://integrate.api.nvidia.com/v1"
        self.supports_tool_calling = True
        self.default_model     = "meta/llama-3.3-70b-instruct"

    def get_recommended_models(self):
        return [
            "meta/llama-3.3-70b-instruct",
            "nvidia/llama-3.1-nemotron-ultra-253b-v1",
            "qwen/qwen3-235b-a22b-instruct-fp8",
            "deepseek-ai/deepseek-r1",
        ]

    def get_system_prompt_appendix(self):
        return "\n## NVIDIA NIM\nNIM serverless inference. Free credits on build.nvidia.com."


class CerebrasProvider(_OpenAICompatProvider):
    def __init__(self, config):
        super().__init__(config)
        self.name              = "cerebras"
        self.base_url          = "https://api.cerebras.ai/v1"
        self.supports_tool_calling = True
        self.default_model     = "llama-3.3-70b"

    def get_recommended_models(self):
        return ["llama-3.3-70b", "llama-3.1-8b", "qwen-3-32b"]

    def get_system_prompt_appendix(self):
        return "\n## CEREBRAS\nWSE inference. 1M tokens/day free. Ultra-fast."


class MistralProvider(_OpenAICompatProvider):
    def __init__(self, config):
        super().__init__(config)
        self.name              = "mistral"
        self.base_url          = "https://api.mistral.ai/v1"
        self.supports_tool_calling = True
        self.default_model     = "mistral-large-latest"

    def get_recommended_models(self):
        return ["mistral-large-latest", "devstral-latest", "codestral-latest", "mistral-small-latest"]

    def get_system_prompt_appendix(self):
        return "\n## MISTRAL\n1B tokens/month free. Codestral best for code."


class XAIProvider(_OpenAICompatProvider):
    def __init__(self, config):
        super().__init__(config)
        self.name              = "xai"
        self.base_url          = "https://api.x.ai/v1"
        self.supports_tool_calling = True
        self.default_model     = "grok-3-mini"

    def get_recommended_models(self):
        return ["grok-3-mini", "grok-3", "grok-3-mini-fast"]

    def get_system_prompt_appendix(self):
        return "\n## XAI\nGrok models. $25 signup credits."


class SambanovaProvider(_OpenAICompatProvider):
    def __init__(self, config):
        super().__init__(config)
        self.name              = "sambanova"
        self.base_url          = "https://api.sambanova.ai/v1"
        self.supports_tool_calling = True
        self.default_model     = "Meta-Llama-3.3-70B-Instruct"

    def get_recommended_models(self):
        return ["Meta-Llama-3.3-70B-Instruct", "Meta-Llama-3.1-405B-Instruct", "DeepSeek-R1-Distill-Llama-70B"]

    def get_system_prompt_appendix(self):
        return "\n## SAMBANOVA\nRDU hardware. Fast free tier."


class TogetherProvider(_OpenAICompatProvider):
    def __init__(self, config):
        super().__init__(config)
        self.name              = "together"
        self.base_url          = "https://api.together.xyz/v1"
        self.supports_tool_calling = True
        self.default_model     = "meta-llama/Meta-Llama-3.3-70B-Instruct-Turbo"

    def get_recommended_models(self):
        return [
            "meta-llama/Meta-Llama-3.3-70B-Instruct-Turbo",
            "deepseek-ai/DeepSeek-R1",
            "Qwen/Qwen3-235B-A22B-fp8-tput",
        ]

    def get_system_prompt_appendix(self):
        return "\n## TOGETHER\n~$100 signup credits. Largest OSS model catalog."


class KimiProvider(_OpenAICompatProvider):
    def __init__(self, config):
        super().__init__(config)
        self.name              = "kimi"
        self.base_url          = "https://api.moonshot.ai/v1"
        self.supports_tool_calling = True
        self.default_model     = "kimi-k2-0711-preview"

    def get_recommended_models(self):
        return ["kimi-k2-0711-preview", "moonshot-v1-128k", "moonshot-v1-8k"]

    def get_system_prompt_appendix(self):
        return "\n## KIMI\nMoonshot AI. Trial credits available."


class QwenProvider(_OpenAICompatProvider):
    def __init__(self, config):
        super().__init__(config)
        self.name              = "qwen"
        region                 = config.get("qwen_region", "sg")
        self.base_url          = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1" if region != "cn" else "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.supports_tool_calling = True
        self.default_model     = "qwen3-235b-a22b"

    def get_recommended_models(self):
        return ["qwen3-235b-a22b", "qwen3-72b", "qwen-coder-plus-latest"]

    def get_system_prompt_appendix(self):
        return "\n## QWEN\nAlibaba DashScope. Trial credits."


class MinimaxProvider(_OpenAICompatProvider):
    def __init__(self, config):
        super().__init__(config)
        self.name              = "minimax"
        self.base_url          = "https://api.minimax.chat/v1"
        self.supports_tool_calling = True
        self.default_model     = "MiniMax-Text-01"

    def get_recommended_models(self):
        return ["MiniMax-Text-01", "MiniMax-M1"]

    def get_system_prompt_appendix(self):
        return "\n## MINIMAX\nMiniMax AI. Trial credits."


class DeepSeekProvider(_OpenAICompatProvider):
    def __init__(self, config):
        super().__init__(config)
        self.name              = "deepseek"
        self.base_url          = "https://api.deepseek.com/v1"
        self.supports_tool_calling = True
        self.default_model     = "deepseek-chat"

    def get_recommended_models(self):
        return ["deepseek-chat", "deepseek-reasoner"]

    def get_system_prompt_appendix(self):
        return "\n## DEEPSEEK\nDeepSeek AI. deepseek-chat = V3, deepseek-reasoner = R1. Sangat murah."
