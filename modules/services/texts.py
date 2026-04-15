"""
modules/services/texts.py
─────────────────────────────────────────────
Text builders for the services module.
Sub-module detail lines are injected per service name.
─────────────────────────────────────────────
"""

from ui.texts import status_icon


def build_services_list_text() -> str:
    return "⚙️ *Services*\n\nSelect a service to manage:"


def build_service_detail_text(s: dict) -> str:
    """
    Base detail text + per-service extra lines.
    To add info for a new service: add elif block below.
    """
    icon  = status_icon(s["active"])
    lines = [
        f"⚙️ *{s['name']}*\n",
        f"Status : {icon} {s['state']} ({s['sub']})",
        f"PID    : `{s['pid']}`",
    ]

    # ── Per-service extra info ─────────────
    if s["name"] == "wsssh":
        from modules.services.wsssh.wsssh import get_banner
        lines.append(f"Banner : `{get_banner()}`")

    elif s["name"] == "telegram-srvbot":
        import config
        lines.append(f"Admin  : `{config.ADMIN_ID}`")

    return "\n".join(lines)


def build_action_result(name: str, ok: bool, msg: str) -> str:
    """One-line result shown above service detail after an action."""
    return f"{'✅' if ok else '❌'} {name}: {msg}\n\n"
