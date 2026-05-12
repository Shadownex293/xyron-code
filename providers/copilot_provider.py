"""
CopilotProvider — Free AI via xyron-rest-api.vercel.app
No API key required. History-aware (full conversation memory).
"""
import json
import httpx
from .base import BaseProvider

COPILOT_BASE_URL = "https://xyron-rest-api.vercel.app/ai/copilot"

_MAX_CTX_PER_MSG  = 2000   # max chars per message in history
_MAX_HISTORY_MSGS = 30     # max recent messages to include


class CopilotProvider(BaseProvider):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name               = "copilot"
        self.base_url           = COPILOT_BASE_URL
        self.supports_thinking  = False
        self.supports_tool_calling = False  # copilot API is plain chat only
        self.default_model      = "copilot-free"
        self.api_key            = ""       # keyless — intentionally empty

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_text(self, content) -> str:
        """
        Safely extract plain text dari semua format content yang mungkin:
          - str       -> langsung pakai
          - None      -> ""
          - dict      -> ambil key 'text'/'content', fallback json.dumps
          - list      -> gabung semua elemen yang punya text
          - lainnya   -> str()
        """
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
        """
        Konversi messages list (system + history + pesan baru) jadi
        satu string untuk dikirim ke Copilot API.

        Format:
            [System]
            <system prompt>

            [Human]: ...
            [AI]: ...
            [Human]: <pesan terbaru>

        System prompt SELALU disertakan supaya AI tidak amnesia.
        History dibatasi _MAX_HISTORY_MSGS pesan terakhir.
        """
        parts = []

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

        # Hanya ambil N pesan terakhir supaya request tidak kegedean
        trimmed = chat_msgs[-_MAX_HISTORY_MSGS:]

        for m in trimmed:
            role    = m.get("role", "")
            content = self._extract_text(m.get("content"))
            content = content[:_MAX_CTX_PER_MSG]

            if role == "user":
                parts.append(f"[Human]: {content}")
            elif role == "assistant":
                parts.append(f"[AI]: {content}")
            # skip role 'tool' / 'tool_result' — tidak relevan untuk copilot

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # BaseProvider interface
    # ------------------------------------------------------------------

    async def validate(self) -> bool:
        """Ping API dengan pesan test singkat."""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(
                    COPILOT_BASE_URL,
                    params={"message": "ping"},
                )
                return r.status_code < 500
        except Exception as e:
            raise ValueError(f"Copilot API unreachable: {e}")

    async def stream(
        self,
        messages,
        tools=None,
        model=None,
        temperature=0.7,
        max_tokens=8000,
        thinking="off",
    ):
        """
        Fetch dari Copilot API (satu response penuh, bukan SSE),
        di-yield per chunk supaya UI terlihat streaming.
        """
        prompt = self._build_prompt(messages)

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.get(
                    COPILOT_BASE_URL,
                    params={"message": prompt},
                )

                if r.status_code != 200:
                    yield {
                        "type":    "text",
                        "content": f"\n[Copilot Error {r.status_code}]: {r.text[:300]}",
                    }
                    return

                # Parse response — API bisa return JSON atau plain text
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

                text = self._extract_text(text)   # pastikan string

                if not text or not text.strip():
                    yield {"type": "text", "content": "[Copilot]: (empty response)"}
                    return

                # Yield per chunk untuk efek streaming
                chunk_size = 40
                for i in range(0, len(text), chunk_size):
                    yield {"type": "text", "content": text[i : i + chunk_size]}

        except httpx.TimeoutException:
            yield {
                "type":    "text",
                "content": "\n[Copilot Error]: Request timeout (60s). Coba lagi.",
            }
        except Exception as e:
            yield {"type": "text", "content": f"\n[Copilot Error]: {e}"}

    async def list_models(self) -> list:
        return [{"id": "copilot-free", "owned_by": "xyron-rest-api", "context_window": 8000}]

    def get_recommended_models(self) -> list:
        return ["copilot-free"]

    def get_system_prompt_appendix(self) -> str:
        return (
            "\n## COPILOT (FREE)\n"
            "Provider gratis via xyron-rest-api.vercel.app. "
            "Tidak butuh API key. History percakapan tetap terjaga."
        )
