"""
modules/services/wsssh/texts.py
─────────────────────────────────────────────
Text builders specific to wsssh.
─────────────────────────────────────────────
"""

from modules.services.wsssh.wsssh import get_banner, get_config_path


def build_banner_prompt_text() -> str:
    current = get_banner()
    path    = get_config_path()
    return (
        "✏️ *Change WebSocket Banner*\n\n"
        f"Config: `{path}`\n"
        f"Current: `{current}`\n\n"
        "Send new banner text:\n\n"
        "/cancel to go back"
    )
