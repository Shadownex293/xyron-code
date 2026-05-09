import json

def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, len(text) // 4)

def truncate_to_budget(history: list, max_tokens: int, system_tokens: int) -> list:
    available = max_tokens - system_tokens
    truncated = []
    for msg in reversed(history):
        msg_tokens = estimate_tokens(json.dumps(msg))
        if available - msg_tokens < 0:
            break
        truncated.insert(0, msg)
        available -= msg_tokens
    return truncated
