"""
modules/services/srvbot/srvbot.py
─────────────────────────────────────────────
Bot self-management: add/remove admin IDs.
Pure logic — no Telegram imports.
─────────────────────────────────────────────
"""

import re
import config
from modules.services.services import restart_service

BOT_CONFIG = "/root/bots/srvbot/config.py"


def get_admins() -> list:
    """Return current admin IDs as a list."""
    admin = config.ADMIN_ID
    return admin if isinstance(admin, list) else [admin]


def add_admin(new_id: int) -> tuple:
    """
    Add a Telegram user ID to ADMIN_ID in config.py.
    Handles both single int and list formats.
    Restarts the bot service after saving.
    """
    try:
        with open(BOT_CONFIG) as f:
            content = f.read()

        list_match = re.search(r'ADMIN_ID\s*=\s*\[([^\]]*)\]', content)
        int_match  = re.search(r'ADMIN_ID\s*=\s*(\d+)', content)

        if list_match:
            ids = [x.strip() for x in list_match.group(1).split(",") if x.strip()]
            if str(new_id) in ids:
                return False, f"{new_id} is already an admin"
            ids.append(str(new_id))
            updated = re.sub(
                r'ADMIN_ID\s*=\s*\[[^\]]*\]',
                f'ADMIN_ID = [{", ".join(ids)}]',
                content
            )
        elif int_match:
            existing = int_match.group(1)
            if existing == str(new_id):
                return False, f"{new_id} is already the admin"
            updated = re.sub(
                r'ADMIN_ID\s*=\s*\d+',
                f'ADMIN_ID = [{existing}, {new_id}]',
                content
            )
        else:
            return False, "Could not parse ADMIN_ID in config.py"

        with open(BOT_CONFIG, "w") as f:
            f.write(updated)

        restart_service("telegram-srvbot")
        return True, f"Admin {new_id} added — bot restarting"

    except Exception as e:
        return False, str(e)
