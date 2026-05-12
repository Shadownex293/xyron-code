"""
Setup wizard interaktif untuk Xyron Codex.
Dipanggil saat tidak ada saved config / user belum pernah setup.
"""

import os
import sys
import json
from pathlib import Path

CONFIG_DIR  = Path.home() / ".xyron-codex"
CONFIG_FILE = CONFIG_DIR / "config.json"

PROVIDERS = [
    {
        "id":      "copilot",
        "label":   "Copilot (GRATIS — No API Key!)",
        "company": "ShadowNex",
        "free":    "100% gratis, langsung pakai, tidak perlu API key",
        "url":     "https://xyron-rest-api.vercel.app",
        "models":  ["copilot-free"],
        "keyless": True,
    },
    {
        "id":      "claude-free",
        "label":   "Claude (GRATIS — No API Key!)",
        "company": "ShadowNex x Anthropic",
        "free":    "100% gratis, Claude AI via xyron-rest-api, tidak perlu API key",
        "url":     "https://xyron-rest-api.vercel.app",
        "models":  ["claude-free"],
        "keyless": True,
    },
    {
        "id":      "gemini",
        "label":   "Gemini",
        "company": "Google",
        "free":    "Free tier — 1500 req/day",
        "url":     "https://aistudio.google.com/app/apikey",
        "models":  ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
    },
    {
        "id":      "groq",
        "label":   "Groq",
        "company": "Groq",
        "free":    "Free — 1M tokens/day (LPU, sangat cepat)",
        "url":     "https://console.groq.com/keys",
        "models":  ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "qwen-3-32b"],
    },
    {
        "id":      "deepseek",
        "label":   "DeepSeek",
        "company": "DeepSeek AI",
        "free":    "Berbayar — sangat murah ($0.07/1M tokens)",
        "url":     "https://platform.deepseek.com/api_keys",
        "models":  ["deepseek-chat", "deepseek-reasoner"],
    },
    {
        "id":      "openrouter",
        "label":   "OpenRouter",
        "company": "OpenRouter",
        "free":    "500+ model — ada yang gratis",
        "url":     "https://openrouter.ai/keys",
        "models":  ["google/gemini-2.5-flash", "deepseek/deepseek-r1", "meta-llama/llama-3.3-70b-instruct"],
    },
    {
        "id":      "cerebras",
        "label":   "Cerebras",
        "company": "Cerebras",
        "free":    "Free — 1M tokens/day (WSE chip, ultra cepat)",
        "url":     "https://cloud.cerebras.ai",
        "models":  ["llama-3.3-70b", "llama-3.1-8b"],
    },
    {
        "id":      "mistral",
        "label":   "Mistral",
        "company": "Mistral AI",
        "free":    "Free — 1B tokens/month",
        "url":     "https://console.mistral.ai/api-keys",
        "models":  ["mistral-large-latest", "codestral-latest", "mistral-small-latest"],
    },
    {
        "id":      "xai",
        "label":   "xAI (Grok)",
        "company": "xAI",
        "free":    "$25 signup credits",
        "url":     "https://console.x.ai",
        "models":  ["grok-3-mini", "grok-3"],
    },
    {
        "id":      "together",
        "label":   "Together AI",
        "company": "Together",
        "free":    "~$100 signup credits",
        "url":     "https://api.together.ai",
        "models":  ["meta-llama/Meta-Llama-3.3-70B-Instruct-Turbo", "deepseek-ai/DeepSeek-R1"],
    },
    {
        "id":      "sambanova",
        "label":   "SambaNova",
        "company": "SambaNova",
        "free":    "Free tier tersedia",
        "url":     "https://cloud.sambanova.ai",
        "models":  ["Meta-Llama-3.3-70B-Instruct", "DeepSeek-R1-Distill-Llama-70B"],
    },
    {
        "id":      "nvidia",
        "label":   "NVIDIA NIM",
        "company": "NVIDIA",
        "free":    "Free credits di build.nvidia.com",
        "url":     "https://build.nvidia.com",
        "models":  ["meta/llama-3.3-70b-instruct", "deepseek-ai/deepseek-r1"],
    },
]

# ── ANSI colors ────────────────────────────────────────────────────────────────

def _c(code, t): return f"\033[{code}m{t}\033[0m"
def brand(t):  return _c("38;2;167;139;250", t)
def dim(t):    return _c("2", t)
def white(t):  return _c("97", t)
def green(t):  return _c("38;2;74;222;128", t)
def red(t):    return _c("38;2;248;113;113", t)
def yellow(t): return _c("38;2;251;191;36", t)
def orange(t): return _c("38;2;251;146;60", t)
def cyan(t):   return _c("38;2;34;211;238", t)
def bold(t):   return _c("1", t)

def _inp(prompt: str) -> str:
    sys.stdout.write(prompt)
    sys.stdout.flush()
    try:
        return input()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)

def _clear_line():
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()

# ── Saved config helpers ───────────────────────────────────────────────────────

def load_saved_config() -> dict | None:
    try:
        if CONFIG_FILE.exists():
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


def save_config(data: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def delete_saved_config():
    try:
        CONFIG_FILE.unlink()
    except Exception:
        pass


# ── Print helpers ──────────────────────────────────────────────────────────────

def _print_header():
    print()
    print("  " + brand("██╗  ██╗██╗   ██╗██████╗  ██████╗ ███╗  ██╗"))
    print("  " + brand("╚██╗██╔╝╚██╗ ██╔╝██╔══██╗██╔═══██╗████╗ ██║"))
    print("  " + brand(" ╚███╔╝  ╚████╔╝ ██████╔╝██║   ██║██╔██╗██║"))
    print("  " + brand(" ██╔██╗   ╚██╔╝  ██╔══██╗██║   ██║██║╚████║"))
    print("  " + brand("██╔╝╚██╗   ██║   ██║  ██║╚██████╔╝██║ ╚███║"))
    print("  " + brand("╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚══╝"))
    print()
    print("  " + dim("Terminal AI Coding Assistant  ·  by ShadowNex  ·  v0.3.0"))
    print()


def _print_separator():
    try:
        w = os.get_terminal_size().columns
    except Exception:
        w = 60
    print("  " + dim("─" * min(w - 4, 56)))


# ── Provider selection ─────────────────────────────────────────────────────────

def _select_provider() -> dict:
    print()
    print("  " + brand("◆") + "  " + white("Pilih provider AI"))
    print()

    for i, p in enumerate(PROVIDERS):
        num   = dim(f"{i+1:>2}.")
        label = white(p["label"])
        comp  = dim(f"  [{p['company']}]")
        free  = dim(f"  {p['free']}")
        print(f"  {num}  {label}{comp}{free}")

    print()
    while True:
        raw = _inp("  " + orange("❯") + "  Pilih nomor: ")
        raw = raw.strip()
        try:
            n = int(raw)
            if 1 <= n <= len(PROVIDERS):
                return PROVIDERS[n - 1]
        except ValueError:
            # coba cocokkan nama
            match = next((p for p in PROVIDERS if p["id"] == raw.lower() or p["label"].lower() == raw.lower()), None)
            if match:
                return match
        print("  " + red("✖") + f"  Input tidak valid. Masukkan nomor 1–{len(PROVIDERS)}.")


# ── API key input ──────────────────────────────────────────────────────────────

def _input_api_key(provider: dict) -> str:
    # Keyless provider — tidak butuh API key sama sekali
    if provider.get("keyless"):
        print()
        _print_separator()
        print()
        print("  " + brand("◆") + "  " + white(f"{provider['label']}"))
        print()
        print("  " + green("✓") + "  " + white("Provider ini GRATIS — tidak perlu API key!"))
        print("  " + dim("Langsung bisa dipakai tanpa daftar apapun."))
        print("  " + dim(f"Endpoint: {provider['url']}"))
        print()
        return ""   # empty string = keyless

    print()
    _print_separator()
    print()
    print("  " + brand("◆") + "  " + white(f"API Key untuk {provider['label']}"))
    print()
    print("  " + dim("Dapatkan key gratis di:"))
    print("  " + cyan(provider["url"]))
    print()

    while True:
        import getpass
        sys.stdout.write("  " + orange("❯") + "  Masukkan API key: ")
        sys.stdout.flush()
        try:
            key = getpass.getpass("")
        except Exception:
            key = _inp("")

        key = key.strip()
        if len(key) >= 8:
            return key
        print("  " + red("✖") + "  API key terlalu pendek. Coba lagi.")


# ── Model selection ────────────────────────────────────────────────────────────

def _select_model(provider: dict) -> str:
    models = provider.get("models", [])
    if not models:
        return "auto"

    print()
    _print_separator()
    print()
    print("  " + brand("◆") + "  " + white("Pilih model"))
    print()

    for i, m in enumerate(models):
        tag = dim("  ← recommended") if i == 0 else ""
        print(f"  {dim(f'{i+1:>2}.')}  {white(m)}{tag}")

    print(f"  {dim(f'{len(models)+1:>2}.')}  {dim('Ketik manual (model ID sendiri)')}")
    print()

    while True:
        raw = _inp("  " + orange("❯") + "  Pilih nomor (Enter = pakai recommended): ").strip()
        if raw == "":
            return models[0]
        try:
            n = int(raw)
            if 1 <= n <= len(models):
                return models[n - 1]
            if n == len(models) + 1:
                return _inp("  " + orange("❯") + "  Model ID: ").strip() or models[0]
        except ValueError:
            if raw:
                return raw
        print("  " + red("✖") + f"  Pilih 1–{len(models)+1}.")


# ── Save prompt ────────────────────────────────────────────────────────────────

def _ask_save(provider: dict, api_key: str, model: str) -> bool:
    print()
    _print_separator()
    print()
    print("  " + brand("◆") + "  " + white("Simpan konfigurasi?"))
    print()
    print(f"  {dim('1.')}  {white('Simpan')}  {dim('— next run langsung masuk, gak perlu input ulang')}")
    print(f"  {dim('2.')}  {white('Sesi ini saja')}  {dim('— next run akan diminta input lagi')}")
    print()

    while True:
        raw = _inp("  " + orange("❯") + "  Pilih (1/2): ").strip()
        if raw in ("1", ""):
            save_config({
                "provider": provider["id"],
                "api_key":  api_key,
                "model":    model,
            })
            print()
            print("  " + green("✓") + "  " + white("Tersimpan di ~/.xyron-codex/config.json"))
            return True
        if raw == "2":
            print()
            print("  " + dim("✓  Sesi ini saja. Tidak disimpan."))
            return False
        print("  " + red("✖") + "  Ketik 1 atau 2.")


# ── Main wizard ────────────────────────────────────────────────────────────────

def run_setup_wizard() -> dict:
    """Jalankan wizard dan return dict config siap pakai."""
    _print_header()
    _print_separator()
    print()
    print("  " + dim("Setup pertama kali. Ikuti langkah berikut."))

    provider = _select_provider()
    api_key  = _input_api_key(provider)
    model    = _select_model(provider)
    _ask_save(provider, api_key, model)

    print()
    _print_separator()
    print()
    print("  " + green("✓") + "  " + white(f"Provider : {provider['label']}"))
    print("  " + green("✓") + "  " + white(f"Model    : {model}"))
    print()

    return {
        "provider": provider["id"],
        "api_key":  api_key,
        "model":    model,
    }


def maybe_change_provider() -> dict | None:
    """Dipanggil via /provider command — re-run wizard untuk ganti provider."""
    saved = load_saved_config()

    print()
    print("  " + brand("◆") + "  " + white("Ganti provider"))
    if saved:
        print("  " + dim(f"Sekarang: {saved.get('provider','?')} / {saved.get('model','?')}"))
    print()

    provider = _select_provider()
    api_key  = _input_api_key(provider)
    model    = _select_model(provider)
    _ask_save(provider, api_key, model)

    return {
        "provider": provider["id"],
        "api_key":  api_key,
        "model":    model,
    }


# ── Key validator (dipanggil dari config.py) ───────────────────────────────────

PLACEHOLDER_PATTERNS = ("...", "your_key_here", "sk-...", "gsk_...", "tvly-...")

# Providers that need no key — empty string is valid for these
_KEYLESS_IDS = {"copilot", "claude-free"}

def _is_valid_key_val(val: str, provider_id: str = "") -> bool:
    """
    Return True jika val adalah API key yang valid.
    Untuk keyless provider (copilot dll), empty string juga valid.
    """
    if provider_id in _KEYLESS_IDS:
        return True   # keyless — selalu valid
    if not val or not val.strip():
        return False
    v = val.strip()
    for p in PLACEHOLDER_PATTERNS:
        if v.endswith(p) or v == p:
            return False
    return len(v) >= 8
