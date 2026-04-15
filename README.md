# srvbot — Server Management Telegram Bot

A modular Telegram bot for managing your VPS.

## Features
- 📊 Live server stats (CPU, RAM, disk, bandwidth)
- 👥 SSH user management (add, delete, lock, expiry, password)
- ⚙️ Systemd service management (start, stop, restart)
- 🚀 Speed test with Ookla integration
- ✏️ wsssh banner editing
- ➕ Add Telegram admin IDs live

## Structure
```
srvbot/
├── bot.py
├── config.py
├── core/           # auth, runner, utils
├── ui/             # shared keyboards, texts
└── modules/
    ├── system/     # main menu stats
    ├── users/      # SSH user management
    ├── services/   # systemd + wsssh + srvbot sub-modules
    └── speedtest/  # speedtest integration
```

## Install
```bash
bash install.sh
```

## Requirements
- Python 3.11+
- systemd
- Ookla speedtest (for result links): `apt install speedtest`
