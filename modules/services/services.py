"""
modules/services/services.py
─────────────────────────────────────────────
Systemd service management.
Pure logic — no Telegram imports.
─────────────────────────────────────────────
"""

import config
from core.utils import run_cmd


def get_service_status(name: str) -> dict:
    """Return status dict for one systemd service."""
    code, _  = run_cmd(["systemctl", "is-active", name])
    _, out   = run_cmd(["systemctl", "show", name,
                        "--property=ActiveState,SubState,MainPID"])
    props = {}
    for line in out.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            props[k] = v
    return {
        "name":   name,
        "active": code == 0,
        "state":  props.get("ActiveState", "unknown"),
        "sub":    props.get("SubState",    "unknown"),
        "pid":    props.get("MainPID",     "0"),
    }


def get_all_services() -> list:
    """Return status for all services in config.SERVICES."""
    return [get_service_status(s) for s in config.SERVICES]


def start_service(name: str) -> tuple:
    if name not in config.SERVICES:
        return False, f"{name} not managed"
    code, out = run_cmd(["systemctl", "start", name])
    return code == 0, out or ("Started" if code == 0 else "Failed")


def stop_service(name: str) -> tuple:
    if name not in config.SERVICES:
        return False, f"{name} not managed"
    code, out = run_cmd(["systemctl", "stop", name])
    return code == 0, out or ("Stopped" if code == 0 else "Failed")


def restart_service(name: str) -> tuple:
    if name not in config.SERVICES:
        return False, f"{name} not managed"
    code, out = run_cmd(["systemctl", "restart", name])
    return code == 0, out or ("Restarted" if code == 0 else "Failed")
