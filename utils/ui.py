import os
import sys
import json
import time
import threading
from pathlib import Path

try:
    from rich.console import Console
    from rich.text import Text
    from rich.live import Live
    RICH = True
except ImportError:
    RICH = False

console = Console() if RICH else None

class C:
    @staticmethod
    def brand(t):   return f"\033[38;2;167;139;250m{t}\033[0m"
    @staticmethod
    def dim(t):     return f"\033[2m{t}\033[0m"
    @staticmethod
    def white(t):   return f"\033[97m{t}\033[0m"
    @staticmethod
    def orange(t):  return f"\033[38;2;251;146;60m{t}\033[0m"
    @staticmethod
    def green(t):   return f"\033[38;2;74;222;128m{t}\033[0m"
    @staticmethod
    def red(t):     return f"\033[38;2;248;113;113m{t}\033[0m"
    @staticmethod
    def cyan(t):    return f"\033[38;2;34;211;238m{t}\033[0m"
    @staticmethod
    def yellow(t):  return f"\033[38;2;251;191;36m{t}\033[0m"
    @staticmethod
    def bold(t):    return f"\033[1m{t}\033[0m"
    success = green
    error   = red
    warn    = yellow
    ai      = brand


def get_width() -> int:
    return min(os.get_terminal_size().columns if hasattr(os, "get_terminal_size") else 80, 120)


def print_banner(provider_name: str, model: str, cfg: dict = None):
    print()
    print("  " + C.brand("██╗  ██╗██╗   ██╗██████╗  ██████╗ ███╗  ██╗"))
    print("  " + C.brand("╚██╗██╔╝╚██╗ ██╔╝██╔══██╗██╔═══██╗████╗ ██║"))
    print("  " + C.brand(" ╚███╔╝  ╚████╔╝ ██████╔╝██║   ██║██╔██╗██║"))
    print("  " + C.brand(" ██╔██╗   ╚██╔╝  ██╔══██╗██║   ██║██║╚████║"))
    print("  " + C.brand("██╔╝╚██╗   ██║   ██║  ██║╚██████╔╝██║ ╚███║"))
    print("  " + C.brand("╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚══╝"))
    print()
    print("  " + C.dim("Xyron Code Ai Agent ·  By ShadowNex  ·  V1.0"))
    print()
    w = get_width()
    parts = [
        C.brand("◆"),
        C.white(provider_name.lower()),
        C.dim("/"),
        C.white(model),
        C.dim("· tools on"),
    ]
    cmds = "/help  /model  /provider  /thinking  /status  /save  /load  /clear"
    disp = cmds[:w - 5] + "…" if len(cmds) > w - 4 else cmds
    print("  " + "  ".join(parts))
    print("  " + C.dim(disp))
    print()


def print_user_box(text: str):
    w = get_width()
    print()
    print("  " + C.dim("─" * (w - 2)))
    for i, line in enumerate(text.split("\n")):
        prefix = C.orange("›") if i == 0 else " "
        print(f"  {prefix} {C.white(line)}")
    print()


def print_ai_header(provider_name: str, model: str):
    w = get_width()
    print("  " + C.dim("─" * (w - 2)))
    print("  " + C.brand("◆") + "  " + C.dim(f"{provider_name.lower()} / {model}"))
    print()


def print_ai_footer():
    print()


def print_ai_footer_line():
    w = get_width()
    print()
    print("  " + C.dim("─" * (w - 2)))


def print_error_box(msg: str):
    print()
    print("  " + C.red("✖") + "  " + C.white(msg))
    print()


def print_info_box(msg: str, label: str = "INFO"):
    print("  " + C.brand("◈") + "  " + C.dim(f"{label.lower()}  ·  ") + C.white(msg))


def print_tool_badge(tool_name: str, detail: str = ""):
    d = C.dim(f"  ·  {str(detail)[:64]}") if detail else ""
    print("  " + C.cyan("⟳") + "  " + C.white(tool_name) + d)


def print_auto_continue_badge(n: int, max_: int):
    print("  " + C.dim(f"↻  auto-continue {n}/{max_}"))


def print_retry_badge(n: int, max_: int, delay: int):
    print("  " + C.yellow("⚠") + "  " + C.dim(f"retry {n}/{max_}  ·  {delay}ms"))


_stream_buf = ""


def stream_chunk(chunk: str):
    global _stream_buf
    _stream_buf += chunk
    lines = _stream_buf.split("\n")
    _stream_buf = lines.pop()
    for line in lines:
        sys.stdout.write("  " + line + "\n")
    sys.stdout.flush()


def stream_flush():
    global _stream_buf
    if _stream_buf:
        sys.stdout.write("  " + _stream_buf + "\n")
        sys.stdout.flush()
        _stream_buf = ""


class Spinner:
    FRAMES = ["◐", "◓", "◑", "◒"]

    def __init__(self, label: str = "thinking…"):
        self.label = label
        self._active = False
        self._thread = None

    def start(self):
        self._active = True
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def _spin(self):
        i = 0
        while self._active:
            frame = self.FRAMES[i % len(self.FRAMES)]
            sys.stdout.write(f"\r  {C.brand(frame)}  {C.dim(self.label)}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

    def stop(self):
        self._active = False
        if self._thread:
            self._thread.join(timeout=0.3)
        sys.stdout.write("\r" + " " * 40 + "\r")
        sys.stdout.flush()


_active_spinner: Spinner | None = None


def create_spinner(status: str = "loading") -> Spinner:
    global _active_spinner
    if _active_spinner:
        try:
            _active_spinner.stop()
        except Exception:
            pass
        _active_spinner = None
    labels = {
        "loading":    "thinking…",
        "connecting": "connecting…",
        "streaming":  "streaming…",
        "thinking":   "deep thinking…",
        "tool_read":  "reading file…",
        "tool_write": "writing file…",
        "tool_shell": "running command…",
        "tool_grep":  "searching codebase…",
        "tool_generic": "running tool…",
    }
    sp = Spinner(labels.get(status, status + "…"))
    sp.start()
    _active_spinner = sp
    return sp


def stop_active_spinner():
    global _active_spinner
    if _active_spinner:
        try:
            _active_spinner.stop()
        except Exception:
            pass
        _active_spinner = None


import re

_ROADMAP_HEADER = re.compile(r"(?:^|\n)#+\s*(?:plan|roadmap|steps|task|todo|langkah)", re.IGNORECASE)
_STEP_LINE      = re.compile(r"^\s*[·•\-*\d+\.]+\s+(.+)")


def parse_roadmap(text: str):
    if not _ROADMAP_HEADER.search(text):
        return None
    steps = []
    in_section = False
    for line in text.split("\n"):
        if _ROADMAP_HEADER.search(line):
            in_section = True
            continue
        if in_section:
            m = _STEP_LINE.match(line)
            if m:
                steps.append({"label": m.group(1).strip(), "done": False})
            elif line.strip() == "":
                continue
            elif line.startswith("#"):
                break
    return {"steps": steps, "current": 0} if len(steps) >= 2 else None


def print_roadmap_status(roadmap: dict):
    if not roadmap or not roadmap.get("steps"):
        return
    print()
    for i, s in enumerate(roadmap["steps"]):
        if s["done"]:
            icon = C.green("✓")
            label = C.dim(s["label"])
        elif i == roadmap.get("current", 0):
            icon = C.brand("●")
            label = C.white(s["label"])
        else:
            icon = C.dim("○")
            label = C.dim(s["label"])
        print(f"  {icon}  {label}")
    print()


def build_roadmap_continue_prompt(roadmap: dict) -> str:
    if not roadmap or not roadmap.get("steps"):
        return ""
    rem = [f"- {s['label']}" for s in roadmap["steps"][roadmap.get("current", 0):]]
    return "\n\nContinue with remaining steps:\n" + "\n".join(rem)


def build_token_bar(used: int, max_: int, length: int = 20) -> str:
    filled = min(round((used / max_) * length), length)
    pct = used / max_
    color = C.red if pct > 0.85 else (C.yellow if pct > 0.60 else C.green)
    return C.dim("[") + color("█" * filled) + C.dim("░" * (length - filled)) + C.dim("]")


_HIST_DIR  = Path.home() / ".xyronccode"
_HIST_FILE = _HIST_DIR / "model-history.json"


def _load_model_history() -> dict:
    try:
        _HIST_DIR.mkdir(parents=True, exist_ok=True)
        if _HIST_FILE.exists():
            return json.loads(_HIST_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def save_model_history(provider_name: str, model: str):
    h = _load_model_history()
    prev = h.get(provider_name, [])
    h[provider_name] = [model] + [m for m in prev if m != model][:4]
    try:
        _HIST_DIR.mkdir(parents=True, exist_ok=True)
        _HIST_FILE.write_text(json.dumps(h, indent=2), encoding="utf-8")
    except Exception:
        pass


def model_selector(provider, current_model: str) -> str:
    h    = _load_model_history()
    rec  = h.get(provider.name, [])[:5]
    reco = [m for m in (provider.get_recommended_models() or []) if m not in rec]
    cur  = current_model or provider.default_model
    all_ = list(dict.fromkeys(rec + reco))

    print()
    print("  " + C.brand("◆") + "  " + C.dim("model  ·  " + provider.name.lower()))
    print()

    if rec:
        print("  " + C.dim("recent"))
        for i, m in enumerate(rec):
            tag = C.dim("  ← last") if i == 0 else ""
            print(f"    {C.dim(str(i+1).rjust(2))}  {C.white(m)}{tag}")
        print()

    if reco:
        print("  " + C.dim("recommended"))
        for i, m in enumerate(reco):
            n = len(rec) + i + 1
            print(f"    {C.dim(str(n).rjust(2))}  {C.white(m)}")
        print()

    print("  " + C.dim("current  ") + C.white(cur))
    print("  " + C.dim("enter number, model id, or ↵ to keep"))
    print()

    sys.stdout.write("  " + C.brand(">") + " ")
    sys.stdout.flush()
    try:
        inp = input().strip()
    except (EOFError, KeyboardInterrupt):
        return cur

    if not inp:
        return cur
    try:
        n = int(inp)
        if 1 <= n <= len(all_):
            chosen = all_[n - 1]
            save_model_history(provider.name, chosen)
            return chosen
    except ValueError:
        pass
    save_model_history(provider.name, inp)
    return inp