"""
helpers/services.py
────────────────────────────────────────────────────────────────
Systemd service management + per-service custom actions:
  - wsssh   : read/set websocket banner
  - srvbot  : add admin Telegram ID
────────────────────────────────────────────────────────────────
"""

import subprocess
import re
import config


# ── Config file paths for custom actions ──────────────────────
WSSSH_CONFIG = "/root/wsssh/config.yaml"
BOT_CONFIG   = "/root/bots/srvbot/config.py"


# ── Internal helper ───────────────────────────────────────────

def _run(cmd: list) -> tuple:
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


# ── Service status ────────────────────────────────────────────

def get_service_status(name: str) -> dict:
    """
    Return current status of a systemd service.
    Result: {name, active, state, sub, pid}
    """
    code, _  = _run(["systemctl", "is-active", name])
    active   = (code == 0)
    _, out   = _run(["systemctl", "show", name,
                     "--property=ActiveState,SubState,MainPID"])
    props = {}
    for line in out.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            props[k] = v
    return {
        "name":   name,
        "active": active,
        "state":  props.get("ActiveState", "unknown"),
        "sub":    props.get("SubState",    "unknown"),
        "pid":    props.get("MainPID",     "0"),
    }


def get_all_services() -> list:
    """Return status for all services listed in config.SERVICES."""
    return [get_service_status(s) for s in config.SERVICES]


# ── Start / Stop / Restart ────────────────────────────────────

def start_service(name: str) -> tuple:
    if name not in config.SERVICES:
        return False, f"{name} not in managed list"
    code, out = _run(["systemctl", "start", name])
    return code == 0, out or ("Started" if code == 0 else "Failed")


def stop_service(name: str) -> tuple:
    if name not in config.SERVICES:
        return False, f"{name} not in managed list"
    code, out = _run(["systemctl", "stop", name])
    return code == 0, out or ("Stopped" if code == 0 else "Failed")


def restart_service(name: str) -> tuple:
    if name not in config.SERVICES:
        return False, f"{name} not in managed list"
    code, out = _run(["systemctl", "restart", name])
    return code == 0, out or ("Restarted" if code == 0 else "Failed")


# ── wsssh custom: banner ──────────────────────────────────────

def get_wsssh_banner() -> str:
    """Read current banner text from wsssh config.yaml."""
    try:
        with open(WSSSH_CONFIG) as f:
            content = f.read()
        match = re.search(r'custom_response_text:\s*"([^"]*)"', content)
        return match.group(1) if match else "Not set"
    except FileNotFoundError:
        return "wsssh config not found"


def set_wsssh_banner(new_banner: str) -> tuple:
    """
    Update custom_response_text in wsssh config.yaml,
    then restart wsssh service.
    """
    try:
        with open(WSSSH_CONFIG) as f:
            content = f.read()
        updated = re.sub(
            r'(custom_response_text:\s*)"[^"]*"',
            f'\\1"{new_banner}"',
            content
        )
        with open(WSSSH_CONFIG, "w") as f:
            f.write(updated)
        restart_service("wsssh")
        return True, "Banner updated — wsssh restarted"
    except Exception as e:
        return False, str(e)


# ── telegram-srvbot custom: add admin ────────────────────────

def add_bot_admin(new_id: int) -> tuple:
    """
    Add a Telegram user ID to ADMIN_ID in config.py.
    Supports both single int and list formats.
    Restarts the bot after saving.
    """
    try:
        with open(BOT_CONFIG) as f:
            content = f.read()

        list_match = re.search(r'ADMIN_ID\s*=\s*\[([^\]]*)\]', content)
        int_match  = re.search(r'ADMIN_ID\s*=\s*(\d+)', content)

        if list_match:
            ids = [x.strip() for x in list_match.group(1).split(",") if x.strip()]
            if str(new_id) in ids:
                return False, f"{new_id} is already an admin"
            ids.append(str(new_id))
            updated = re.sub(
                r'ADMIN_ID\s*=\s*\[[^\]]*\]',
                f'ADMIN_ID = [{", ".join(ids)}]',
                content
            )
        elif int_match:
            existing = int_match.group(1)
            if existing == str(new_id):
                return False, f"{new_id} is already the admin"
            updated = re.sub(
                r'ADMIN_ID\s*=\s*\d+',
                f'ADMIN_ID = [{existing}, {new_id}]',
                content
            )
        else:
            return False, "Could not parse ADMIN_ID in config.py"

        with open(BOT_CONFIG, "w") as f:
            f.write(updated)

        restart_service("telegram-srvbot")
        return True, f"Admin {new_id} added — bot restarting"

    except Exception as e:
        return False, str(e)
