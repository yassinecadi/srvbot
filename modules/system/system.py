"""
modules/system/system.py
─────────────────────────────────────────────
Pure system stats functions.
No Telegram imports. No side effects.
─────────────────────────────────────────────
"""

import os
import time
import urllib.request


# ── Public IP ─────────────────────────────

def get_public_ip() -> str:
    try:
        return urllib.request.urlopen(
            "https://api.ipify.org", timeout=5
        ).read().decode()
    except Exception:
        return "Unknown"


# ── CPU ───────────────────────────────────

def _read_cpu_times() -> tuple:
    with open("/proc/stat") as f:
        line = f.readline()
    fields = list(map(int, line.split()[1:]))
    return fields[3], sum(fields)   # idle, total


def get_cpu_percent() -> float:
    """CPU usage %. Sleeps 0.3s for delta measurement."""
    idle1, total1 = _read_cpu_times()
    time.sleep(0.3)
    idle2, total2 = _read_cpu_times()
    dt = total2 - total1
    return round((1 - (idle2 - idle1) / dt) * 100, 1) if dt else 0.0


# ── RAM ───────────────────────────────────

def _meminfo() -> dict:
    mem = {}
    with open("/proc/meminfo") as f:
        for line in f:
            p = line.split()
            if len(p) >= 2:
                mem[p[0].rstrip(":")] = int(p[1])
    return mem


def get_total_ram_gb() -> float:
    return round(_meminfo().get("MemTotal", 0) / 1024 / 1024, 1)


def get_used_ram_mb() -> int:
    m = _meminfo()
    return (m.get("MemTotal", 0) - m.get("MemAvailable", 0)) // 1024


def get_ram_percent() -> float:
    m = _meminfo()
    t = m.get("MemTotal", 1)
    return round((t - m.get("MemAvailable", 0)) / t * 100, 1)


# ── Disk ──────────────────────────────────

def get_disk_info() -> dict:
    st = os.statvfs("/")
    total = round(st.f_blocks * st.f_frsize / 1024 ** 3, 1)
    free  = round(st.f_bfree  * st.f_frsize / 1024 ** 3, 1)
    used  = round(total - free, 1)
    return {
        "total":   total,
        "used":    used,
        "free":    free,
        "percent": round(used / total * 100, 1) if total else 0,
    }


# ── Bandwidth ─────────────────────────────

def _net_bytes(iface: str) -> tuple:
    try:
        base = f"/sys/class/net/{iface}/statistics"
        rx = int(open(f"{base}/rx_bytes").read())
        tx = int(open(f"{base}/tx_bytes").read())
        return rx, tx
    except FileNotFoundError:
        return 0, 0


def get_bandwidth_mbps(iface: str = "eth0", interval: float = 1.0) -> dict:
    """Live bandwidth in Mbps. Sleeps `interval` seconds."""
    rx1, tx1 = _net_bytes(iface)
    time.sleep(interval)
    rx2, tx2 = _net_bytes(iface)
    return {
        "rx": round((rx2 - rx1) * 8 / 1e6 / interval, 2),
        "tx": round((tx2 - tx1) * 8 / 1e6 / interval, 2),
    }


# ── Combined snapshot ─────────────────────

def get_all_stats(iface: str = "eth0") -> dict:
    """All stats in one call (~1.3s due to measurement sleeps)."""
    bw = get_bandwidth_mbps(iface)
    return {
        "ip":           get_public_ip(),
        "cpu":          get_cpu_percent(),
        "ram_used_mb":  get_used_ram_mb(),
        "ram_total_gb": get_total_ram_gb(),
        "ram_percent":  get_ram_percent(),
        "disk":         get_disk_info(),
        "bw_rx_mbps":   bw["rx"],
        "bw_tx_mbps":   bw["tx"],
    }
