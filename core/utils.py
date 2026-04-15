"""
core/utils.py
─────────────────────────────────────────────
Shared utility functions used across modules.
─────────────────────────────────────────────
"""


def fmt_bytes(n: int, human: bool = True) -> str:
    """Format byte count into human-readable string."""
    if not human or n < 1024:
        return f"{n}B"
    if n < 1024 ** 2:
        return f"{n / 1024:.1f}KB"
    if n < 1024 ** 3:
        return f"{n / 1024 ** 2:.1f}MB"
    return f"{n / 1024 ** 3:.2f}GB"


def fmt_duration(seconds: float) -> str:
    """Format seconds into Xh Xm Xs string."""
    h, rem = divmod(int(seconds), 3600)
    m, s   = divmod(rem, 60)
    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def run_cmd(cmd: list) -> tuple:
    """
    Run a shell command, return (returncode, combined_output).
    Used by services and users modules.
    """
    import subprocess
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()
