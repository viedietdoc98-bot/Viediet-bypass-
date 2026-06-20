#!/usr/bin/env python3
"""
🚂 VIEDIET BYPASS - Main Controller
Teeno bots ko control karega alag-alag buttons ke saath
- 🛒 Flipkart Checker
- 🧘 Habit.Yoga Referral
- ⚡ Viediet Bypass (Brevistay)

Channel: @viedietlooters
Group: @viedietlooterschat
"""

import os
import sys
import time
import asyncio
import logging
import subprocess
import signal
import threading
from flask import Flask, render_template_string, request, jsonify

# ==================== TELEGRAM IMPORTS ====================
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger("ViedietMain")

# ==================== CONFIG ====================
PORT = int(os.environ.get("PORT", 8080))
MAIN_BOT_TOKEN = os.environ.get("https://github.com/viedietdoc98-bot/Viediet-bypass-.git", "")

# Bot configurations
BOTS_CONFIG = {
    "flipkart": {
        "name": "Flipkart Checker",
        "emoji": "🛒",
        "script": "flipkart_bot.py",
        "token": os.environ.get("7893651923:AAGGxbRIqZEMCWF2rSNF8a4NxhpHaAnpRl0", ""),
        "process": None,
        "status": "stopped",
        "pid": None
    },
    "yogabite": {
        "name": "Habit.Yoga Referral",
        "emoji": "🧘",
        "script": "yogabite_bot.py",
        "token": os.environ.get("7893651923:AAGGxbRIqZEMCWF2rSNF8a4NxhpHaAnpRl0", ""),
        "process": None,
        "status": "stopped",
        "pid": None
    },
    "viediet": {
        "name": "Viediet Bypass",
        "emoji": "⚡",
        "script": "viediet_bot.py",
        "token": os.environ.get("7893651923:AAGGxbRIqZEMCWF2rSNF8a4NxhpHaAnpRl0", ""),
        "process": None,
        "status": "stopped",
        "pid": None
    }
}

# ==================== FLASK WEB INTERFACE ====================
flask_app = Flask(__name__)

WEB_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>⚡ Viediet Bot Controller</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            padding: 20px 0;
        }
        .header h1 {
            font-size: 2.8em;
            background: linear-gradient(90deg, #f7971e, #ffd200);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }
        .header .subtitle {
            color: #8899aa;
            font-size: 1em;
        }
        .header .brand {
            color: #ffd200;
            font-weight: bold;
        }
        .bot-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .bot-card {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s ease;
        }
        .bot-card:hover {
            transform: translateY(-5px);
        }
        .bot-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
        }
        .bot-emoji { font-size: 2.5em; }
        .bot-name { font-size: 1.3em; font-weight: bold; }
        .bot-status {
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: auto;
        }
        .status-running { background: #00c853; color: #fff; }
        .status-stopped { background: #ff1744; color: #fff; }
        .status-starting { background: #ffd600; color: #000; }
        .bot-info {
            color: #8899aa;
            font-size: 0.85em;
            margin: 8px 0;
        }
        .bot-info span { color: #fff; }
        .btn-group {
            display: flex;
            gap: 8px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 8px 18px;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.85em;
        }
        .btn:hover { transform: scale(1.05); opacity: 0.9; }
        .btn-start { background: #00c853; color: #fff; }
        .btn-stop { background: #ff1744; color: #fff; }
        .btn-restart { background: #ffd600; color: #000; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
        }
        .stat-item { text-align: center; }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            background: linear-gradient(90deg, #f7971e, #ffd200);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-label { color: #8899aa; font-size: 0.8em; margin-top: 5px; }
        .channels {
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: rgba(255,215,0,0.05);
            border-radius: 10px;
            border: 1px solid rgba(255,215,0,0.1);
        }
        .channels a {
            color: #ffd200;
            text-decoration: none;
            margin: 0 10px;
        }
        .channels a:hover { text-decoration: underline; }
        .footer {
            text-align: center;
            color: #445566;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.05);
            font-size: 0.8em;
        }
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 24px;
            border-radius: 10px;
            color: #fff;
            font-weight: bold;
            z-index: 1000;
            animation: slideIn 0.5s ease;
        }
        .toast-success { background: #00c853; }
        .toast-error { background: #ff1744; }
        .toast-info { background: #2979ff; }
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @media (max-width: 600px) {
            .bot-grid { grid-template-columns: 1fr; }
            .header h1 { font-size: 2em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ Viediet Bypass</h1>
            <p class="subtitle">Bot Controller <span class="brand">· All Bots in One</span></p>
        </div>

        <div class="channels">
            📢 <strong>Join Our Channels:</strong>
            <a href="https://t.me/viedietlooters" target="_blank">@viedietlooters</a> |
            <a href="https://t.me/viedietlooterschat" target="_blank">@viedietlooterschat</a>
        </div>

        <div style="text-align: center; margin-bottom: 20px;">
            <button class="btn btn-start" onclick="startAll()">▶ Start All</button>
            <button class="btn btn-stop" onclick="stopAll()">⏹ Stop All</button>
            <button class="btn btn-restart" onclick="window.location.reload()">🔄 Refresh</button>
        </div>

        <div class="bot-grid">
            {% for key, bot in bots.items() %}
            <div class="bot-card" id="bot-{{ key }}">
                <div class="bot-header">
                    <span class="bot-emoji">{{ bot.emoji }}</span>
                    <span class="bot-name">{{ bot.name }}</span>
                    <span class="bot-status status-{{ bot.status }}">
                        {% if bot.status == 'running' %}● Running{% elif bot.status == 'starting' %}◐ Starting{% else %}○ Stopped{% endif %}
                    </span>
                </div>
                <div class="bot-info">
                    PID: <span>{{ bot.pid or 'N/A' }}</span>
                </div>
                <div class="bot-info">
                    Token: <span>{{ bot.token[:10] + '***' if bot.token else '❌ Not Set' }}</span>
                </div>
                <div class="btn-group">
                    <button class="btn btn-start" onclick="controlBot('{{ key }}', 'start')" {% if bot.status == 'running' %}disabled{% endif %}>
                        ▶ Start
                    </button>
                    <button class="btn btn-stop" onclick="controlBot('{{ key }}', 'stop')" {% if bot.status != 'running' %}disabled{% endif %}>
                        ⏹ Stop
                    </button>
                    <button class="btn btn-restart" onclick="controlBot('{{ key }}', 'restart')" {% if bot.status == 'starting' %}disabled{% endif %}>
                        🔄 Restart
                    </button>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">{{ stats.total }}</div>
                <div class="stat-label">Total Bots</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" style="background: linear-gradient(90deg, #00c853, #00e676); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{{ stats.running }}</div>
                <div class="stat-label">Running</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" style="background: linear-gradient(90deg, #ff1744, #ff5252); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{{ stats.stopped }}</div>
                <div class="stat-label">Stopped</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{{ stats.uptime }}</div>
                <div class="stat-label">Uptime</div>
            </div>
        </div>

        <div class="footer">
            <p>⚡ <strong>Viediet Bypass</strong> · Made for Railway</p>
            <p>📢 @viedietlooters · @viedietlooterschat</p>
        </div>
    </div>

    <script>
        function controlBot(botKey, action) {
            fetch('/control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bot: botKey, action: action })
            })
            .then(response => response.json())
            .then(data => {
                showToast(data.message, data.status);
                setTimeout(() => window.location.reload(), 1000);
            })
            .catch(error => {
                showToast('Error: ' + error, 'error');
            });
        }

        function startAll() {
            fetch('/start_all', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                showToast(data.message, 'success');
                setTimeout(() => window.location.reload(), 2000);
            });
        }

        function stopAll() {
            fetch('/stop_all', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                showToast(data.message, 'info');
                setTimeout(() => window.location.reload(), 2000);
            });
        }

        function showToast(message, type) {
            const toast = document.createElement('div');
            toast.className = 'toast toast-' + type;
            toast.textContent = message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }
    </script>
</body>
</html>
"""

# ==================== FLASK ROUTES ====================

@flask_app.route('/')
def index():
    """Main web interface"""
    stats = {
        "total": len(BOTS_CONFIG),
        "running": sum(1 for b in BOTS_CONFIG.values() if b["status"] == "running"),
        "stopped": sum(1 for b in BOTS_CONFIG.values() if b["status"] == "stopped"),
        "uptime": get_uptime()
    }
    
    bot_data = {}
    for key, bot in BOTS_CONFIG.items():
        bot_data[key] = {
            "name": bot["name"],
            "emoji": bot["emoji"],
            "status": bot["status"],
            "pid": bot["process"].pid if bot["process"] and bot["process"].poll() is None else None,
            "token": bot["token"] if bot["token"] else ""
        }
    
    return render_template_string(WEB_TEMPLATE, bots=bot_data, stats=stats)

@flask_app.route('/control', methods=['POST'])
def control_bot():
    """Control individual bot"""
    data = request.get_json()
    bot_key = data.get('bot')
    action = data.get('action')
    
    if bot_key not in BOTS_CONFIG:
        return jsonify({"status": "error", "message": "Bot not found"})
    
    if action == "start":
        start_bot_process(bot_key)
        return jsonify({"status": "success", "message": f"{BOTS_CONFIG[bot_key]['name']} starting..."})
    elif action == "stop":
        stop_bot_process(bot_key)
        return jsonify({"status": "success", "message": f"{BOTS_CONFIG[bot_key]['name']} stopped."})
    elif action == "restart":
        restart_bot_process(bot_key)
        return jsonify({"status": "success", "message": f"{BOTS_CONFIG[bot_key]['name']} restarting..."})
    
    return jsonify({"status": "error", "message": "Invalid action"})

@flask_app.route('/start_all', methods=['POST'])
def start_all_bots():
    """Start all bots"""
    for key in BOTS_CONFIG:
        if BOTS_CONFIG[key]["token"]:
            start_bot_process(key)
    return jsonify({"status": "success", "message": "All bots starting..."})

@flask_app.route('/stop_all', methods=['POST'])
def stop_all_bots():
    """Stop all bots"""
    for key in BOTS_CONFIG:
        stop_bot_process(key)
    return jsonify({"status": "success", "message": "All bots stopped."})

# ==================== BOT MANAGEMENT ====================

start_time = time.time()

def get_uptime():
    uptime_seconds = int(time.time() - start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    return f"{hours}h {minutes}m {seconds}s"

def start_bot_process(bot_key):
    """Start a bot as subprocess"""
    bot = BOTS_CONFIG[bot_key]
    
    if bot["process"] and bot["process"].poll() is None:
        logger.info(f"⚠️ {bot['name']} already running!")
        return
    
    if not bot["token"]:
        logger.error(f"❌ {bot['name']} - No token set!")
        bot["status"] = "stopped"
        return
    
    bot["status"] = "starting"
    logger.info(f"🚀 Starting {bot['name']}...")
    
    try:
        # Start process
        process = subprocess.Popen(
            [sys.executable, bot["script"]],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        bot["process"] = process
        bot["pid"] = process.pid
        bot["status"] = "running"
        
        # Start monitoring thread
        threading.Thread(target=monitor_bot, args=(bot_key, process), daemon=True).start()
        
        logger.info(f"✅ {bot['name']} started (PID: {process.pid})")
        
    except Exception as e:
        bot["status"] = "stopped"
        logger.error(f"❌ Failed to start {bot['name']}: {e}")

def stop_bot_process(bot_key):
    """Stop a bot process"""
    bot = BOTS_CONFIG[bot_key]
    
    if bot["process"] and bot["process"].poll() is None:
        bot["process"].terminate()
        try:
            bot["process"].wait(timeout=5)
        except subprocess.TimeoutExpired:
            bot["process"].kill()
        bot["status"] = "stopped"
        bot["pid"] = None
        logger.info(f"⏹ {bot['name']} stopped")
    else:
        bot["status"] = "stopped"
        bot["pid"] = None

def restart_bot_process(bot_key):
    """Restart a bot"""
    stop_bot_process(bot_key)
    time.sleep(1)
    start_bot_process(bot_key)

def monitor_bot(bot_key, process):
    """Monitor bot process"""
    while process.poll() is None:
        time.sleep(2)
    
    # Process died
    logger.warning(f"⚠️ {BOTS_CONFIG[bot_key]['name']} died. Restarting...")
    BOTS_CONFIG[bot_key]["status"] = "stopped"
    BOTS_CONFIG[bot_key]["pid"] = None
    
    # Auto-restart
    if BOTS_CONFIG[bot_key]["token"]:
        time.sleep(3)
        start_bot_process(bot_key)

# ==================== TELEGRAM MAIN BOT ====================

async def telegram_main_bot():
    """Main Telegram bot for controlling all bots"""
    if not MAIN_BOT_TOKEN:
        logger.warning("⚠️ MAIN_BOT_TOKEN not set! Web interface only.")
        return
    
    app = Application.builder().token(MAIN_BOT_TOKEN).build()
    
    async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("🛒 Flipkart Checker", callback_data="bot_flipkart")],
            [InlineKeyboardButton("🧘 Habit.Yoga Referral", callback_data="bot_yogabite")],
            [InlineKeyboardButton("⚡ Viediet Bypass", callback_data="bot_viediet")],
            [InlineKeyboardButton("📊 Status", callback_data="status")],
            [InlineKeyboardButton("📢 Join Channel", url="https://t.me/viedietlooters")],
        ]
        await update.message.reply_text(
            "⚡ *VIEDIET BYPASS* ⚡\n\n"
            "Select a bot to control:\n\n"
            "📢 @viedietlooters · @viedietlooterschat",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        
        if data == "status":
            lines = ["📊 *Bot Status*\n"]
            for key, bot in BOTS_CONFIG.items():
                status = "🟢 Running" if bot["status"] == "running" else "🔴 Stopped"
                lines.append(f"{bot['emoji']} {bot['name']}: {status}")
            lines.append("\n📢 @viedietlooters")
            await query.edit_message_text("\n".join(lines), parse_mode="Markdown")
            return
        
        if data.startswith("bot_"):
            bot_key = data[4:]
            if bot_key not in BOTS_CONFIG:
                return
            bot = BOTS_CONFIG[bot_key]
            keyboard = [
                [InlineKeyboardButton("▶ Start", callback_data=f"start_{bot_key}")],
                [InlineKeyboardButton("⏹ Stop", callback_data=f"stop_{bot_key}")],
                [InlineKeyboardButton("🔄 Restart", callback_data=f"restart_{bot_key}")],
                [InlineKeyboardButton("« Back", callback_data="back")],
            ]
            await query.edit_message_text(
                f"{bot['emoji']} *{bot['name']}*\n"
                f"Status: {'🟢 Running' if bot['status'] == 'running' else '🔴 Stopped'}\n"
                f"PID: {bot['pid'] or 'N/A'}\n\n"
                "📢 @viedietlooters",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        
        elif data.startswith("start_"):
            bot_key = data[6:]
            start_bot_process(bot_key)
            await query.edit_message_text(f"✅ {BOTS_CONFIG[bot_key]['name']} starting...\n\n📢 @viedietlooters")
        
        elif data.startswith("stop_"):
            bot_key = data[5:]
            stop_bot_process(bot_key)
            await query.edit_message_text(f"⏹ {BOTS_CONFIG[bot_key]['name']} stopped.\n\n📢 @viedietlooters")
        
        elif data.startswith("restart_"):
            bot_key = data[8:]
            restart_bot_process(bot_key)
            await query.edit_message_text(f"🔄 {BOTS_CONFIG[bot_key]['name']} restarting...\n\n📢 @viedietlooters")
        
        elif data == "back":
            await start_cmd(update, context)
    
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    logger.info("✅ Main Telegram bot started!")
    await app.run_polling()

# ==================== MAIN ENTRY ====================

def run_flask():
    """Run Flask in a separate thread"""
    flask_app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

def main():
    """Main entry point"""
    logger.info("⚡ Viediet Bypass Controller starting...")
    logger.info("📢 Channel: @viedietlooters")
    logger.info("📢 Group: @viedietlooterschat")
    
    # Start Flask in a thread (not daemon so it keeps running)
    flask_thread = threading.Thread(target=run_flask, daemon=False)
    flask_thread.start()
    logger.info(f"🌐 Web interface: http://0.0.0.0:{PORT}")
    
    # Auto-start bots with tokens
    for key, bot in BOTS_CONFIG.items():
        if bot["token"]:
            logger.info(f"🚀 Auto-starting {bot['name']}...")
            start_bot_process(key)
    
    # Run main Telegram bot in the same process (this blocks)
    try:
        asyncio.run(telegram_main_bot())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        for key in BOTS_CONFIG:
            stop_bot_process(key)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()