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
        "description": "Audit keamanan web — celah, severity, PoC, cara fix, scan URL",
        "version":     "1.0.0",
        "skill_key":   "xsecurity",
        "tools":       ["security_scan_url"],
        "author":      "ShadowNex",
    },
    "xyron test": {
        "id":          "xyron test",
        "name":        "Xyron Test",
        "description": "Auto-generate unit test, jalankan, dan laporkan hasilnya",
        "version":     "1.0.0",
        "skill_key":   "xyron-test",
        "tools":       ["read_file", "write_file", "execute_command"],
        "author":      "ShadowNex",
    },
    "xyron docs": {
        "id":          "xyron docs",
        "name":        "Xyron Docs",
        "description": "Auto-generate README, API docs, dan dokumentasi project lengkap",
        "version":     "1.0.0",
        "skill_key":   "xyron-docs",
        "tools":       ["read_file", "write_file", "list_directory"],
        "author":      "ShadowNex",
    },
    "xyron translate": {
        "id":          "xyron translate",
        "name":        "Xyron Translate",
        "description": "Konversi kode antar bahasa: JS→Python, Express→FastAPI, dll",
        "version":     "1.0.0",
        "skill_key":   "xyron-translate",
        "tools":       ["read_file", "write_file"],
        "author":      "ShadowNex",
    },
    "xyron scraper": {
        "id":          "xyron scraper",
        "name":        "Xyron Scraper",
        "description": "Scrape data dari URL — harga, artikel, tabel — simpan ke JSON/CSV",
        "version":     "1.0.0",
        "skill_key":   "xyron-scraper",
        "tools":       ["web_fetch", "write_file"],
        "author":      "ShadowNex",
    },
    "xyron convert": {
        "id":          "xyron convert",
        "name":        "Xyron Convert",
        "description": "Konversi file: CSV↔JSON, compress gambar, audio/video via ffmpeg",
        "version":     "1.0.0",
        "skill_key":   "xyron-convert",
        "tools":       ["execute_command", "write_file", "read_file"],
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
            return False, f"Modul '{module_id}' tidak ditemukan.\nTersedia: {available}"
    if is_installed(mid):
        return False, f"Modul '{info['name']}' sudah terinstall."
    state = _load_state()
    state.setdefault("installed", []).append(mid)
    _save_state(state)
    return True, (
        f"✓ Modul '{info['name']}' v{info['version']} berhasil diinstall!\n"
        f"  Deskripsi : {info['description']}\n"
        f"  Tools     : {', '.join(info['tools'])}\n"
        f"  Restart Xyron Codex agar modul aktif."
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
