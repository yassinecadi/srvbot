"""
modules/speedtest/keyboards.py
─────────────────────────────────────────────
Keyboards for the speedtest module.
─────────────────────────────────────────────
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def kb_speedtest(has_result: bool) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🚀 Run Now", callback_data="speedtest_run")],
    ]
    if has_result:
        rows.append([
            InlineKeyboardButton("📋 Last Result", callback_data="speedtest_last"),
        ])
    rows.append([InlineKeyboardButton("🔙 Back", callback_data="menu_refresh")])
    return InlineKeyboardMarkup(rows)
