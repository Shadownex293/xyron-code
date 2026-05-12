import json
import random
import uuid
import httpx
from .base import BaseProvider

_DEEPAI_URL = "https://api.deepai.org/hacking_is_a_serious_crime"
_REFERER    = "https://deepai.org/chat/claude-3-haiku"
_UA         = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"

_MAX_CTX_PER_MSG  = 2000
_MAX_HISTORY_MSGS = 20

_ANTI_YAPPING = """INSTRUKSI KERAS — WAJIB DIIKUTI:
- Diminta BUAT sesuatu → LANGSUNG TULIS KODENYA, tidak ada kalimat pembuka
- DILARANG: "I am", "I'll help", "Sure!", "Great!", "To confirm", "I understand", "What's the project"
- DILARANG tanya balik kalau permintaan sudah jelas
- Respons HARUS dimulai langsung dengan kode
- Penjelasan taruh sebagai komentar di dalam kode saja
- Kode harus LENGKAP, RUNNABLE, ZERO placeholder
---
"""


def _gen_api_key() -> str:
    r = random.randint(0, int(1e11))
    return f"tryit-{r}-a3edf17b505349f1794bcdbc7290a045"

def _gen_uuid() -> str:
    return str(uuid.uuid4())


class ClaudeFreeProvider(BaseProvider):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name                  = "claude-free"
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
            return content.get("text") or content.get("content") or json.dumps(content)
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

    def _build_history(self, messages: list) -> list:
        system_content = ""
        chat_msgs      = []

        for m in messages:
            role = m.get("role", "")
            if role == "system":
                system_content = self._extract_text(m.get("content"))
            elif role in ("user", "assistant"):
                chat_msgs.append(m)

        history = []
        trimmed = chat_msgs[-_MAX_HISTORY_MSGS:]

        for i, m in enumerate(trimmed):
            role    = m.get("role")
            content = self._extract_text(m.get("content"))[:_MAX_CTX_PER_MSG]

            if role == "user":
                prefix = ""
                if i == 0 and system_content:
                    prefix = _ANTI_YAPPING + f"[Konteks]\n{system_content[:1500]}\n\n"
                elif i == 0:
                    prefix = _ANTI_YAPPING
                history.append({"role": "user", "content": prefix + content})
            elif role == "assistant":
                history.append({"role": "assistant", "content": content})

        if not history:
            history.append({"role": "user", "content": _ANTI_YAPPING + "ping"})

        return history

    async def _scrape(self, messages: list) -> str:
        history      = self._build_history(messages)
        api_key      = _gen_api_key()
        session_uuid = _gen_uuid()

        data = {
            "chat_style":        "claudeai_0",
            "chatHistory":       json.dumps(history),
            "model":             "standard",
            "session_uuid":      session_uuid,
            "hacker_is_stinky":  "very_stinky",
        }

        headers = {
            "api-key":    api_key,
            "user-agent": _UA,
            "referer":    _REFERER,
            "accept":     "*/*",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(_DEEPAI_URL, data=data, headers=headers)
            if r.status_code != 200:
                raise RuntimeError(f"DeepAI error {r.status_code}: {r.text[:200]}")
            try:
                result = r.json()
                if isinstance(result, dict):
                    return (
                        result.get("output")
                        or result.get("result")
                        or result.get("response")
                        or result.get("text")
                        or json.dumps(result)
                    )
                return str(result)
            except Exception:
                return r.text

    async def validate(self) -> bool:
        try:
            text = await self._scrape([{"role": "user", "content": "hi"}])
            return bool(text and len(text) > 0)
        except Exception as e:
            raise ValueError(f"Claude Free (DeepAI) unreachable: {e}")

    async def stream(self, messages, tools=None, model=None, temperature=0.7, max_tokens=8000, thinking="off"):
        try:
            text = await self._scrape(messages)
            text = self._extract_text(text)

            if not text or not text.strip():
                yield {"type": "text", "content": "[Claude Free]: (empty response)"}
                return

            chunk_size = 40
            for i in range(0, len(text), chunk_size):
                yield {"type": "text", "content": text[i: i + chunk_size]}

        except httpx.TimeoutException:
            yield {"type": "text", "content": "\n[Claude Free Error]: Timeout 60s. Coba lagi."}
        except Exception as e:
            yield {"type": "text", "content": f"\n[Claude Free Error]: {e}"}

    async def list_models(self) -> list:
        return [{"id": "claude-free", "owned_by": "deepai-scrape", "context_window": 8000}]

    def get_recommended_models(self) -> list:
        return ["claude-free"]

    def get_system_prompt_appendix(self) -> str:
        return (
            "\n## CLAUDE FREE\n"
            "Claude 3 Haiku via DeepAI scrape. Gratis, tidak butuh API key."
        )
