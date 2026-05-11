#!/usr/bin/env python3
import sys
import os
import asyncio
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from providers.factory import create_provider, get_available_providers, get_api_key_for_provider
from utils.config import get_config
from utils.session import SessionManager
from utils.cache import prompt_cache
from utils.tokenizer import estimate_tokens, truncate_to_budget
from utils.model_catalog import ModelCatalog
from utils.context_manager import ContextManager
from utils.retry import is_retryable_error
from utils.system_prompt import build_system_prompt
from utils.ui import (
    C, get_width, print_banner, print_user_box, print_ai_header,
    print_ai_footer, print_ai_footer_line, print_error_box, print_info_box,
    print_tool_badge, print_auto_continue_badge, print_retry_badge,
    parse_roadmap, print_roadmap_status, build_roadmap_continue_prompt,
    build_token_bar, create_spinner, stop_active_spinner,
    stream_chunk, stream_flush, model_selector, save_model_history,
)
from skills import detect_skills, SKILL_REGISTRY
from tools import ALL_TOOLS, execute_tool

MAX_AUTO_CONTINUE = 4


def clear_screen():
    """Clear terminal — cross-platform (Linux/Termux/Windows)."""
    os.system("cls" if os.name == "nt" else "clear")

def fuzzy_match_provider(query: str, providers: list) -> str | None:
    q = query.lower().replace(" ", "")
    exact = next((p for p in providers if p.lower() == q), None)
    if exact:
        return exact
    prefix = next((p for p in providers if p.lower().startswith(q)), None)
    if prefix:
        return prefix
    contains = next((p for p in providers if q in p.lower()), None)
    if contains:
        return contains
    return None


async def stream_with_auto_continue(provider, base_params: dict, state_ref: dict | None):
    auto_continues = 0
    current_params = {**base_params, "messages": list(base_params["messages"])}
    accumulated = ""

    while True:
        partial = ""
        tool_calls = None
        err = None

        try:
            async for chunk in provider.stream(**current_params):
                if chunk["type"] == "text":
                    stream_chunk(chunk["content"])
                    partial += chunk["content"]
                elif chunk["type"] == "thinking":
                    sys.stdout.write(C.dim("·"))
                    sys.stdout.flush()
                elif chunk["type"] == "thinking_end":
                    sys.stdout.write("\n  ")
                    sys.stdout.flush()
                elif chunk["type"] == "tool_calls":
                    tool_calls = chunk["content"]
                    partial = chunk.get("full_content", partial)

            stream_flush()
            print_ai_footer_line()
            accumulated += partial

            roadmap = parse_roadmap(accumulated)
            if roadmap and state_ref is not None:
                state_ref["roadmap"] = roadmap

            return {"response": accumulated, "tool_calls": tool_calls}

        except Exception as e:
            err = e
            stream_flush()
            print_ai_footer_line()
            accumulated += partial

        retryable = is_retryable_error(err)
        has_content = len(accumulated.strip()) > 30

        if not retryable or auto_continues >= MAX_AUTO_CONTINUE:
            sys.stdout.write(C.error(f"\n\n  ✖  {err}\n"))
            return {"response": accumulated, "tool_calls": None}

        auto_continues += 1

        if has_content:
            print_auto_continue_badge(auto_continues, MAX_AUTO_CONTINUE)
            roadmap = (state_ref or {}).get("roadmap") or parse_roadmap(accumulated)
            continue_msg = build_roadmap_continue_prompt(roadmap) if roadmap else "Please continue."
            current_params = {
                **base_params,
                "messages": [
                    *current_params["messages"],
                    {"role": "assistant", "content": accumulated},
                    {"role": "user", "content": continue_msg},
                ],
            }
            print_ai_header(provider.name, current_params.get("model", provider.default_model))
        else:
            delay_ms = 1500 * auto_continues
            print_retry_badge(auto_continues, MAX_AUTO_CONTINUE, delay_ms)
            await asyncio.sleep(delay_ms / 1000)



async def handle_command(raw: str, state: dict) -> dict:
    parts = raw[1:].strip().split()
    cmd   = parts[0] if parts else ""
    args  = parts[1:]

    if cmd == "help":
        lines = [
            "/help                   Show this help",
            "/provider <name>        Switch provider",
            "/model [id]             Set or pick model interactively",
            "/models                 List all available models",
            "/skills                 Show active skills",
            "/status                 Provider + model + token info",
            "/roadmap                Show current task roadmap",
            "/clear                  Clear conversation history",
            "/save [name]            Save session",
            "/load [name]            Load saved session",
            "/tokens                 Token usage bar",
            "/refresh                Refresh model catalog cache",
            "exit                    Quit",
        ]
        print_info_box("\n".join(lines), "COMMANDS")

    elif cmd == "provider":
        from utils.setup import maybe_change_provider
        result = maybe_change_provider()
        if result:
            sp = create_spinner("connecting")
            try:
                p = create_provider(result["provider"], result["api_key"])
                await p.validate()
                sp.stop()
                state["provider"] = p
                state["model"]    = result.get("model") or p.default_model
                state["thinking"] = "off"
                state["history"]  = []
                state["roadmap"]  = None
                cfg = get_config()
                print_banner(p.name, state["model"], cfg)
            except Exception as e:
                sp.stop()
                print_error_box(str(e))

    elif cmd == "model":
        if args:
            state["model"] = args[0]
            save_model_history(state["provider"].name, args[0])
            print(C.green(f"  ✓  Model: {args[0]}"))
        else:
            state["model"] = model_selector(state["provider"], state["model"])
            print(C.green(f"  ✓  Model: {state['model']}"))

    elif cmd == "models":
        sp = create_spinner("loading")
        try:
            catalog = ModelCatalog()
            models  = await catalog.get_models(state["provider"], state["provider"].name)
            sp.stop()
            lines = []
            for i, m in enumerate(models[:40]):
                cur = C.green(" ●") if m["id"] == state["model"] else "  "
                ctx = C.dim(f" {round(m['context_window'] / 1000)}K") if m.get("context_window") else ""
                lines.append(f"{cur} {str(i+1).rjust(2)}.  {m['id']}{ctx}")
            if len(models) > 40:
                lines.append(C.dim(f"  ... and {len(models) - 40} more"))
            print_info_box("\n".join(lines), f"MODELS  ·  {state['provider'].name.upper()}")
        except Exception as e:
            sp.stop()
            print_error_box(str(e))

    elif cmd == "status":
        cfg = get_config()
        est = estimate_tokens(json.dumps(state["history"]))
        pct = f"{(est / cfg['max_context_tokens']) * 100:.1f}"
        bar = build_token_bar(est, cfg["max_context_tokens"], 24)
        lines = [
            f"Provider    {state['provider'].name.upper()}",
            f"Model       {state['model']}",
            f"Thinking    {state['thinking']}",
            f"History     {len(state['history'])} messages",
            f"Tokens      {bar}  {est}/{cfg['max_context_tokens']}  ({pct}%)",
            f"Roadmap     {state['roadmap']['steps'][0]['label'] if state.get('roadmap') else 'none'}",
        ]
        print_info_box("\n".join(lines), "STATUS")

    elif cmd == "tokens":
        cfg = get_config()
        est = estimate_tokens(json.dumps(state["history"]))
        bar = build_token_bar(est, cfg["max_context_tokens"], 30)
        print(f"\n  {bar}  {C.white(str(est) + '/' + str(cfg['max_context_tokens']))}\n")

    elif cmd == "roadmap":
        if not state.get("roadmap"):
            print_info_box("No roadmap in current session. Start a complex task to generate one.", "ROADMAP")
        else:
            print_roadmap_status(state["roadmap"])

    elif cmd == "clear":
        state["history"] = []
        state["roadmap"] = None
        print(C.dim("  ✓  Conversation cleared."))

    elif cmd == "save":
        name = args[0] if args else "default"
        SessionManager(name).save(state["history"])
        print(C.green(f'  ✓  Session saved as "{name}".'))

    elif cmd == "load":
        name = args[0] if args else "default"
        loaded = SessionManager(name).load()
        state["history"] = loaded
        state["roadmap"] = None
        print(C.green(f'  ✓  Loaded {len(loaded)} messages from "{name}".'))

    elif cmd == "skills":
        if state.get("active_skills"):
            lines = [f"  ◆  {s['name']}" for s in state["active_skills"]]
        else:
            lines = ["  No skills active."]
        print_info_box("\n".join(lines), "SKILLS")

    elif cmd == "refresh":
        catalog = ModelCatalog()
        catalog.invalidate(state["provider"].name)
        print(C.green("  ✓  Model catalog cache cleared."))

    else:
        print_error_box(f"Unknown command: /{cmd}\nType /help for available commands.")

    return state



async def start_interactive():
    config = get_config()

    init_sp = create_spinner("connecting")
    try:
        provider = create_provider(config["provider"], config["api_key"])
        await provider.validate()
    except Exception as e:
        init_sp.stop()

        from utils.setup import run_setup_wizard, delete_saved_config
        delete_saved_config()
        print_error_box(f"Koneksi gagal: {e}\n  Config lama dihapus. Menjalankan setup ulang...")
        result = run_setup_wizard()
        from utils.config import _build
        config = _build(result["provider"], result["api_key"], result.get("model", "auto"))
        try:
            provider = create_provider(config["provider"], config["api_key"])
            await provider.validate()
        except Exception as e2:
            print_error_box(f"Masih gagal: {e2}")
            sys.exit(1)
    init_sp.stop()

    model = config["model"]
    if model == "auto" or not model:
        model = provider.default_model
        model = model_selector(provider, model)
    save_model_history(provider.name, model)

    state = {
        "provider":      provider,
        "model":         model,
        "thinking":      "off",
        "history":       [],
        "active_skills": [],
        "roadmap":       None,
        "last_partial":  "",
    }

    clear_screen()
    print_banner(provider.name, model, config)

    session = SessionManager("default")
    saved   = session.load()
    if saved:
        state["history"] = saved
        print(C.dim(f"  ↺  Session restored  ·  {len(saved)} messages"))

    context_mgr = ContextManager()

    while True:
        sys.stdout.write(C.orange("\n  ❯  "))
        sys.stdout.flush()
        try:
            raw_input = input()
        except (EOFError, KeyboardInterrupt):
            break

        if not raw_input.strip():
            continue
        if raw_input.lower() == "exit":
            break

        if raw_input.startswith("/"):
            state = await handle_command(raw_input, state)
            continue

        user_input = raw_input
        clear_screen()
        print_banner(state["provider"].name, state["model"], config)
        print_user_box(user_input)

        detected = detect_skills(user_input)
        if detected:
            state["active_skills"] = detected
            print(C.dim(f"  ◈  Skills: {'  ·  '.join(s['name'] for s in detected)}"))

        relevant_files = context_mgr.get_relevant_files(user_input)
        ctx_content = ""
        if relevant_files:
            print(C.dim(f"  ◈  Context: {' '.join(relevant_files[:3])}"))
            ctx_content = context_mgr.read_files(relevant_files)

        cache_key = f"sys_{provider.name}_{'_'.join(sorted(s['name'] for s in state['active_skills']))}"
        system_prompt = prompt_cache.get(cache_key)
        if not system_prompt:
            system_prompt = build_system_prompt(
                state["active_skills"],
                provider.get_system_prompt_appendix(),
            )
            prompt_cache.set(cache_key, system_prompt)

        user_content = (
            f"{user_input}\n\n<project-context>\n{ctx_content}\n</project-context>"
            if ctx_content else user_input
        )

        messages = [
            {"role": "system",  "content": system_prompt},
            *state["history"],
            {"role": "user",    "content": user_content},
        ]

        total_est = estimate_tokens(json.dumps(messages))
        if total_est > config["max_context_tokens"]:
            print(C.dim("  ⟳  Trimming history to fit context window..."))
            state["history"] = truncate_to_budget(
                state["history"],
                config["max_context_tokens"],
                estimate_tokens(system_prompt),
            )
            messages = [{"role": "system", "content": system_prompt}, *state["history"], {"role": "user", "content": user_content}]

        stream_params = {
            "messages":    messages,
            "tools":       ALL_TOOLS,
            "model":       state["model"],
            "temperature": config["temperature"],
            "max_tokens":  config["max_response_tokens"],
            "thinking":    state["thinking"],
        }

        gen_spinner  = create_spinner("thinking" if state["thinking"] != "off" else "streaming")
        gen_intercepted = False
        original_stream = provider.stream

        async def intercepted_stream(**params):
            nonlocal gen_intercepted
            async for chunk in original_stream(**params):
                if not gen_intercepted and chunk["type"] in ("text", "thinking"):
                    gen_spinner.stop()
                    print_ai_header(provider.name, state["model"])
                    gen_intercepted = True
                yield chunk

        provider.stream = intercepted_stream

        full_response = ""
        tool_calls    = None

        try:
            result       = await stream_with_auto_continue(provider, stream_params, state)
            full_response = result["response"]
            tool_calls    = result["tool_calls"]

            loop_count = 0
            while tool_calls and loop_count < 6:
                gen_spinner.stop()
                stop_active_spinner()
                stream_flush()

                messages.append({
                    "role":       "assistant",
                    "content":    full_response or None,
                    "tool_calls": tool_calls,
                })

                for tc in tool_calls:
                    tool_name = tc["function"].get("name", "")
                    try:
                        tool_args = json.loads(tc["function"].get("arguments", "{}"))
                    except Exception:
                        tool_args = {}

                    detail = tool_args.get("query") or tool_args.get("path") or (tool_args.get("urls") or [""])[0] or ""
                    print_tool_badge(tool_name, detail)

                    spinner_type = (
                        "tool_read"   if tool_name == "read_file" else
                        "tool_write"  if tool_name == "write_file" else
                        "tool_shell"  if tool_name == "execute_command" else
                        "tool_grep"   if tool_name == "search_codebase" else
                        "tool_generic"
                    )
                    tool_sp = create_spinner(spinner_type)

                    try:
                        tool_result = await execute_tool(tc, {"cwd": os.getcwd()})
                    except Exception as e:
                        tool_result = f"Error: {e}"

                    tool_sp.stop()
                    preview = str(tool_result)[:120].replace("\n", " ")
                    print(C.dim(f"  ↳  {preview}…"))
                    messages.append({
                        "role":         "tool",
                        "tool_call_id": tc.get("id", ""),
                        "content":      str(tool_result)[:4000],
                    })

                full_response  = ""
                tool_calls     = None
                gen_intercepted = False

                loop_sp = create_spinner("streaming")

                async def loop_intercepted_stream(**params):
                    nonlocal gen_intercepted
                    async for chunk in original_stream(**params):
                        if not gen_intercepted and chunk["type"] == "text":
                            loop_sp.stop()
                            print_ai_header(provider.name, state["model"])
                            gen_intercepted = True
                        yield chunk

                provider.stream = loop_intercepted_stream

                loop_result   = await stream_with_auto_continue(provider, {**stream_params, "messages": messages}, state)
                full_response = loop_result["response"]
                tool_calls    = loop_result["tool_calls"]
                loop_count   += 1

            state["last_partial"] = ""

        except Exception as e:
            gen_spinner.stop()
            print_error_box(str(e))
            state["last_partial"] = full_response
        finally:
            provider.stream = original_stream

        if gen_intercepted:
            stream_flush()
        print_ai_footer()

        if state.get("roadmap") and parse_roadmap(full_response):
            print_roadmap_status(state["roadmap"])

        if full_response or tool_calls:
            state["history"].append({"role": "user",      "content": user_input})
            state["history"].append({"role": "assistant", "content": full_response or "(tool actions)"})
            session.save(state["history"])

    session.save(state["history"])
    print(C.dim("\n  ✓  Session saved. Bye.\n"))



async def run_task(task: str, forced_skill: str = None):
    config   = get_config()
    provider = create_provider(config["provider"], config["api_key"])
    model    = config["model"] if config["model"] != "auto" else provider.default_model

    active_skills = []
    if forced_skill and forced_skill in SKILL_REGISTRY:
        active_skills = [SKILL_REGISTRY[forced_skill]]
    else:
        active_skills = detect_skills(task)

    context_mgr  = ContextManager()
    files        = context_mgr.get_relevant_files(task)
    ctx_content  = context_mgr.read_files(files)
    system_prompt = build_system_prompt(active_skills, provider.get_system_prompt_appendix())

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": f"{task}\n\n<project-context>\n{ctx_content}\n</project-context>" if ctx_content else task},
    ]

    print(C.dim(f"  Provider: {provider.name.upper()}  ·  Model: {model}\n"))
    print_ai_header(provider.name, model)

    result = await stream_with_auto_continue(provider, {
        "messages":    messages,
        "tools":       ALL_TOOLS,
        "model":       model,
        "temperature": config["temperature"],
        "max_tokens":  config["max_response_tokens"],
    }, None)

    stream_flush()
    print_ai_footer()
    print()
    sys.exit(0)



if __name__ == "__main__":
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
        asyncio.run(run_task(task))
    else:
        asyncio.run(start_interactive())