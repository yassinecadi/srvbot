"""
handlers/users_handler.py
────────────────────────────────────────────────────────────────
Users menu: list, view, add, delete, lock, unlock, expiry,
            change password.
Multi-step actions use context.user_data["action"].
────────────────────────────────────────────────────────────────
"""

from telegram.ext import ContextTypes

from handlers.keyboards import kb_users, kb_user_actions, kb_back_main
from handlers.texts     import build_users_list_text, build_user_detail_text
from helpers            import users


# ── Button handlers ───────────────────────────────────────────

async def handle_users_list(query, context: ContextTypes.DEFAULT_TYPE):
    """Show list of all SSH users."""
    user_list = users.get_all_users()
    context.user_data["user_list"] = user_list
    await query.edit_message_text(
        build_users_list_text(user_list),
        parse_mode="Markdown",
        reply_markup=kb_users(user_list)
    )


async def handle_user_detail(query, username: str, context: ContextTypes.DEFAULT_TYPE):
    """Show detail page for one user."""
    user_list = users.get_all_users()
    u = next((x for x in user_list if x["username"] == username), None)
    if not u:
        await query.edit_message_text("❌ User not found.", reply_markup=kb_back_main())
        return
    await query.edit_message_text(
        build_user_detail_text(u),
        parse_mode="Markdown",
        reply_markup=kb_user_actions(username, u["active"])
    )


async def handle_user_add_prompt(query, context: ContextTypes.DEFAULT_TYPE):
    """Prompt admin to type new username."""
    context.user_data["action"] = "add_user_name"
    await query.edit_message_text(
        "➕ *Add User*\n\nSend username:\n\n/cancel to go back",
        parse_mode="Markdown", reply_markup=kb_back_main()
    )


async def handle_chpass_prompt(query, username: str, context: ContextTypes.DEFAULT_TYPE):
    """Prompt admin to type new password."""
    context.user_data.update(action="chpass", target_user=username)
    await query.edit_message_text(
        f"🔑 *Change password — {username}*\n\nSend new password or /random\n\n/cancel to go back",
        parse_mode="Markdown", reply_markup=kb_back_main()
    )


async def handle_expiry_prompt(query, username: str, context: ContextTypes.DEFAULT_TYPE):
    """Prompt admin to type expiry days."""
    context.user_data.update(action="expiry", target_user=username)
    await query.edit_message_text(
        f"⏰ *Set expiry — {username}*\n\nSend days (e.g. `30`) or `0` for never\n\n/cancel to go back",
        parse_mode="Markdown", reply_markup=kb_back_main()
    )


async def handle_lock(query, username: str):
    ok, msg = users.lock_user(username)
    await query.edit_message_text(
        f"{'🔒' if ok else '❌'} {msg}", reply_markup=kb_back_main()
    )


async def handle_unlock(query, username: str):
    ok, msg = users.unlock_user(username)
    await query.edit_message_text(
        f"{'🔓' if ok else '❌'} {msg}", reply_markup=kb_back_main()
    )


async def handle_delete(query, username: str):
    ok, msg = users.delete_user(username)
    await query.edit_message_text(
        f"{'✅' if ok else '❌'} {msg}", reply_markup=kb_back_main()
    )


# ── Message (text input) handlers ────────────────────────────

async def on_add_user_name(message, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: receive username."""
    context.user_data["new_username"] = message.text.strip()
    context.user_data["action"]       = "add_user_pass"
    await message.reply_text(
        f"Username: *{message.text.strip()}*\n\nSend password or /random:",
        parse_mode="Markdown"
    )


async def on_add_user_pass(message, context: ContextTypes.DEFAULT_TYPE):
    """Step 2: receive password and create user."""
    username = context.user_data.get("new_username", "")
    password = users.random_password() if message.text.strip() == "/random" else message.text.strip()
    ok, msg  = users.add_user(username, password)
    context.user_data.clear()
    if ok:
        await message.reply_text(
            f"✅ *User created*\n\n`{username}` / `{password}`",
            parse_mode="Markdown"
        )
    else:
        await message.reply_text(f"❌ {msg}")


async def on_chpass(message, context: ContextTypes.DEFAULT_TYPE):
    """Receive and apply new password."""
    username = context.user_data.get("target_user", "")
    password = users.random_password() if message.text.strip() == "/random" else message.text.strip()
    ok, msg  = users.change_password(username, password)
    context.user_data.clear()
    if ok:
        await message.reply_text(
            f"✅ *Password changed*\n\n`{username}` / `{password}`",
            parse_mode="Markdown"
        )
    else:
        await message.reply_text(f"❌ {msg}")


async def on_expiry(message, context: ContextTypes.DEFAULT_TYPE):
    """Receive days and set expiry."""
    username = context.user_data.get("target_user", "")
    try:
        days    = int(message.text.strip())
        ok, msg = users.set_expiry(username, None if days == 0 else days)
        context.user_data.clear()
        await message.reply_text(f"{'✅' if ok else '❌'} {msg}")
    except ValueError:
        await message.reply_text("❌ Send a number. e.g. `30`")
