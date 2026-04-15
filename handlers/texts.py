"""
handlers/texts.py
────────────────────────────────────────────────────────────────
All Telegram message text builders.
Keep formatting logic here — bot.py stays clean.
────────────────────────────────────────────────────────────────
"""

import config
from helpers import system, users, services, speedtest as sp


# ── Main menu ─────────────────────────────────────────────────

async def build_main_text() -> str:
    """
    Build the main menu message.
    Shows: IP, domain, live bandwidth / speedtest result,
           CPU, RAM, disk, user count.
    """
    stats     = system.get_all_stats(config.IFACE)
    user_list = users.get_all_users()
    active    = users.get_active_count(user_list)
    disk      = stats["disk"]
    st        = config.SPEEDTEST   # saved speedtest results

    # Live bandwidth / speedtest columns
    dl_speed = st.get("download_mbps")
    ul_speed = st.get("upload_mbps")

    rx_line = f"⬇️ `{stats['bw_rx_mbps']} Mbps`"
    tx_line = f"⬆️ `{stats['bw_tx_mbps']} Mbps`"

    if dl_speed:
        rx_line += f" / `{dl_speed} Mbps`"
    if ul_speed:
        tx_line += f" / `{ul_speed} Mbps`"

    lines = [
        "🤖 *srv Management Bot*",
        f"☢️ {config.HANDLE}",
        f"🌐 Server: `{stats['ip']}`",
        f"🔗 Domain: `{config.DOMAIN}`",
        rx_line,
        tx_line,
        f"💻 CPU: {stats['cpu']}%",
        f"🧠 RAM: {stats['ram_used_mb']}mb/{stats['ram_total_gb']}GB • {stats['ram_percent']}%",
        f"💾 Disk: {disk['used']}GB/{disk['total']}GB • {disk['percent']}%",
        f"👥 Users: {active}/{len(user_list)} active",
    ]

    if st.get("last_run"):
        lines.append(f"🚀 Speed: `{st['last_run'][:10]}`")

    return "\n".join(lines)


# ── Users ─────────────────────────────────────────────────────

def build_users_list_text(user_list: list) -> str:
    active = users.get_active_count(user_list)
    return f"👥 *Users* — {active}/{len(user_list)} active\n\nSelect a user:"


def build_user_detail_text(u: dict) -> str:
    icon   = "✅" if u["active"] else "❌"
    expiry = u["expires"] or "Never"
    return (
        f"{icon} *{u['username']}*\n\n"
        f"Expires    : {expiry}\n"
        f"Connections: {u['connections']}"
    )


# ── Services ──────────────────────────────────────────────────

def build_services_list_text() -> str:
    return "⚙️ *Services*\n\nSelect a service to manage:"


def build_service_detail_text(s: dict) -> str:
    """Detail text for one service — includes custom info per service."""
    icon  = "🟢" if s["active"] else "🔴"
    lines = [
        f"⚙️ *{s['name']}*\n",
        f"Status : {icon} {s['state']} ({s['sub']})",
        f"PID    : `{s['pid']}`",
    ]
    if s["name"] == "wsssh":
        banner = services.get_wsssh_banner()
        lines.append(f"Banner : `{banner}`")
    elif s["name"] == "telegram-srvbot":
        lines.append(f"Admin  : `{config.ADMIN_ID}`")
    return "\n".join(lines)


def build_service_action_text(name: str, ok: bool, msg: str) -> str:
    """Result line prepended before service detail."""
    status = "✅" if ok else "❌"
    return f"{status} {name}: {msg}\n\n"


# ── Speedtest ─────────────────────────────────────────────────

def build_speedtest_menu_text() -> str:
    """Speedtest screen — shows last result if available."""
    st = config.SPEEDTEST
    if not st.get("last_run"):
        return (
            "🚀 *Speed Test*\n\n"
            "No results yet.\n"
            "Press *Run Now* to start."
        )
    return sp.format_result(st)


def build_speedtest_running_text() -> str:
    return "⏳ *Running speed test...*\n\nThis takes ~30 seconds. Please wait."
