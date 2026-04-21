"""
modules/v2ray/handler.py
─────────────────────────────────────────────
V2Ray module: button router + message handler.
─────────────────────────────────────────────
"""

from telegram import Update
from telegram.ext import ContextTypes

from core.auth               import is_admin
from modules.v2ray.v2ray     import list_users, add_user, remove_user, get_user
from modules.v2ray.keyboards import kb_v2ray_menu, kb_v2ray_user, kb_back_v2ray
from modules.v2ray.texts     import build_v2ray_menu_text, build_user_detail_text


async def on_v2ray_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data

    if not is_admin(q.from_user.id):
        await q.edit_message_text("⛔ Unauthorized")
        return

    if data == "menu_v2ray":
        users = list_users()
        await q.edit_message_text(
            build_v2ray_menu_text(users),
            parse_mode="Markdown",
            reply_markup=kb_v2ray_menu(users)
        )

    elif data.startswith("v2_user_"):
        username = data[8:]
        user     = get_user(username)
        if not user:
            await q.edit_message_text("❌ User not found", reply_markup=kb_back_v2ray())
            return
        await q.edit_message_text(
            build_user_detail_text(user),
            parse_mode="Markdown",
            reply_markup=kb_v2ray_user(username)
        )

    elif data.startswith("v2_del_"):
        username = data[7:]
        ok, msg  = remove_user(username)
        users    = list_users()
        await q.edit_message_text(
            f"{'✅' if ok else '❌'} {msg}\n\n" + build_v2ray_menu_text(users),
            parse_mode="Markdown",
            reply_markup=kb_v2ray_menu(users)
        )

    elif data == "v2_add":
        context.user_data["action"] = "v2ray_add"
        await q.edit_message_text(
            "➕ *Add V2Ray User*\n\nSend username:\n\n/cancel to go back",
            parse_mode="Markdown",
            reply_markup=kb_back_v2ray()
        )


async def on_v2ray_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username   = update.message.text.strip()
    ok, result = add_user(username)
    context.user_data.clear()
    if ok:
        await update.message.reply_text(
            f"✅ *User created*\n\n"
            f"Username : `{username}`\n"
            f"UUID     : `{result}`",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(f"❌ {result}")
