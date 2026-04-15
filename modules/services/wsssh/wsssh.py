"""
modules/services/wsssh/wsssh.py
─────────────────────────────────────────────
wsssh-specific logic: read and update banner.
Pure logic — no Telegram imports.
─────────────────────────────────────────────
"""

import re
import os
from modules.services.services import restart_service

# Try multiple possible config locations
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
        return f"config.yaml not found (checked: {', '.join(_POSSIBLE_PATHS)})"
    try:
        with open(path) as f:
            content = f.read()
        match = re.search(r'custom_response_text:\s*"([^"]*)"', content)
        return match.group(1) if match else "Not set"
    except Exception as e:
        return f"Error: {e}"


def set_banner(new_banner: str) -> tuple:
    """Update banner in wsssh config.yaml and restart service."""
    path = _find_config()
    if not path:
        return False, f"wsssh config.yaml not found. Checked:\n" + "\n".join(_POSSIBLE_PATHS)
    try:
        with open(path) as f:
            content = f.read()
        if 'custom_response_text' not in content:
            return False, "custom_response_text key not found in config.yaml"
        updated = re.sub(
            r'(custom_response_text:\s*)"[^"]*"',
            f'\\1"{new_banner}"',
            content
        )
        with open(path, "w") as f:
            f.write(updated)
        restart_service("wsssh")
        return True, f"Banner updated — wsssh restarted\nConfig: {path}"
    except Exception as e:
        return False, str(e)


def get_config_path() -> str:
    """Return the detected config path for display."""
    path = _find_config()
    return path or "Not found"
