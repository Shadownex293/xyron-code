"""
CopilotProvider — Free AI via xyron-rest-api.vercel.app
No API key required. History-aware (full conversation memory).
"""
import json
import httpx
from .base import BaseProvider

COPILOT_BASE_URL = "https://xyron-rest-api.vercel.app/ai/copilot"

# Max chars per message when building context string for copilot API
# (keep reasonable so URL/body doesn't explode)
_MAX_CTX_PER_MSG = 2000
_MAX_HISTORY_MSGS = 30  # last N messages to include in context


class CopilotProvider(BaseProvider):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "copilot"
        self.base_url = COPILOT_BASE_URL
        self.supports_thinking = False
        self.supports_tool_calling = False   # copilot API is plain chat only
        self.default_model = "copilot-free"
        # api_key is intentionally unused — provider is keyless
        self.api_key = ""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_prompt(self, messages: list) -> str:
        """
        Convert full messages list (including history) into a single
        prompt string the Copilot API can understand.

        Format:
            [System]
            <system content>

            [Human]: ...
            [AI]: ...
            [Human]: <latest user message>

        We only send the last _MAX_HISTORY_MSGS messages so we don't
        blow up the request, but the system prompt is ALWAYS included
        so the AI never loses its identity/instructions.
        """
        parts = []

        # Always keep system prompt
        system_content = ""
        chat_msgs = []
        for m in messages:
            if m["role"] == "system":
                system_content = m["content"]
            else:
                chat_msgs.append(m)

        if system_content:
            parts.append(f"[System]\n{system_content[:3000]}\n")

        # Trim history — keep last N messages
        trimmed = chat_msgs[-_MAX_HISTORY_MSGS:]

        for m in trimmed:
            role = m["role"]
            content = m.get("content") or ""
            if isinstance(content, list):
                # Handle multi-part content blocks
                content = " ".join(
                    c.get("text", "") for c in content if isinstance(c, dict)
                )
            content = content[:_MAX_CTX_PER_MSG]

            if role == "user":
                parts.append(f"[Human]: {content}")
            elif role == "assistant":
                parts.append(f"[AI]: {content}")

        return "\n".join(parts)

    def _headers(self) -> dict:
        return {"Content-Type": "application/json"}

    # ------------------------------------------------------------------
    # BaseProvider interface
    # ------------------------------------------------------------------

    async def validate(self) -> bool:
        """Ping the API with a simple test message."""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(
                    COPILOT_BASE_URL,
                    params={"message": "ping"},
                )
                # Any 2xx or 4xx (means API responded) is fine
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
        Non-streaming call to Copilot API (API returns full JSON),
        yielded as a single text chunk so the rest of the codebase
        sees it as a normal stream.
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
                        "type": "text",
                        "content": f"\n[Copilot Error {r.status_code}]: {r.text[:300]}",
                    }
                    return

                # Try to parse JSON response
                try:
                    data = r.json()
                    # API returns {"result": "..."} or {"response": "..."} or plain string
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
                    # Not JSON — use raw text
                    text = r.text

                if not text or not text.strip():
                    yield {"type": "text", "content": "[Copilot]: (empty response)"}
                    return

                # Simulate streaming by yielding in small chunks
                # so the UI renders progressively
                chunk_size = 40
                for i in range(0, len(text), chunk_size):
                    yield {"type": "text", "content": text[i : i + chunk_size]}

        except httpx.TimeoutException:
            yield {
                "type": "text",
                "content": "\n[Copilot Error]: Request timeout (60s). Try again.",
            }
        except Exception as e:
            yield {"type": "text", "content": f"\n[Copilot Error]: {e}"}

    async def list_models(self) -> list:
        return [
            {
                "id": "copilot-free",
                "owned_by": "xyron-rest-api",
                "context_window": 8000,
            }
        ]

    def get_recommended_models(self) -> list:
        return ["copilot-free"]

    def get_system_prompt_appendix(self) -> str:
        return (
            "\n## COPILOT (FREE)\n"
            "Provider gratis via xyron-rest-api.vercel.app. "
            "Tidak butuh API key. History percakapan tetap terjaga."
        )
