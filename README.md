<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=32&duration=3000&pause=1000&color=A78BFA&center=true&vCenter=true&width=500&lines=Xyron+Code;Terminal+AI+Assistant;by+ShadowNex" alt="Xyron Code" />

<br/>

![Preview](https://github.com/Shadownex293/xyron-code/blob/main/Screenshot_20260510-012715.jpg)

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-a78bfa?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Providers](https://img.shields.io/badge/Providers-13-22d3ee?style=flat-square)](https://github.com/Shadownex293/xyron-code)
[![Platform](https://img.shields.io/badge/Termux-Android-4ade80?style=flat-square&logo=android&logoColor=white)](https://github.com/Shadownex293/xyron-code)
[![License](https://img.shields.io/badge/License-MIT-fb923c?style=flat-square)](https://github.com/Shadownex293/xyron-code)
<img src="https://img.shields.io/badge/Version-1.0-blue?style=for-the-badge&logo=linux">

**Terminal AI Coding Assistant — built in Python**

</div>

---

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
xyroncodex
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

| Tool | Fungsi |
|---|---|
| `read_file` | Baca isi file |
| `write_file` | Tulis atau overwrite file |
| `list_directory` | List isi direktori |
| `execute_command` | Jalankan shell command |
| `search_codebase` | Grep pattern di codebase |
| `web_search` | Search web via Tavily |
| `web_fetch` | Fetch konten dari URL |

> Web search & fetch butuh `TAVILY_API_KEY` — gratis 1000 req/month di [app.tavily.com](https://app.tavily.com)

---

## Skills

| Skill | Trigger |
|---|---|
| **frontend-design** | ui, react, html, css, component |
| **backend-architect** | api, server, route, database, auth |
| **security-auditor** | security, audit, vulnerability |
| **refactor-master** | refactor, clean, optimize |

---

## Structure

```
xyron-code/
├── xyron_code.py
├── install.sh
├── providers/
├── tools/
├── skills/
├── utils/
└── docs/
    └── index.html
```

---

## Dependencies

```bash
pip install httpx python-dotenv rich
```

---

## Reset

```bash
# Ganti provider di dalam sesi:
/provider

# Reset total:
rm ~/.xyron-code/config.json && xyroncode
```

---

<div align="center">

**by ShadowNex**

[![Telegram](https://img.shields.io/badge/Telegram-@SHADOWNEX2-a78bfa?style=flat-square&logo=telegram&logoColor=white)](https://t.me/SHADOWNEX2)
[![GitHub](https://img.shields.io/badge/GitHub-ShadowNex293-22d3ee?style=flat-square&logo=github&logoColor=white)](https://github.com/ShadowNex293)
[![TikTok](https://img.shields.io/badge/TikTok-@mr.shadownex-4ade80?style=flat-square&logo=tiktok&logoColor=white)](https://tiktok.com/@mr.shadownex)
[![Saweria](https://img.shields.io/badge/Saweria-Support-fb923c?style=flat-square)](https://saweria.co/shadownex)
[![WhatsApp Channel](https://img.shields.io/badge/WhatsApp-Channel-25D366?style=flat-square&logo=whatsapp&logoColor=white)](https://whatsapp.com/channel/0029Vb8Lge5FHWq3fTan4V0J)

</div>
