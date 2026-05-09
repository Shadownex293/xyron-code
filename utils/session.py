import json
import os
from pathlib import Path

SESSION_DIR = Path.home() / ".xyron-code-sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

class SessionManager:
    def __init__(self, name="default"):
        self.name = name
        self.path = SESSION_DIR / f"{name}.json"

    def save(self, history: list):
        self.path.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")

    def load(self) -> list:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def list_sessions(self) -> list:
        return [f.stem for f in SESSION_DIR.glob("*.json")]

    def delete(self):
        try:
            self.path.unlink()
        except Exception:
            pass
