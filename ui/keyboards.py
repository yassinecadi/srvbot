"""
ui/keyboards.py
─────────────────────────────────────────────
Shared navigation keyboards used across multiple modules.
Module-specific keyboards live in their own keyboards.py.
─────────────────────────────────────────────
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def kb_back_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Main Menu", callback_data="menu_refresh")],
    ])


def kb_back_users() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Users", callback_data="menu_users")],
    ])


def kb_back_services() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Services", callback_data="menu_services")],
    ])
