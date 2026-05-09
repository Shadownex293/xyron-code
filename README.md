# Xyron Code

**Terminal AI Coding Assistant — built in Python**

Xyron Code adalah AI coding assistant yang jalan langsung di terminal. Multi-provider, streaming real-time, bisa baca & tulis file, jalankan shell command, dan search web — semua dari satu sesi CLI. Dibangun untuk developer yang kerja di environment terbatas termasuk **Termux Android**.

---

## Features

- **Multi-provider** — 13 AI provider didukung (Gemini, Groq, DeepSeek, OpenRouter, Mistral, xAI, Cerebras, SambaNova, Together, NVIDIA NIM, Kimi, Qwen, MiniMax)
- **Streaming real-time** — response muncul karakter demi karakter, auto-continue kalau kepotong
- **Built-in tools** — baca/tulis file, jalankan shell command, grep codebase, web search & fetch
- **Skill detection** — otomatis detect context: frontend, backend, security audit, refactor
- **Session memory** — conversation tersimpan otomatis, bisa resume kapanpun
- **Task roadmap** — untuk task kompleks, AI buat roadmap dan track progress
- **Setup wizard** — pilih provider & input API key lewat wizard interaktif saat pertama run
- **Termux-friendly** — install script detect environment Termux otomatis

---

## Install

```bash
# 1. Clone repo
git clone https://github.com/ShadowNex293/xyron-code.git
cd xyron-code

# 2. Jalankan install script
bash install.sh

# 3. Aktifkan PATH kalau diminta (non-Termux)
export PATH="$HOME/.local/bin:$PATH"

# 4. Jalankan
xyroncode
```

> **Termux:** `bash install.sh` otomatis detect, langsung bisa tanpa export PATH.

---

## Setup API Key

Saat pertama run, wizard interaktif akan muncul:

```
  ◆  Pilih provider AI

   1.  Gemini      [Google]       Free — 1500 req/day
   2.  Groq        [Groq]         Free — 1M tokens/day
   3.  DeepSeek    [DeepSeek AI]  V3 & R1 — sangat murah
   4.  OpenRouter               500+ models
   ...

  ❯  Pilih nomor:
```

Pilih provider → masukkan API key → pilih simpan atau sesi ini saja. Selesai.

Config tersimpan di `~/.xyron-code/config.json`.

---

## Providers

| Provider | Env Key | Keterangan |
|---|---|---|
| Gemini | `GEMINI_API_KEY` | Free — 1500 req/day |
| Groq | `GROQ_API_KEY` | Free — 1M tokens/day |
| DeepSeek | `DEEPSEEK_API_KEY` | V3 & R1, sangat murah |
| Cerebras | `CEREBRAS_API_KEY` | Free — 1M tokens/day |
| Mistral | `MISTRAL_API_KEY` | Free — 1B tokens/month |
| SambaNova | `SAMBANOVA_API_KEY` | Free tier |
| OpenRouter | `OPENROUTER_API_KEY` | 500+ model, ada yang gratis |
| xAI | `XAI_API_KEY` | $25 signup credits |
| Together AI | `TOGETHER_API_KEY` | ~$100 signup credits |
| NVIDIA NIM | `NVIDIA_NIM_API_KEY` | Free credits |
| Kimi | `KIMI_API_KEY` | Trial credits |
| Qwen | `QWEN_API_KEY` | Trial credits |
| MiniMax | `MINIMAX_API_KEY` | Trial credits |

---

## Commands

| Command | Fungsi |
|---|---|
| `/help` | Tampilkan semua command |
| `/provider` | Ganti AI provider via wizard |
| `/model [id]` | Pilih model secara interaktif |
| `/models` | List semua model dari provider aktif |
| `/status` | Info provider, model, dan token usage |
| `/roadmap` | Tampilkan task roadmap sesi ini |
| `/skills` | Lihat skill mode yang aktif |
| `/clear` | Reset conversation history |
| `/save [nama]` | Simpan sesi ke file |
| `/load [nama]` | Load sesi yang tersimpan |
| `/tokens` | Bar penggunaan token context window |
| `/refresh` | Clear cache model catalog |
| `exit` | Keluar |

---

## Tools

AI bisa menggunakan tools berikut secara otomatis:

| Tool | Fungsi |
|---|---|
| `read_file` | Baca isi file |
| `write_file` | Tulis atau overwrite file |
| `list_directory` | List isi direktori |
| `execute_command` | Jalankan shell command |
| `search_codebase` | Grep pattern di codebase |
| `web_search` | Search web via Tavily |
| `web_fetch` | Fetch konten dari URL |

> Web search & fetch butuh `TAVILY_API_KEY` (gratis 1000 req/month di [app.tavily.com](https://app.tavily.com))

---

## Skills (Auto-detect)

| Skill | Trigger Keywords |
|---|---|
| **frontend-design** | ui, react, html, css, component, interface |
| **backend-architect** | api, server, route, database, auth, endpoint |
| **security-auditor** | security, audit, vulnerability, review |
| **refactor-master** | refactor, clean, optimize, simplify |

---

## Structure

```
xyron-code/
├── xyron_code.py            ← entry point + REPL
├── install.sh               ← install script
├── providers/
│   ├── base.py
│   ├── groq_provider.py
│   ├── openrouter_provider.py
│   ├── other_providers.py   ← semua provider lainnya
│   └── factory.py
├── tools/
│   ├── file_ops.py
│   ├── shell_tool.py
│   ├── search_tool.py
│   └── web_fetch.py
├── skills/
│   ├── frontend.py
│   ├── backend.py
│   ├── security.py
│   └── refactor.py
├── utils/
│   ├── config.py
│   ├── setup.py             ← wizard interaktif
│   ├── session.py
│   ├── cache.py
│   ├── tokenizer.py
│   ├── retry.py
│   ├── model_catalog.py
│   ├── context_manager.py
│   ├── system_prompt.py
│   └── ui.py
└── docs/
    └── index.html           ← landing page
```

---

## Dependencies

Hanya 3 package:

```bash
pip install httpx python-dotenv rich
```

---

## Reset

```bash
# Ganti provider lewat dalam sesi:
/provider

# Atau reset total:
rm ~/.xyron-code/config.json
xyroncode
```

---

## By

**ShadowNex** — [@TELEGRAM DEVELOPER](https://t.me/SHADOWNEX2) · [GitHub Developer](https://github.com/ShadowNex293) · [TikTok](https://tiktok.com/@mr.shadownex) · [Saweria](https://saweria.co/shadownex)
