"""
modules/services/wsssh/keyboards.py
─────────────────────────────────────────────
Extra keyboard rows injected into the wsssh detail page.
Returns a list of rows (not a full InlineKeyboardMarkup)
so services/keyboards.py can compose them.
─────────────────────────────────────────────
"""


def kb_wsssh_extra() -> list:
    return []
