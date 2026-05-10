import json
import time
from pathlib import Path

CACHE_DIR = Path.home() / ".xyron-codex-cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = CACHE_DIR / "prompts.json"
TTL = 24 * 60 * 60

class PromptCache:
    def __init__(self):
        self._cache = {}
        self._loaded = False

    def _load(self):
        if self._loaded:
            return
        try:
            if CACHE_FILE.exists():
                self._cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            self._cache = {}
        self._loaded = True

    def _save(self):
        try:
            CACHE_FILE.write_text(json.dumps(self._cache, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def get(self, key: str):
        self._load()
        entry = self._cache.get(key)
        if not entry:
            return None
        if time.time() - entry["timestamp"] > TTL:
            del self._cache[key]
            self._save()
            return None
        return entry["value"]

    def set(self, key: str, value: str):
        self._load()
        self._cache[key] = {"value": value, "timestamp": time.time()}
        self._save()

    def invalidate(self):
        self._cache = {}
        self._save()

prompt_cache = PromptCache()
