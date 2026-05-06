# VPS Monitor Dashboard

A real-time VPS monitoring dashboard built as a [Telegram Mini App](https://core.telegram.org/bots/webapps). Displays system resources, PM2 processes, and network stats with Telegram auto-login authentication.

## Overview

A real-time VPS monitoring dashboard accessible directly from Telegram as a Mini App. No need to open a browser or SSH — just tap a button in the bot and instantly see your server status.

### Use Cases
- 📊 Monitor CPU, RAM, and Disk usage in real-time
- 🤖 Check PM2 process status (nara-dca-agent, portal-bot, etc.)
- 🌐 View public IP and active network connections
- 🔄 Auto-refreshes every 30 seconds
- 🔒 Secure — only accessible via Telegram, not exposed to the public web

### Who needs this?
- VPS owners who want quick server status from their phone without SSH
- Monitoring trading bot servers (DCA, arbitrage, etc.)
- Quick health check to see if your server is alive or down

### Access
Open @smartportalaibot → tap 📊 VPS or 🖥️ Dashboard

Simple, fast, secure. 🚀

## Features

- 📊 **Real-time CPU, RAM, Disk monitoring** — progress bars with color-coded thresholds
- 🤖 **PM2 process status** — name, PID, uptime, and memory per process
- 🌐 **Network stats** — public IP and active connections
- 🔄 **Auto-refresh every 30 seconds** — with manual refresh button
- 🔒 **Telegram Mini App authentication** — HMAC-SHA256 verification of `initData`
- 📱 **Mobile-friendly dark theme UI** — responsive layout, Telegram theme integration
- 🌍 **CORS-enabled API** — works cross-origin from Telegram WebView

## Project Structure

```
vps-dashboard/
├── index.html          # Frontend dashboard (Telegram Mini App)
├── api/
│   └── status.py       # Vercel serverless function (Telegram auth + VPS proxy)
├── vercel.json         # Vercel deployment config
└── README.md           # This file
```

## Architecture

```
┌──────────────┐     initData (HMAC)      ┌──────────────────┐     HTTP      ┌─────────────┐
│   Telegram   │ ──────────────────────▶  │  Vercel Serverless│ ──────────▶  │  VPS :80    │
│   Mini App   │ ◀────────────────────── │  (api/status.py)  │ ◀──────────  │  /api/status│
│  (index.html)│     JSON (system stats)  │  Verify + Proxy   │     JSON     │  (HTTP srv) │
└──────────────┘                          └──────────────────┘              └─────────────┘
```

- **Frontend** — Static HTML/CSS/JS served by Vercel. Calls `/api/status` with the Telegram `initData` header.
- **Backend** — Python serverless function on Vercel that verifies the Telegram HMAC signature, then proxies the request to the VPS.
- **VPS** — Python HTTP server on port 80 that returns system stats (`cpu`, `ram`, `disk`, `uptime`, `processes`, `ip`, `connections`).

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/vkaroo/vps-dashboard.git
   cd vps-dashboard
   ```

2. **Set environment variable** in Vercel dashboard
   ```
   TELEGRAM_BOT_TOKEN = your_bot_token_here
   ```

3. **Deploy to Vercel**
   ```bash
   vercel deploy --prod
   ```

4. **Configure your Telegram Bot** — set the Mini App URL to your Vercel deployment.

5. **Open from Telegram** — launch the Mini App from your bot's menu button.

## Tech Stack

- **Python 3** — Vercel Serverless Functions (HMAC-SHA256 auth, HTTP proxy)
- **HTML / CSS / JavaScript** — zero-dependency frontend
- **Telegram Mini Apps API** — `telegram-web-app.js` SDK
- **Vercel** — hosting, serverless compute, and routing

## Credits

- Built by [vkaroo](https://github.com/vkaroo)
- [Telegram Mini Apps](https://core.telegram.org/bots/webapps)
- [Vercel Serverless Functions](https://vercel.com/docs/functions)

## License

MIT
