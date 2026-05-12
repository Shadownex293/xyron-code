import os
import json
from pathlib import Path

MODULE_CATALOG = {
    "xyron preview": {
        "id":          "xyron preview",
        "name":        "Xyron Preview",
        "description": "Scan error kode otomatis + web preview via HTTP lokal",
        "version":     "1.0.0",
        "skill_key":   "preview",
        "tools":       ["preview_scan", "preview_web"],
        "author":      "ShadowNex",
    },
    "xyron security": {
        "id":          "xyron security",
        "name":        "Xyron Security",
        "description": "Audit keamanan web — temukan celah, severity level, PoC, dan cara fix",
        "version":     "1.0.0",
        "skill_key":   "xsecurity",
        "tools":       ["security_scan_url"],
        "author":      "ShadowNex",
    },
}

_STATE_FILE = Path.home() / ".xyron_codex" / "modules.json"


def _load_state():
    if _STATE_FILE.exists():
        try:
            return json.loads(_STATE_FILE.read_text())
        except Exception:
            pass
    return {"installed": []}

def _save_state(state):
    _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _STATE_FILE.write_text(json.dumps(state, indent=2))

def list_modules():
    state     = _load_state()
    installed = set(state.get("installed", []))
    return [{**info, "installed": mid in installed} for mid, info in MODULE_CATALOG.items()]

def is_installed(module_id):
    state = _load_state()
    return module_id.lower() in [x.lower() for x in state.get("installed", [])]

def install_module(module_id):
    mid  = module_id.lower().strip()
    info = MODULE_CATALOG.get(mid)
    if not info:
        matches = [k for k in MODULE_CATALOG if mid in k.lower()]
        if matches:
            info = MODULE_CATALOG[matches[0]]
            mid  = matches[0]
        else:
            available = ", ".join(f'"{k}"' for k in MODULE_CATALOG)
            return False, f"Modul '{module_id}' tidak ditemukan.\nModul tersedia: {available}"
    if is_installed(mid):
        return False, f"Modul '{info['name']}' sudah terinstall."
    state = _load_state()
    state.setdefault("installed", []).append(mid)
    _save_state(state)
    return True, (
        f"✓ Modul '{info['name']}' v{info['version']} berhasil diinstall!\n"
        f"  Deskripsi : {info['description']}\n"
        f"  Tools     : {', '.join(info['tools'])}\n"
        f"  Restart Xyron Codex agar modul aktif sepenuhnya."
    )

def uninstall_module(module_id):
    mid = module_id.lower().strip()
    if not is_installed(mid):
        return False, f"Modul '{module_id}' belum terinstall."
    state = _load_state()
    state["installed"] = [x for x in state.get("installed", []) if x.lower() != mid]
    _save_state(state)
    info = MODULE_CATALOG.get(mid, {})
    return True, f"✓ Modul '{info.get('name', module_id)}' berhasil diuninstall."

def get_installed_ids():
    return _load_state().get("installed", [])
