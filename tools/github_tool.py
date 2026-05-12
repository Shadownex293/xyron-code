import asyncio
import base64
import json
import os
from pathlib import Path

try:
    import httpx
    _HTTPX = True
except ImportError:
    _HTTPX = False

GITHUB_API = "https://api.github.com"

github_tools = [
    {
        "type": "function",
        "function": {
            "name": "github_create_repo",
            "description": "Buat repository GitHub baru.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":        {"type": "string",  "description": "Nama repo"},
                    "description": {"type": "string",  "description": "Deskripsi repo (opsional)"},
                    "private":     {"type": "boolean", "description": "Private repo? (default: false)"},
                    "auto_init":   {"type": "boolean", "description": "Init dengan README? (default: true)"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_list_repos",
            "description": "Tampilkan semua repository milik user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sort": {"type": "string", "description": "Sort by: updated, created, pushed, full_name (default: updated)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_upload_file",
            "description": "Upload satu file ke repository GitHub.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo":    {"type": "string", "description": "Nama repo (contoh: MyProject)"},
                    "path":    {"type": "string", "description": "Path file lokal yang mau diupload"},
                    "dest":    {"type": "string", "description": "Path tujuan di dalam repo (contoh: src/index.js). Kalau kosong, pakai nama file saja."},
                    "message": {"type": "string", "description": "Commit message (opsional, AI akan generate otomatis)"},
                    "branch":  {"type": "string", "description": "Branch tujuan (default: main)"},
                },
                "required": ["repo", "path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_upload_folder",
            "description": "Upload seluruh isi folder ke repository GitHub secara rekursif.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo":    {"type": "string", "description": "Nama repo tujuan"},
                    "folder":  {"type": "string", "description": "Path folder lokal yang mau diupload"},
                    "dest":    {"type": "string", "description": "Path tujuan di dalam repo (default: root '/')"},
                    "message": {"type": "string", "description": "Commit message"},
                    "branch":  {"type": "string", "description": "Branch tujuan (default: main)"},
                    "exclude": {"type": "array",  "description": "Daftar folder/file yang dikecualikan", "items": {"type": "string"}},
                },
                "required": ["repo", "folder"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_delete_repo",
            "description": "Hapus repository GitHub. HATI-HATI: permanen dan tidak bisa dibatalkan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Nama repo yang mau dihapus"},
                },
                "required": ["repo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_list_files",
            "description": "Lihat isi file/folder di dalam repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo":   {"type": "string", "description": "Nama repo"},
                    "path":   {"type": "string", "description": "Path di dalam repo (default: root)"},
                    "branch": {"type": "string", "description": "Branch (default: main)"},
                },
                "required": ["repo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_create_branch",
            "description": "Buat branch baru di repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo":   {"type": "string", "description": "Nama repo"},
                    "branch": {"type": "string", "description": "Nama branch baru"},
                    "from_branch": {"type": "string", "description": "Branch sumber (default: main)"},
                },
                "required": ["repo", "branch"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_whoami",
            "description": "Cek info akun GitHub yang sedang login (token aktif).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def _get_token() -> str:
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        return token
    config_file = Path.home() / ".xyron_codex" / "github.json"
    if config_file.exists():
        try:
            return json.loads(config_file.read_text()).get("token", "")
        except Exception:
            pass
    return ""

def _headers(token: str) -> dict:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "XyronCodex/1.0",
    }

async def _req(method: str, url: str, token: str, **kwargs):
    if _HTTPX:
        async with httpx.AsyncClient(timeout=30) as client:
            fn = getattr(client, method.lower())
            return await fn(url, headers=_headers(token), **kwargs)
    else:
        import urllib.request
        import urllib.error
        data = kwargs.get("json")
        body = json.dumps(data).encode() if data else None
        req  = urllib.request.Request(url, data=body, headers=_headers(token), method=method.upper())
        loop = asyncio.get_event_loop()
        def _sync():
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    class R:
                        status_code = r.status
                        def json(self): return json.loads(r.read().decode())
                        text = ""
                    return R()
            except urllib.error.HTTPError as e:
                class E:
                    status_code = e.code
                    def json(self): return json.loads(e.read().decode())
                    text = str(e)
                return E()
        return await loop.run_in_executor(None, _sync)

def _encode_file(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

async def _get_file_sha(repo: str, dest: str, branch: str, token: str, username: str) -> str | None:
    url = f"{GITHUB_API}/repos/{username}/{repo}/contents/{dest}"
    r   = await _req("GET", url, token, params={"ref": branch})
    if r.status_code == 200:
        return r.json().get("sha")
    return None

async def _get_username(token: str) -> str:
    r = await _req("GET", f"{GITHUB_API}/user", token)
    if r.status_code == 200:
        return r.json().get("login", "")
    return ""

DEFAULT_EXCLUDE = {
    ".git", "node_modules", "__pycache__", ".env", "venv",
    ".DS_Store", "*.pyc", ".idea", ".vscode", "dist", ".next",
}

def _should_exclude(path: Path, excludes: list) -> bool:
    all_ex = DEFAULT_EXCLUDE | set(excludes or [])
    for part in path.parts:
        if part in all_ex:
            return True
    for ex in all_ex:
        if "*" in ex and path.match(ex):
            return True
    return False

async def _upload_single(repo, local_path, dest_path, branch, message, token, username) -> tuple[bool, str]:
    sha     = await _get_file_sha(repo, dest_path, branch, token, username)
    content = _encode_file(local_path)
    payload = {"message": message, "content": content, "branch": branch}
    if sha:
        payload["sha"] = sha
    url = f"{GITHUB_API}/repos/{username}/{repo}/contents/{dest_path}"
    r   = await _req("PUT", url, token, json=payload)
    if r.status_code in (200, 201):
        html_url = r.json().get("content", {}).get("html_url", "")
        return True, html_url
    return False, r.json().get("message", r.text if hasattr(r, "text") else "")


async def handle_github_tool(name: str, args: dict) -> str:
    token = _get_token()
    if not token and name != "github_whoami":
        return (
            "✖ GitHub token belum diset!\n"
            "Jalankan perintah berikut untuk set token:\n"
            "  /github token <YOUR_GITHUB_PAT>\n\n"
            "Generate token di: https://github.com/settings/tokens\n"
            "Centang scope: repo, delete_repo"
        )

    if name == "github_whoami":
        if not token:
            return "✖ Token belum diset. Jalankan: /github token <TOKEN>"
        r = await _req("GET", f"{GITHUB_API}/user", token)
        if r.status_code != 200:
            return f"✖ Token tidak valid atau expired. ({r.status_code})"
        d = r.json()
        return (
            f"  ✓ Login sebagai: {d.get('login')}\n"
            f"  ◆ Nama    : {d.get('name', '-')}\n"
            f"  ◆ Email   : {d.get('email', '-')}\n"
            f"  ◆ Repo    : {d.get('public_repos', 0)} public, {d.get('total_private_repos', 0)} private\n"
            f"  ◆ Profile : {d.get('html_url')}"
        )

    username = await _get_username(token)
    if not username:
        return "✖ Gagal ambil info user dari token. Cek token lo masih valid."

    if name == "github_list_repos":
        sort = args.get("sort", "updated")
        r    = await _req("GET", f"{GITHUB_API}/user/repos", token, params={"sort": sort, "per_page": 50})
        if r.status_code != 200:
            return f"✖ Gagal ambil list repo: {r.json().get('message', '')}"
        repos = r.json()
        if not repos:
            return "  Belum ada repository."
        lines = [f"  Repository milik {username} ({len(repos)} repo):\n"]
        for rp in repos:
            vis = "🔒" if rp["private"] else "🌐"
            lines.append(f"  {vis} {rp['name']}")
            lines.append(f"      ⭐ {rp['stargazers_count']}  🍴 {rp['forks_count']}  {rp.get('language') or '-'}")
            lines.append(f"      {rp['html_url']}")
        return "\n".join(lines)

    if name == "github_create_repo":
        repo_name = args.get("name", "")
        payload   = {
            "name":        repo_name,
            "description": args.get("description", ""),
            "private":     args.get("private", False),
            "auto_init":   args.get("auto_init", True),
        }
        r = await _req("POST", f"{GITHUB_API}/user/repos", token, json=payload)
        if r.status_code == 201:
            d = r.json()
            return (
                f"  ✓ Repo berhasil dibuat!\n"
                f"  ◆ Nama    : {d['name']}\n"
                f"  ◆ Visibel : {'Private 🔒' if d['private'] else 'Public 🌐'}\n"
                f"  ◆ URL     : {d['html_url']}\n"
                f"  ◆ Clone   : git clone {d['clone_url']}"
            )
        return f"✖ Gagal buat repo: {r.json().get('message', '')}"

    if name == "github_delete_repo":
        repo = args.get("repo", "")
        r    = await _req("DELETE", f"{GITHUB_API}/repos/{username}/{repo}", token)
        if r.status_code == 204:
            return f"  ✓ Repo '{repo}' berhasil dihapus."
        return f"✖ Gagal hapus repo: {r.json().get('message', '')}"

    if name == "github_list_files":
        repo   = args.get("repo", "")
        path   = args.get("path", "")
        branch = args.get("branch", "main")
        url    = f"{GITHUB_API}/repos/{username}/{repo}/contents/{path}"
        r      = await _req("GET", url, token, params={"ref": branch})
        if r.status_code != 200:
            return f"✖ Gagal ambil isi repo: {r.json().get('message', '')}"
        items = r.json()
        if not isinstance(items, list):
            items = [items]
        lines = [f"  Isi /{path or ''} di {repo} ({branch}):\n"]
        for item in items:
            icon = "📁" if item["type"] == "dir" else "📄"
            size = f"  {item.get('size', 0)} bytes" if item["type"] == "file" else ""
            lines.append(f"  {icon} {item['name']}{size}")
        return "\n".join(lines)

    if name == "github_create_branch":
        repo        = args.get("repo", "")
        new_branch  = args.get("branch", "")
        from_branch = args.get("from_branch", "main")
        r_ref = await _req("GET", f"{GITHUB_API}/repos/{username}/{repo}/git/ref/heads/{from_branch}", token)
        if r_ref.status_code != 200:
            return f"✖ Branch '{from_branch}' tidak ditemukan di repo '{repo}'."
        sha = r_ref.json()["object"]["sha"]
        r   = await _req("POST", f"{GITHUB_API}/repos/{username}/{repo}/git/refs", token, json={
            "ref": f"refs/heads/{new_branch}", "sha": sha
        })
        if r.status_code == 201:
            return f"  ✓ Branch '{new_branch}' berhasil dibuat dari '{from_branch}'."
        return f"✖ Gagal buat branch: {r.json().get('message', '')}"

    if name == "github_upload_file":
        repo       = args.get("repo", "")
        local_path = args.get("path", "")
        dest       = args.get("dest", "") or Path(local_path).name
        branch     = args.get("branch", "main")
        message    = args.get("message", "") or f"Upload {Path(local_path).name} via Xyron Codex"

        if not Path(local_path).exists():
            return f"✖ File tidak ditemukan: {local_path}"

        ok, result = await _upload_single(repo, local_path, dest, branch, message, token, username)
        if ok:
            return f"  ✓ File berhasil diupload!\n  ◆ URL: {result}"
        return f"✖ Gagal upload: {result}"

    if name == "github_upload_folder":
        repo    = args.get("repo", "")
        folder  = args.get("folder", "")
        dest    = args.get("dest", "").strip("/")
        branch  = args.get("branch", "main")
        message = args.get("message", "") or f"Upload folder via Xyron Codex"
        exclude = args.get("exclude", [])

        folder_path = Path(folder)
        if not folder_path.exists() or not folder_path.is_dir():
            return f"✖ Folder tidak ditemukan: {folder}"

        all_files = [f for f in folder_path.rglob("*") if f.is_file() and not _should_exclude(f.relative_to(folder_path), exclude)]

        if not all_files:
            return "✖ Tidak ada file yang bisa diupload di folder ini."

        results    = []
        success    = 0
        fail       = 0

        for file_path in all_files:
            rel      = file_path.relative_to(folder_path)
            dest_key = f"{dest}/{rel}".strip("/") if dest else str(rel)
            dest_key = dest_key.replace("\\", "/")

            ok, result = await _upload_single(repo, str(file_path), dest_key, branch, f"{message}: {dest_key}", token, username)
            if ok:
                results.append(f"  ✓ {dest_key}")
                success += 1
            else:
                results.append(f"  ✖ {dest_key} — {result}")
                fail += 1

        summary = f"\n  Upload selesai: {success} berhasil, {fail} gagal dari {len(all_files)} file."
        repo_url = f"\n  ◆ Repo: https://github.com/{username}/{repo}"
        return "\n".join(results) + summary + repo_url

    return f"Unknown github tool: {name}"
