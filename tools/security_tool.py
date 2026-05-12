
import asyncio
import re
from urllib.parse import urljoin, urlparse

security_tools = [
    {
        "type": "function",
        "function": {
            "name": "security_scan_url",
            "description": (
                "Scan keamanan website yang sudah di-deploy. "
                "Fetch HTML, JavaScript, dan CSS dari URL target, "
                "lalu analisis semua konten untuk menemukan celah keamanan. "
                "Gunakan tool ini setiap kali user memberikan URL untuk di-scan."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL website yang mau di-scan (harus lengkap dengan https:// atau http://)",
                    },
                    "deep": {
                        "type": "boolean",
                        "description": "Fetch juga file JS/CSS external yang direferensikan (default: true)",
                    },
                    "follow_links": {
                        "type": "boolean",
                        "description": "Ikuti internal links untuk scan lebih dalam (default: false, max 3 halaman)",
                    },
                },
                "required": ["url"],
            },
        },
    },
]




async def _fetch(session, url: str, timeout: int = 15) -> tuple[str, str]:

    try:
        import aiohttp
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout), ssl=False) as resp:
            ct = resp.headers.get("Content-Type", "")

            return await resp.text(errors="replace"), ct, dict(resp.headers)
    except ImportError:
        pass


    import urllib.request
    import urllib.error
    loop = asyncio.get_event_loop()

    def _sync_fetch():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "XyronSecurity/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                ct = r.headers.get("Content-Type", "")
                headers = dict(r.headers)
                return r.read().decode("utf-8", errors="replace"), ct, headers
        except Exception as e:
            return f"[FETCH ERROR: {e}]", "", {}

    return await loop.run_in_executor(None, _sync_fetch)


def _extract_scripts(html: str, base_url: str) -> list[str]:
    
    pattern = re.compile(r'<script[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
    urls = []
    for match in pattern.finditer(html):
        src = match.group(1)
        if src.startswith("http"):
            urls.append(src)
        elif not src.startswith("data:"):
            urls.append(urljoin(base_url, src))
    return urls


def _extract_styles(html: str, base_url: str) -> list[str]:

    pattern = re.compile(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>', re.IGNORECASE)
    urls = []
    for match in pattern.finditer(html):
        href = match.group(1)
        if "stylesheet" in match.group(0).lower() or ".css" in href:
            if href.startswith("http"):
                urls.append(href)
            elif not href.startswith("data:"):
                urls.append(urljoin(base_url, href))
    return urls


def _extract_internal_links(html: str, base_url: str) -> list[str]:

    base_domain = urlparse(base_url).netloc
    pattern = re.compile(r'<a[^>]+href=["\']([^"\'#?]+)["\']', re.IGNORECASE)
    links = []
    for match in pattern.finditer(html):
        href = match.group(1)
        if href.startswith("http"):
            if urlparse(href).netloc == base_domain:
                links.append(href)
        elif href.startswith("/") and not href.startswith("//"):
            links.append(urljoin(base_url, href))
    return list(set(links))[:5]


def _extract_inline_scripts(html: str) -> str:

    pattern = re.compile(r'<script(?![^>]*src)[^>]*>(.*?)</script>', re.IGNORECASE | re.DOTALL)
    scripts = pattern.findall(html)
    return "\n\n".join(scripts)


def _check_security_headers(headers: dict) -> list[str]:

    findings = []
    headers_lower = {k.lower(): v for k, v in headers.items()}

    checks = [
        ("content-security-policy",       "🟡 MEDIUM — Missing Content-Security-Policy (CSP) header"),
        ("x-frame-options",                "🟡 MEDIUM — Missing X-Frame-Options header (Clickjacking risk)"),
        ("x-content-type-options",         "🔵 LOW    — Missing X-Content-Type-Options header"),
        ("strict-transport-security",      "🟡 MEDIUM — Missing HSTS header (Strict-Transport-Security)"),
        ("referrer-policy",                "🔵 LOW    — Missing Referrer-Policy header"),
        ("permissions-policy",             "🔵 LOW    — Missing Permissions-Policy header"),
        ("x-xss-protection",               "🔵 LOW    — Missing X-XSS-Protection header"),
    ]

    for header_name, message in checks:
        if header_name not in headers_lower:
            findings.append(message)


    csp = headers_lower.get("content-security-policy", "")
    if csp and "unsafe-inline" in csp:
        findings.append("🟠 HIGH   — CSP menggunakan 'unsafe-inline' yang melemahkan proteksi XSS")
    if csp and "unsafe-eval" in csp:
        findings.append("🟠 HIGH   — CSP menggunakan 'unsafe-eval' yang berbahaya")


    acao = headers_lower.get("access-control-allow-origin", "")
    if acao == "*":
        findings.append("🟡 MEDIUM — Access-Control-Allow-Origin: * (terlalu permisif)")

    return findings


def _truncate(text: str, max_chars: int = 8000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n... [dipotong, total {len(text)} karakter]"




async def handle_security_tool(name: str, args: dict) -> str:
    if name != "security_scan_url":
        return f"Unknown security tool: {name}"

    url          = args.get("url", "").strip()
    deep         = args.get("deep", True)
    follow_links = args.get("follow_links", False)

    if not url:
        return "✖ URL tidak boleh kosong."
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    result_parts = []
    result_parts.append(f"=== XYRON SECURITY SCAN ===")
    result_parts.append(f"Target URL : {url}")
    result_parts.append(f"Mode       : {'Deep (JS+CSS)' if deep else 'HTML only'}\n")

    
    try:
        import aiohttp
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(
            connector=connector,
            headers={"User-Agent": "Mozilla/5.0 (XyronSecurity/1.0)"}
        ) as session:
            html, ct, headers = await _fetch(session, url)

            result_parts.append("── RESPONSE HEADERS ──")
            important_headers = [
                "content-security-policy", "x-frame-options", "x-content-type-options",
                "strict-transport-security", "referrer-policy", "access-control-allow-origin",
                "x-xss-protection", "permissions-policy", "set-cookie", "server", "x-powered-by"
            ]
            headers_lower = {k.lower(): v for k, v in headers.items()}
            for h in important_headers:
                if h in headers_lower:
                    result_parts.append(f"  {h}: {headers_lower[h]}")
                else:
                    result_parts.append(f"  {h}: [TIDAK ADA]")

            if "server" in headers_lower:
                result_parts.append(f"\n── SERVER FINGERPRINT ──")
                result_parts.append(f"  Server    : {headers_lower.get('server', '-')}")
                result_parts.append(f"  Powered by: {headers_lower.get('x-powered-by', '-')}")


            header_findings = _check_security_headers(headers)
            if header_findings:
                result_parts.append(f"\n── SECURITY HEADER ISSUES ({len(header_findings)} ditemukan) ──")
                for f in header_findings:
                    result_parts.append(f"  {f}")


            result_parts.append(f"\n── HTML CONTENT ({len(html)} chars) ──")
            result_parts.append(_truncate(html, 6000))


            inline_js = _extract_inline_scripts(html)
            if inline_js.strip():
                result_parts.append(f"\n── INLINE JAVASCRIPT ──")
                result_parts.append(_truncate(inline_js, 4000))


            if deep:
                script_urls = _extract_scripts(html, url)[:6]
                style_urls  = _extract_styles(html, url)[:4]

                if script_urls:
                    result_parts.append(f"\n── EXTERNAL SCRIPTS ({len(script_urls)} files) ──")
                    for surl in script_urls:
                        result_parts.append(f"  → {surl}")
                        try:
                            js_content, _, _ = await _fetch(session, surl, timeout=10)
                            result_parts.append(_truncate(js_content, 3000))
                        except Exception as e:
                            result_parts.append(f"  [gagal fetch: {e}]")

                if style_urls:
                    result_parts.append(f"\n── EXTERNAL CSS ({len(style_urls)} files) ──")
                    for curl in style_urls:
                        result_parts.append(f"  → {curl}")
                        try:
                            css_content, _, _ = await _fetch(session, curl, timeout=10)
                            result_parts.append(_truncate(css_content, 1500))
                        except Exception as e:
                            result_parts.append(f"  [gagal fetch: {e}]")


            if follow_links:
                internal = _extract_internal_links(html, url)[:3]
                if internal:
                    result_parts.append(f"\n── INTERNAL PAGES SCANNED ──")
                    for iurl in internal:
                        result_parts.append(f"\n  Halaman: {iurl}")
                        try:
                            page_html, _, page_headers = await _fetch(session, iurl, timeout=10)
                            page_inline = _extract_inline_scripts(page_html)
                            result_parts.append(_truncate(page_html, 2000))
                            if page_inline.strip():
                                result_parts.append("  [Inline JS]")
                                result_parts.append(_truncate(page_inline, 1500))
                        except Exception as e:
                            result_parts.append(f"  [gagal fetch: {e}]")

    except ImportError:

        result_parts.append("[INFO: aiohttp tidak tersedia, pakai urllib fallback]\n")
        loop = asyncio.get_event_loop()

        def _sync_fetch_simple(target_url):
            import urllib.request
            try:
                req = urllib.request.Request(
                    target_url,
                    headers={"User-Agent": "Mozilla/5.0 (XyronSecurity/1.0)"}
                )
                with urllib.request.urlopen(req, timeout=15) as r:
                    return r.read().decode("utf-8", errors="replace"), dict(r.headers)
            except Exception as e:
                return f"[FETCH ERROR: {e}]", {}

        html, headers = await loop.run_in_executor(None, _sync_fetch_simple, url)

        header_findings = _check_security_headers(headers)
        result_parts.append("── RESPONSE HEADERS ──")
        for k, v in list(headers.items())[:15]:
            result_parts.append(f"  {k}: {v}")

        if header_findings:
            result_parts.append(f"\n── SECURITY HEADER ISSUES ──")
            for f in header_findings:
                result_parts.append(f"  {f}")

        result_parts.append(f"\n── HTML CONTENT ──")
        result_parts.append(_truncate(html, 6000))

        inline_js = _extract_inline_scripts(html)
        if inline_js.strip():
            result_parts.append(f"\n── INLINE JAVASCRIPT ──")
            result_parts.append(_truncate(inline_js, 4000))

    except Exception as e:
        result_parts.append(f"\n✖ Gagal fetch URL: {e}")
        result_parts.append("Kemungkinan penyebab:")
        result_parts.append("  - URL salah atau tidak bisa diakses")
        result_parts.append("  - Website memblokir bot/scraper")
        result_parts.append("  - Timeout (website terlalu lambat)")

    result_parts.append(f"\n=== END OF SCAN DATA ===")
    result_parts.append("Analisis celah keamanan berdasarkan data di atas sekarang.")

    return "\n".join(result_parts)
