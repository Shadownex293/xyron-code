import json
import time
from pathlib import Path

CACHE_DIR = Path.home() / ".xyron-code-cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CATALOG_FILE = CACHE_DIR / "model-catalog.json"
CACHE_TTL = 3600

class ModelCatalog:
    def __init__(self):
        self._catalog = {}
        self._loaded = False

    def _load(self):
        if self._loaded:
            return
        try:
            if CATALOG_FILE.exists():
                data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
                self._catalog = data.get("catalog", {})
        except Exception:
            self._catalog = {}
        self._loaded = True

    def _save(self):
        try:
            CATALOG_FILE.write_text(json.dumps({"catalog": self._catalog, "updated": time.time()}, indent=2), encoding="utf-8")
        except Exception:
            pass

    def get_cached_models(self, provider: str):
        self._load()
        entry = self._catalog.get(provider)
        if not entry:
            return None
        if time.time() - entry["timestamp"] > CACHE_TTL:
            return None
        return entry["models"]

    def set_cached_models(self, provider: str, models: list):
        self._load()
        self._catalog[provider] = {"models": models, "timestamp": time.time()}
        self._save()

    async def get_models(self, provider_instance, provider_name: str) -> list:
        cached = self.get_cached_models(provider_name)
        if cached:
            return cached
        try:
            models = await provider_instance.list_models()
            self.set_cached_models(provider_name, models)
            return models
        except Exception:
            fallback = [{"id": m, "owned_by": provider_name, "context_window": None} for m in provider_instance.get_recommended_models()]
            self.set_cached_models(provider_name, fallback)
            return fallback

    def invalidate(self, provider: str):
        self._load()
        self._catalog.pop(provider, None)
        self._save()
