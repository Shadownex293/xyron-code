import json
import httpx
from .base import BaseProvider

COPILOT_BASE_URL = "https://xyron-rest-api.vercel.app/ai/copilot"

_MAX_CTX_PER_MSG  = 2000
_MAX_HISTORY_MSGS = 30

_SYSTEM_ANCHOR = """IDENTITAS & INSTRUKSI PERMANEN — BERLAKU SEPANJANG PERCAKAPAN:
Kamu adalah Xyron Codex, AI coding assistant elite buatan ShadowNex.

ATURAN WAJIB:
- Diminta BUAT sesuatu → LANGSUNG TULIS KODENYA, tidak ada kalimat pembuka apapun
- DILARANG: "I am", "I'll help", "Sure!", "Great!", "To confirm", "I understand"
- DILARANG tanya balik kalau permintaan sudah jelas
- Respons HARUS dimulai langsung dengan kode atau jawaban singkat
- Penjelasan taruh sebagai komentar di dalam kode saja
- Kode harus LENGKAP, RUNNABLE, ZERO placeholder
- INGAT seluruh percakapan sebelumnya dan gunakan sebagai konteks"""

_REMINDER = "\n[INGAT: Jawab langsung sesuai permintaan, tanpa basa-basi]"


class CopilotProvider(BaseProvider):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name                  = "copilot"
        self.base_url              = COPILOT_BASE_URL
        self.supports_thinking     = False
        self.supports_tool_calling = False
        self.default_model         = "copilot-free"
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

    def _build_prompt(self, messages: list) -> str:
        system_content = ""
        chat_msgs      = []

        for m in messages:
            role = m.get("role", "")
            if role == "system":
                system_content = self._extract_text(m.get("content"))
            elif role in ("user", "assistant"):
                chat_msgs.append(m)

        parts   = [_SYSTEM_ANCHOR]
        trimmed = chat_msgs[-_MAX_HISTORY_MSGS:]

        if system_content:
            parts.append(f"[Konteks]\n{system_content[:1500]}\n")

        for i, m in enumerate(trimmed):
            role    = m.get("role", "")
            content = self._extract_text(m.get("content"))[:_MAX_CTX_PER_MSG]
            is_last = (i == len(trimmed) - 1)

            if role == "user":
                parts.append(f"[Human]: {content}{_REMINDER if is_last else ''}")
            elif role == "assistant":
                parts.append(f"[AI]: {content}")

        return "\n".join(parts)

    async def validate(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(COPILOT_BASE_URL, params={"message": "ping"})
                return r.status_code < 500
        except Exception as e:
            raise ValueError(f"Copilot API unreachable: {e}")

    async def stream(self, messages, tools=None, model=None, temperature=0.7, max_tokens=8000, thinking="off"):
        prompt = self._build_prompt(messages)
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.get(COPILOT_BASE_URL, params={"message": prompt})
                if r.status_code != 200:
                    yield {"type": "text", "content": f"\n[Copilot Error {r.status_code}]: {r.text[:300]}"}
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
                    yield {"type": "text", "content": "[Copilot]: (empty response)"}
                    return

                chunk_size = 40
                for i in range(0, len(text), chunk_size):
                    yield {"type": "text", "content": text[i: i + chunk_size]}

        except httpx.TimeoutException:
            yield {"type": "text", "content": "\n[Copilot Error]: Timeout 60s. Coba lagi."}
        except Exception as e:
            yield {"type": "text", "content": f"\n[Copilot Error]: {e}"}

    async def list_models(self) -> list:
        return [{"id": "copilot-free", "owned_by": "xyron-rest-api", "context_window": 8000}]

    def get_recommended_models(self) -> list:
        return ["copilot-free"]

    def get_system_prompt_appendix(self) -> str:
        return (
            "\n## COPILOT (FREE)\n"
            "Provider gratis via xyron-rest-api.vercel.app. Tidak butuh API key."
        )
