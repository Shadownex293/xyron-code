import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.cwd() / ".env")

_config = None


def load_config() -> dict:
    global _config
    from utils.setup import load_saved_config, run_setup_wizard, _is_valid_key_val

    
    saved = load_saved_config()
    if saved and saved.get("provider") and saved.get("api_key") and _is_valid_key_val(saved["api_key"]):
        _config = _build(saved["provider"], saved["api_key"], saved.get("model", "auto"))
        return _config


    from providers.factory import auto_detect_provider, get_api_key_for_provider
    env_provider = os.environ.get("XYRON_PROVIDER", "auto")
    if env_provider != "auto":
        key = get_api_key_for_provider(env_provider)
        if key and _is_valid_key_val(key):
            _config = _build(env_provider, key, os.environ.get("XYRON_DEFAULT_MODEL", "auto"))
            return _config
    else:
        detected = auto_detect_provider()
        if detected:
            key = get_api_key_for_provider(detected)
            if key and _is_valid_key_val(key):
                _config = _build(detected, key, os.environ.get("XYRON_DEFAULT_MODEL", "auto"))
                return _config

    
    result = run_setup_wizard()
    _config = _build(result["provider"], result["api_key"], result.get("model", "auto"))
    return _config


def _build(provider: str, api_key: str, model: str) -> dict:
    return {
        "provider":            provider,
        "api_key":             api_key,
        "model":               model,
        "max_context_tokens":  int(os.environ.get("XYRON_MAX_CONTEXT_TOKENS", "120000")),
        "max_response_tokens": int(os.environ.get("XYRON_MAX_RESPONSE_TOKENS", "8000")),
        "temperature":         float(os.environ.get("XYRON_TEMPERATURE", "0.7")),
        "tavily_key":          os.environ.get("TAVILY_API_KEY", ""),
    }


def get_config() -> dict:
    global _config
    if not _config:
        return load_config()
    return _config


def reset_config() -> dict:
    global _config
    _config = None
    return load_config()
