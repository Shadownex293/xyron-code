import os
from .groq_provider import GroqProvider
from .openrouter_provider import OpenRouterProvider
from .copilot_provider import CopilotProvider
from .other_providers import (
    GeminiProvider, NvidiaProvider, CerebrasProvider, MistralProvider,
    XAIProvider, SambanovaProvider, TogetherProvider, KimiProvider,
    QwenProvider, MinimaxProvider, DeepSeekProvider,
)

PROVIDER_REGISTRY = {
    "copilot":    CopilotProvider,   
    "groq":       GroqProvider,
    "openrouter": OpenRouterProvider,
    "gemini":     GeminiProvider,
    "deepseek":   DeepSeekProvider,
    "nvidia":     NvidiaProvider,
    "cerebras":   CerebrasProvider,
    "mistral":    MistralProvider,
    "xai":        XAIProvider,
    "sambanova":  SambanovaProvider,
    "together":   TogetherProvider,
    "kimi":       KimiProvider,
    "qwen":       QwenProvider,
    "minimax":    MinimaxProvider,
}

KEY_MAP = {
    "copilot":    None,              
    "groq":       "GROQ_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "gemini":     "GEMINI_API_KEY",
    "deepseek":   "DEEPSEEK_API_KEY",
    "nvidia":     "NVIDIA_NIM_API_KEY",
    "cerebras":   "CEREBRAS_API_KEY",
    "mistral":    "MISTRAL_API_KEY",
    "xai":        "XAI_API_KEY",
    "sambanova":  "SAMBANOVA_API_KEY",
    "together":   "TOGETHER_API_KEY",
    "kimi":       "KIMI_API_KEY",
    "qwen":       "QWEN_API_KEY",
    "minimax":    "MINIMAX_API_KEY",
}

PRIORITY_ORDER = [
    "groq", "openrouter", "gemini", "deepseek", "cerebras", "mistral",
    "xai", "kimi", "qwen", "sambanova", "together", "minimax", "nvidia",
    "copilot",
]

PLACEHOLDER_PATTERNS = ("...", "your_key_here", "sk-...", "gsk_...", "tvly-...")


KEYLESS_PROVIDERS = {"copilot"}


def get_available_providers():
    return list(PROVIDER_REGISTRY.keys())


def _is_valid_key(val: str) -> bool:
    if not val or not val.strip():
        return False
    v = val.strip()
    
    for placeholder in PLACEHOLDER_PATTERNS:
        if v.endswith(placeholder) or v == placeholder:
            return False
    
    if len(v) < 8:
        return False
    return True


def auto_detect_provider():

    for name in PRIORITY_ORDER:
        if name in KEYLESS_PROVIDERS:

            continue
        env_key = KEY_MAP.get(name)
        val = os.environ.get(env_key, "") if env_key else ""
        if _is_valid_key(val):
            return name

    for name in PRIORITY_ORDER:
        if name in KEYLESS_PROVIDERS:
            return name
    return None


def get_api_key_for_provider(name):
    if name in KEYLESS_PROVIDERS:
        return ""
    env_key = KEY_MAP.get(name)
    return os.environ.get(env_key, "").strip() if env_key else None


def create_provider(name, api_key):
    cls = PROVIDER_REGISTRY.get(name)
    if not cls:
        available = ", ".join(get_available_providers())
        raise ValueError(f'Unknown provider: "{name}". Available: {available}')
    config = {"api_key": api_key, "qwen_region": os.environ.get("QWEN_REGION", "sg")}
    return cls(config)
