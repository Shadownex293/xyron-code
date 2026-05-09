def is_retryable_error(err: Exception) -> bool:
    if not err:
        return False
    msg = str(err).lower()
    code = getattr(err, "code", "") or ""
    status = getattr(err, "status_code", 0) or 0
    return (
        "connection" in msg
        or "premature close" in msg
        or "network" in msg
        or "timeout" in msg
        or "reset" in msg
        or "refused" in msg
        or status in (502, 503, 529)
    )
