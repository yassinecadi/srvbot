"""
modules/services/wsssh/wsssh.py
─────────────────────────────────────────────
wsssh-specific logic: read and update banner.
Pure logic — no Telegram imports.
─────────────────────────────────────────────
"""

import re
import os
import config
from modules.services.services import restart_service

# Try multiple possible config locations
_POSSIBLE_PATHS = [
    "/root/wsssh/config.yaml",
    "/root/bots/wsssh/config.yaml",
]

_SSH_BANNER_PATH = "/etc/ssh/banner.txt"


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


def _write_ssh_banner(msg: str) -> None:
    """Rewrite /etc/ssh/banner.txt using message + domain from config."""
    try:
        domain = getattr(config, "DOMAIN", "")
        lines = [
            "╔══════════════════════════════════════════╗\n",
            f"║  {msg}\n",
        ]
        if domain:
            lines.append(f"║  Domain  : {domain}\n")
        lines.append("╚══════════════════════════════════════════╝\n")
        with open(_SSH_BANNER_PATH, "w") as f:
            f.writelines(lines)
    except Exception:
        pass  # best-effort; SSH banner is not critical to fail the whole operation


def set_banner(new_banner: str) -> tuple:
    """Update banner in wsssh config.yaml and /etc/ssh/banner.txt, then restart service."""
    path = _find_config()
    if not path:
        return False, "wsssh config.yaml not found. Checked:\n" + "\n".join(_POSSIBLE_PATHS)
    try:
        with open(path) as f:
            content = f.read()
        if 'custom_response_text' not in content:
            return False, "custom_response_text key not found in config.yaml"
        updated = re.sub(
            r'(custom_response_text:\s*)"[^"]*"',
            lambda m: f'{m.group(1)}"{new_banner}"',
            content
        )
        if updated == content:
            return False, 'Pattern not matched — config.yaml must have: custom_response_text: "..."'
        with open(path, "w") as f:
            f.write(updated)
        _write_ssh_banner(new_banner)
        restart_service("wsssh")
        return True, f"Banner updated — wsssh restarted\nConfig: {path}"
    except Exception as e:
        return False, str(e)


def get_config_path() -> str:
    """Return the detected config path for display."""
    path = _find_config()
    return path or "Not found"
