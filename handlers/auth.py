"""
handlers/auth.py
────────────────────────────────────────────────────────────────
Admin authentication helpers.
Supports single int or list of ints in config.ADMIN_ID.
────────────────────────────────────────────────────────────────
"""

from telegram import Update
import config


def is_admin(uid: int) -> bool:
    """Check if Telegram user ID is in the admin list."""
    admin = config.ADMIN_ID
    if isinstance(admin, list):
        return uid in admin
    return uid == admin


async def check_admin(update: Update) -> bool:
    """
    Guard for command handlers.
    Replies with ⛔ if not admin and returns False.
    """
    uid = update.effective_user.id if update.effective_user else None
    if not uid or not is_admin(uid):
        if update.message:
            await update.message.reply_text("⛔ Unauthorized")
        return False
    return True
