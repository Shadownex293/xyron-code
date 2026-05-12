import asyncio
import os
import re
import webbrowser
import http.server
import threading
import socket
from pathlib import Path

preview_tools = [
    {
        "type": "function",
        "function": {
            "name": "preview_scan",
            "description": "Scan file atau direktori untuk mendeteksi error sintaks, import rusak, atau masalah umum sebelum preview. Dukung: Python (.py), JavaScript (.js), TypeScript (.ts/.tsx), HTML (.html), CSS (.css), JSON (.json).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path file atau direktori yang mau di-scan."},
                    "recursive": {"type": "boolean", "description": "Scan subdirektori juga (default: false)."},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "preview_web",
            "description": "Launch web preview untuk file HTML / direktori web project. Serve via HTTP lokal dan buka di browser default.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path file HTML atau direktori yang mau di-preview."},
                    "port": {"type": "integer", "description": "Port HTTP server (default: auto-detect free port)."},
                    "auto_open": {"type": "boolean", "description": "Buka browser otomatis (default: true)."},
                },
                "required": ["path"],
            },
        },
    },
]


def _scan_python(path):
    import py_compile
    errors = []
    try:
        py_compile.compile(path, doraise=True)
    except py_compile.PyCompileError as e:
        errors.append(str(e))
    return errors

def _scan_json(path):
    import json
    errors = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"JSON error at line {e.lineno}: {e.msg}")
    return errors

def _scan_html(path):
    errors = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read()
        if re.search(r'<img(?![^>]*alt=)[^>]*>', content, re.IGNORECASE):
            errors.append("WARNING: Ada tag <img> tanpa atribut alt.")
        open_tags  = re.findall(r'<([a-z][a-z0-9]*)\b[^/]*?(?<!/)>', content, re.IGNORECASE)
        close_tags = re.findall(r'</([a-z][a-z0-9]*)>', content, re.IGNORECASE)
        void_tags  = {"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}
        opens  = [t.lower() for t in open_tags  if t.lower() not in void_tags]
        closes = [t.lower() for t in close_tags if t.lower() not in void_tags]
        opens_count, closes_count = {}, {}
        for t in opens:  opens_count[t]  = opens_count.get(t, 0) + 1
        for t in closes: closes_count[t] = closes_count.get(t, 0) + 1
        for tag, count in opens_count.items():
            if closes_count.get(tag, 0) < count:
                errors.append(f"WARNING: Tag <{tag}> mungkin tidak ditutup ({count} buka, {closes_count.get(tag,0)} tutup).")
    except Exception as e:
        errors.append(f"Gagal scan HTML: {e}")
    return errors

def _scan_js_ts(path):
    errors = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        for i, line in enumerate(lines, 1):
            if line.count("(") - line.count(")") > 2:
                errors.append(f"WARNING baris {i}: Kemungkinan kurung tidak seimbang.")
            if "TODO" in line or "FIXME" in line:
                errors.append(f"INFO baris {i}: Ada TODO/FIXME — {line.strip()[:60]}")
        if re.search(r'\bundefined\b.*=', "".join(lines)):
            errors.append("WARNING: Penggunaan 'undefined' yang mencurigakan ditemukan.")
    except Exception as e:
        errors.append(f"Gagal scan JS/TS: {e}")
    return errors

def _scan_css(path):
    errors = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read()
        opens, closes = content.count("{"), content.count("}")
        if opens != closes:
            errors.append(f"ERROR CSS: Kurung kurawal tidak seimbang ({opens} buka, {closes} tutup).")
    except Exception as e:
        errors.append(f"Gagal scan CSS: {e}")
    return errors


SCANNERS = {
    ".py": _scan_python, ".json": _scan_json,
    ".html": _scan_html, ".htm": _scan_html,
    ".js": _scan_js_ts, ".ts": _scan_js_ts, ".tsx": _scan_js_ts, ".jsx": _scan_js_ts,
    ".css": _scan_css,
}


def scan_path(path, recursive=False):
    p = Path(path)
    results = {}
    if p.is_file():
        ext = p.suffix.lower()
        scanner = SCANNERS.get(ext)
        results[str(p)] = scanner(str(p)) if scanner else [f"INFO: Tipe file '{ext}' tidak di-scan otomatis."]
        return results
    if p.is_dir():
        for child in p.glob("**/*" if recursive else "*"):
            if child.is_file():
                scanner = SCANNERS.get(child.suffix.lower())
                if scanner:
                    results[str(child)] = scanner(str(child))
        return results
    return {"error": [f"Path tidak ditemukan: {path}"]}


def _find_free_port(start=8400):
    for port in range(start, start + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue
    return start

def _serve_directory(directory, port):
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *a: None
    os.chdir(directory)
    server = http.server.HTTPServer(("", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


async def handle_preview_tool(name, args):
    path      = args.get("path", ".")
    recursive = args.get("recursive", False)
    auto_open = args.get("auto_open", True)
    port      = args.get("port", None)

    if name == "preview_scan":
        results = scan_path(path, recursive=recursive)
        if not results:
            return "✓ Tidak ada file yang bisa di-scan di path tersebut."
        lines, total_e, total_w = [], 0, 0
        for fpath, errs in results.items():
            fname = os.path.relpath(fpath, path) if os.path.isdir(path) else os.path.basename(fpath)
            if not errs:
                lines.append(f"  ✓  {fname}")
            else:
                for e in errs:
                    icon = "✖" if e.startswith("ERROR") else "⚠" if e.startswith("WARNING") else "ℹ"
                    lines.append(f"  {icon}  {fname}  →  {e}")
                    if e.startswith("ERROR"): total_e += 1
                    elif e.startswith("WARNING"): total_w += 1
        return "\n".join(lines) + f"\n  Scan selesai: {total_e} error, {total_w} warning dari {len(results)} file."

    elif name == "preview_web":
        p = Path(path)
        if not p.exists():
            return f"✖ Path tidak ditemukan: {path}"
        if p.is_file() and p.suffix.lower() in (".html", ".htm"):
            serve_dir, entry_file = str(p.parent), p.name
        elif p.is_dir():
            serve_dir = str(p)
            entry_file = None
            for c in ["index.html", "index.htm", "public/index.html", "dist/index.html"]:
                if (p / c).exists():
                    entry_file = c
                    break
            if not entry_file:
                htmls = list(p.glob("*.html"))
                entry_file = htmls[0].name if htmls else None
            if not entry_file:
                return "✖ Tidak ada file HTML ditemukan di direktori ini."
        else:
            return f"✖ File '{path}' bukan HTML dan bukan direktori web."

        scan_result = scan_path(path, recursive=True)
        error_files = {f: e for f, e in scan_result.items() if any(x.startswith("ERROR") for x in e)}
        scan_summary = ""
        if error_files:
            scan_summary = "\n⚠ Ada error ditemukan saat scan:\n"
            for fpath, errs in error_files.items():
                for e in errs:
                    if e.startswith("ERROR"):
                        scan_summary += f"   ✖ {os.path.basename(fpath)}: {e}\n"
            scan_summary += "  Preview tetap dilanjutkan, tapi kode mungkin ga jalan dengan benar.\n"

        used_port = port or _find_free_port()
        try:
            _serve_directory(serve_dir, used_port)
        except Exception as e:
            return f"✖ Gagal start server: {e}"

        url = f"http://localhost:{used_port}/{entry_file}"
        try:
            if auto_open:
                webbrowser.open(url)
            open_msg = "  ↳ Browser dibuka otomatis." if auto_open else "  ↳ Auto-open dimatikan."
        except Exception:
            open_msg = "  ↳ Gagal buka browser otomatis. Buka manual ya."

        return (
            f"{scan_summary}"
            f"  ✓ Preview server aktif!\n"
            f"  ◆ URL  : {url}\n"
            f"  ◆ Port : {used_port}\n"
            f"  ◆ Dir  : {serve_dir}\n"
            f"{open_msg}\n"
            f"  ℹ Server berjalan di background. Ctrl+C untuk stop."
        )

    return f"Unknown preview tool: {name}"
