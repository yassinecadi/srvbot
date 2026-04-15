"""
modules/system/texts.py
─────────────────────────────────────────────
Main menu message text builder.
Not async — get_all_stats is blocking (1.3s sleep for measurement).
─────────────────────────────────────────────
"""

import config
from modules.system.system import get_all_stats
from modules.users.users   import get_all_users, get_active_count


def build_main_text() -> str:
    """
    Build the main menu message.
    Live bandwidth shown alongside saved speedtest result.
    Note: takes ~1.3s due to CPU + bandwidth measurement.
    """
    stats     = get_all_stats(config.IFACE)
    user_list = get_all_users()
    active    = get_active_count(user_list)
    disk      = stats["disk"]
    st        = config.SPEEDTEST

    # Live bandwidth / speedtest columns
    rx_line = f"⬇️ `{stats['bw_rx_mbps']} Mbps`"
    tx_line = f"⬆️ `{stats['bw_tx_mbps']} Mbps`"
    if st.get("download_mbps"):
        rx_line += f" / `{st['download_mbps']} Mbps`"
    if st.get("upload_mbps"):
        tx_line += f" / `{st['upload_mbps']} Mbps`"

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
        lines.append(f"🚀 Last speed test: `{st['last_run'][:10]}`")

    return "\n".join(lines)
