"""
core/auth.py
─────────────────────────────────────────────
Admin authentication.
Supports single int or list of ints in config.ADMIN_ID.
─────────────────────────────────────────────
"""

from telegram import Update
import config


def is_admin(uid: int) -> bool:
    """Return True if uid is in the admin list."""
    admin = config.ADMIN_ID
    if isinstance(admin, list):
        return uid in admin
    return uid == admin


async def check_admin(update: Update) -> bool:
    """
    Guard for command and message handlers.
    Sends ⛔ reply and returns False if not admin.
    """
    uid = update.effective_user.id if update.effective_user else None
    if not uid or not is_admin(uid):
        if update.message:
            await update.message.reply_text("⛔ Unauthorized")
        return False
    return True
