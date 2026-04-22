"""
modules/v2ray/v2ray.py
─────────────────────────────────────────────
Xray/V2Ray user management.
Reads and writes xray.json directly — no API needed.
Pure logic — no Telegram imports.
─────────────────────────────────────────────
"""

import json
import os
import uuid

import config
from core.utils import run_cmd

_CONFIG_PATH = getattr(config, "XRAY_CONFIG",      "/root/srtunnel/xray.json")
_INBOUND_TAG = getattr(config, "XRAY_INBOUND_TAG", "xray-vless")


def is_available() -> bool:
    return os.path.exists(_CONFIG_PATH)


def _read() -> dict:
    with open(_CONFIG_PATH) as f:
        return json.load(f)


def _write(data: dict) -> None:
    tmp = _CONFIG_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, _CONFIG_PATH)


def _get_inbound(data: dict, tag: str) -> dict | None:
    for ib in data.get("inbounds", []):
        if ib.get("tag") == tag:
            return ib
    return None


def _reload() -> None:
    run_cmd(["systemctl", "reload-or-restart", "xray"])


def list_users(tag: str = _INBOUND_TAG) -> list:
    try:
        ib = _get_inbound(_read(), tag)
        return ib["settings"].get("clients", []) if ib else []
    except Exception:
        return []


def get_user(username: str, tag: str = _INBOUND_TAG) -> dict | None:
    for c in list_users(tag):
        if c.get("email") == username:
            return c
    return None


def add_user(username: str, uid: str | None = None,
             flow: str = "", tag: str = _INBOUND_TAG) -> tuple:
    try:
        uid  = uid or str(uuid.uuid4())
        data = _read()
        ib   = _get_inbound(data, tag)
        if not ib:
            return False, f"Inbound '{tag}' not found in xray.json"
        clients = ib["settings"].setdefault("clients", [])
        if any(c.get("email") == username for c in clients):
            return False, f"User '{username}' already exists"
        clients.append({"id": uid, "email": username, "flow": flow})
        _write(data)
        _reload()
        return True, uid
    except Exception as e:
        return False, str(e)


def remove_user(username: str, tag: str = _INBOUND_TAG) -> tuple:
    try:
        data   = _read()
        ib     = _get_inbound(data, tag)
        if not ib:
            return False, f"Inbound '{tag}' not found"
        before = ib["settings"].get("clients", [])
        after  = [c for c in before if c.get("email") != username]
        if len(after) == len(before):
            return False, f"User '{username}' not found"
        ib["settings"]["clients"] = after
        _write(data)
        _reload()
        return True, f"User '{username}' removed"
    except Exception as e:
        return False, str(e)
