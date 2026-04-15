"""
modules/services/wsssh/keyboards.py
─────────────────────────────────────────────
Extra keyboard rows injected into the wsssh detail page.
Returns a list of rows (not a full InlineKeyboardMarkup)
so services/keyboards.py can compose them.
─────────────────────────────────────────────
"""

from telegram import InlineKeyboardButton


def kb_wsssh_extra() -> list:
    """Extra button rows for wsssh service detail page."""
    return [
        [InlineKeyboardButton("✏️ Change Banner", callback_data="svc_wsssh_banner")],
    ]
