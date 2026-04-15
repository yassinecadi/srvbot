"""
modules/users/texts.py
─────────────────────────────────────────────
Text builders for the users module.
─────────────────────────────────────────────
"""

from ui.texts import active_icon
from modules.users.users import get_active_count


def build_users_list_text(user_list: list) -> str:
    active = get_active_count(user_list)
    return f"👥 *Users* — {active}/{len(user_list)} active\n\nSelect a user:"


def build_user_detail_text(u: dict) -> str:
    icon   = active_icon(u["active"])
    expiry = u["expires"] or "Never"
    return (
        f"{icon} *{u['username']}*\n\n"
        f"Expires    : {expiry}\n"
        f"Connections: {u['connections']}"
    )
