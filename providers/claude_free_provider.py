import json
import httpx
from .base import BaseProvider

CLAUDE_FREE_BASE_URL = "https://xyron-rest-api.vercel.app/ai/claude"

_MAX_CTX_PER_MSG  = 2000
_MAX_HISTORY_MSGS = 30


class ClaudeFreeProvider(BaseProvider):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name                  = "claude-free"
        self.base_url              = CLAUDE_FREE_BASE_URL
        self.supports_thinking     = False
        self.supports_tool_calling = False
        self.default_model         = "claude-free"
        self.api_key               = ""

    def _extract_text(self, content) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, dict):
            return (
                content.get("text")
                or content.get("content")
                or json.dumps(content)
            )
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    t = item.get("text") or item.get("content") or ""
                    if t:
                        parts.append(str(t))
            return " ".join(parts)
        return str(content)

    def _build_prompt(self, messages: list) -> str:
        parts          = []
        system_content = ""
        chat_msgs      = []

        for m in messages:
            role = m.get("role", "")
            if role == "system":
                system_content = self._extract_text(m.get("content"))
            else:
                chat_msgs.append(m)

        if system_content:
            parts.append(f"[System]\n{system_content[:3000]}\n")

        trimmed = chat_msgs[-_MAX_HISTORY_MSGS:]

        for m in trimmed:
            role    = m.get("role", "")
            content = self._extract_text(m.get("content"))
            content = content[:_MAX_CTX_PER_MSG]

            if role == "user":
                parts.append(f"[Human]: {content}")
            elif role == "assistant":
                parts.append(f"[AI]: {content}")

        return "\n".join(parts)

    async def validate(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(CLAUDE_FREE_BASE_URL, params={"message": "ping"})
                return r.status_code < 500
        except Exception as e:
            raise ValueError(f"Claude Free API unreachable: {e}")

    async def stream(self, messages, tools=None, model=None, temperature=0.7, max_tokens=8000, thinking="off"):
        prompt = self._build_prompt(messages)

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.get(CLAUDE_FREE_BASE_URL, params={"message": prompt})

                if r.status_code != 200:
                    yield {"type": "text", "content": f"\n[Claude Free Error {r.status_code}]: {r.text[:300]}"}
                    return

                try:
                    data = r.json()
                    if isinstance(data, dict):
                        text = (
                            data.get("result")
                            or data.get("response")
                            or data.get("message")
                            or data.get("text")
                            or data.get("answer")
                            or json.dumps(data)
                        )
                    else:
                        text = str(data)
                except Exception:
                    text = r.text

                text = self._extract_text(text)

                if not text or not text.strip():
                    yield {"type": "text", "content": "[Claude Free]: (empty response)"}
                    return

                chunk_size = 40
                for i in range(0, len(text), chunk_size):
                    yield {"type": "text", "content": text[i: i + chunk_size]}

        except httpx.TimeoutException:
            yield {"type": "text", "content": "\n[Claude Free Error]: Request timeout (60s). Coba lagi."}
        except Exception as e:
            yield {"type": "text", "content": f"\n[Claude Free Error]: {e}"}

    async def list_models(self) -> list:
        return [{"id": "claude-free", "owned_by": "xyron-rest-api", "context_window": 8000}]

    def get_recommended_models(self) -> list:
        return ["claude-free"]

    def get_system_prompt_appendix(self) -> str:
        return (
            "\n## CLAUDE FREE\n"
            "Provider gratis via xyron-rest-api.vercel.app. "
            "Tidak butuh API key. History percakapan tetap terjaga."
        )
