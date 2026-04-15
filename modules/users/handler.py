"""
modules/users/handler.py
─────────────────────────────────────────────
Users module: button router + multi-step message handler.
─────────────────────────────────────────────
"""

from telegram import Update
from telegram.ext import ContextTypes

from core.auth                  import is_admin
from ui.keyboards               import kb_back_main
from modules.users.users        import (
    get_all_users, add_user, delete_user,
    change_password, lock_user, unlock_user,
    set_expiry, random_password,
)
from modules.users.keyboards    import kb_users_list, kb_user_actions
from modules.users.texts        import build_users_list_text, build_user_detail_text


# ── Button handler ────────────────────────

async def on_users_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data

    if not is_admin(q.from_user.id):
        await q.edit_message_text("⛔ Unauthorized")
        return

    # Users list
    if data == "menu_users":
        user_list = get_all_users()
        context.user_data["user_list"] = user_list
        await q.edit_message_text(
            build_users_list_text(user_list),
            parse_mode="Markdown",
            reply_markup=kb_users_list(user_list)
        )

    # Single user detail
    elif data.startswith("user_") and data != "user_add":
        username  = data[5:]
        user_list = get_all_users()
        u = next((x for x in user_list if x["username"] == username), None)
        if not u:
            await q.edit_message_text("❌ User not found.", reply_markup=kb_back_main())
            return
        await q.edit_message_text(
            build_user_detail_text(u),
            parse_mode="Markdown",
            reply_markup=kb_user_actions(username, u["active"])
        )

    # Add user — step 1 prompt
    elif data == "user_add":
        context.user_data["action"] = "add_user_name"
        await q.edit_message_text(
            "➕ *Add User*\n\nSend username:\n\n/cancel to go back",
            parse_mode="Markdown", reply_markup=kb_back_main()
        )

    # Change password prompt
    elif data.startswith("chpass_"):
        username = data[7:]
        context.user_data.update(action="chpass", target_user=username)
        await q.edit_message_text(
            f"🔑 *Change password — {username}*\n\nSend new password or /random\n\n/cancel to go back",
            parse_mode="Markdown", reply_markup=kb_back_main()
        )

    # Set expiry prompt
    elif data.startswith("expiry_"):
        username = data[7:]
        context.user_data.update(action="expiry", target_user=username)
        await q.edit_message_text(
            f"⏰ *Set expiry — {username}*\n\nSend days (e.g. `30`) or `0` for never\n\n/cancel to go back",
            parse_mode="Markdown", reply_markup=kb_back_main()
        )

    # Lock
    elif data.startswith("lock_"):
        ok, msg = lock_user(data[5:])
        await q.edit_message_text(
            f"{'🔒' if ok else '❌'} {msg}", reply_markup=kb_back_main()
        )

    # Unlock
    elif data.startswith("unlock_"):
        ok, msg = unlock_user(data[7:])
        await q.edit_message_text(
            f"{'🔓' if ok else '❌'} {msg}", reply_markup=kb_back_main()
        )

    # Delete
    elif data.startswith("delete_"):
        ok, msg = delete_user(data[7:])
        await q.edit_message_text(
            f"{'✅' if ok else '❌'} {msg}", reply_markup=kb_back_main()
        )


# ── Message handler (multi-step) ──────────

async def on_users_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action = context.user_data.get("action")
    text   = update.message.text.strip()

    if action == "add_user_name":
        context.user_data["new_username"] = text
        context.user_data["action"]       = "add_user_pass"
        await update.message.reply_text(
            f"Username: *{text}*\n\nSend password or /random:",
            parse_mode="Markdown"
        )

    elif action == "add_user_pass":
        username = context.user_data.get("new_username", "")
        password = random_password() if text == "/random" else text
        ok, msg  = add_user(username, password)
        context.user_data.clear()
        if ok:
            await update.message.reply_text(
                f"✅ *User created*\n\n`{username}` / `{password}`",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(f"❌ {msg}")

    elif action == "chpass":
        username = context.user_data.get("target_user", "")
        password = random_password() if text == "/random" else text
        ok, msg  = change_password(username, password)
        context.user_data.clear()
        if ok:
            await update.message.reply_text(
                f"✅ *Password changed*\n\n`{username}` / `{password}`",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(f"❌ {msg}")

    elif action == "expiry":
        username = context.user_data.get("target_user", "")
        try:
            days    = int(text)
            ok, msg = set_expiry(username, None if days == 0 else days)
            context.user_data.clear()
            await update.message.reply_text(f"{'✅' if ok else '❌'} {msg}")
        except ValueError:
            await update.message.reply_text("❌ Send a number. e.g. `30`")
