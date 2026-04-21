"""
modules/services/wsssh/wsssh.py
─────────────────────────────────────────────
wsssh-specific logic: read current banner for display.
Pure logic — no Telegram imports.
─────────────────────────────────────────────
"""

import re
import os

_POSSIBLE_PATHS = [
    "/root/wsssh/config.yaml",
    "/root/bots/wsssh/config.yaml",
]


def _find_config() -> str | None:
    for path in _POSSIBLE_PATHS:
        if os.path.exists(path):
            return path
    return None


def get_banner() -> str:
    """Read current banner from wsssh config.yaml."""
    path = _find_config()
    if not path:
        return "Not found"
    try:
        with open(path) as f:
            content = f.read()
        match = re.search(r'custom_response_text:\s*"([^"]*)"', content)
        return match.group(1) if match else "Not set"
    except Exception as e:
        return f"Error: {e}"


def get_config_path() -> str:
    path = _find_config()
    return path or "Not found"
