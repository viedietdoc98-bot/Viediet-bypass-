#!/usr/bin/env python3
"""
🚂 VIEDIET BYPASS - Main Controller
Teeno bots ko control karega alag-alag buttons ke saath
- Flipkart Checker 🛒
- Habit.Yoga Referral 🧘
- Viediet Bypass ⚡

Railway Deployment Ready
"""

import os
import sys
import time
import json
import asyncio
import logging
import subprocess
import signal
from datetime import datetime
from threading import Thread
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
MAIN_BOT_TOKEN = os.environ.get("7893651923:AAGGxbRIqZEMCWF2rSNF8a4NxhpHaAnpRl0", "")

# Bot configurations
BOTS_CONFIG = {
    "flipkart": {
        "name": "Flipkart Checker",
        "emoji": "🛒",
        "script": "flipkart_bot.py",
        "token_env": "FLIPKART_BOT_TOKEN",
        "token": os.environ.get("7893651923:AAGGxbRIqZEMCWF2rSNF8a4NxhpHaAnpRl0", ""),
        "process": None,
        "status": "stopped",
        "pid": None,
        "port": 8081
    },
    "yogabite": {
        "name": "Habit.Yoga Referral",
        "emoji": "🧘",
        "script": "yogabite_bot.py",
        "token_env": "YOGABITE_BOT_TOKEN",
        "token": os.environ.get("7893651923:AAGGxbRIqZEMCWF2rSNF8a4NxhpHaAnpRl0", ""),
        "process": None,
        "status": "stopped",
        "pid": None,
        "port": 8082
    },
    "viediet": {
        "name": "Viediet Bypass",
        "emoji": "⚡",
        "script": "viediet_bot.py",
        "token_env": "VIEDIET_BOT_TOKEN",
        "token": os.environ.get("7893651923:AAGGxbRIqZEMCWF2rSNF8a4NxhpHaAnpRl0", ""),
        "process": None,
        "status": "stopped",
        "pid": None,
        "port": 8083
    }
}

# ==================== FLASK WEB INTERFACE ====================
flask_app = Flask(__name__)

WEB_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🚂 Viediet Bot Controller</title>
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
        h1 {
            text-align: center;
            font-size: 2.5em;
            background: linear-gradient(90deg, #f7971e, #ffd200);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }
        .subtitle {
            text-align: center;
            color: #8899aa;
            margin-bottom: 30px;
            font-size: 0.95em;
        }
        .bot-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .bot-card {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
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
        .bot-emoji { font-size: 2em; }
        .bot-name { font-size: 1.2em; font-weight: bold; }
        .bot-status {
            padding: 4px 12px;
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
            font-size: 1.8em;
            font-weight: bold;
            background: linear-gradient(90deg, #f7971e, #ffd200);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-label { color: #8899aa; font-size: 0.8em; margin-top: 5px; }
        .refresh-btn {
            background: rgba(255,255,255,0.1);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.2);
            padding: 8px 20px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        .refresh-btn:hover { background: rgba(255,255,255,0.2); }
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
            h1 { font-size: 1.8em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚂 Viediet Bot Controller</h1>
        <p class="subtitle">All Bots in One · Railway Deployment</p>

        <div style="text-align: center; margin-bottom: 20px;">
            <button class="refresh-btn" onclick="window.location.reload()">🔄 Refresh Status</button>
            <button class="refresh-btn" onclick="startAll()">▶ Start All</button>
            <button class="refresh-btn" onclick="stopAll()">⏹ Stop All</button>
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
                    Token: <span>{{ bot.token[:10] + '***' if bot.token else 'Not Set' }}</span>
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
            <p>📢 @ViedietBypass · Made for Railway</p>
            <p>⚠️ Set environment variables for each bot token</p>
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
            "pid": bot["process"].pid if bot["process"] and bot["process"].is_alive() else None,
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
    
    if bot["process"] and bot["process"].is_alive():
        logger.info(f"⚠️ {bot['name']} already running!")
        return
    
    if not bot["token"]:
        logger.error(f"❌ {bot['name']} - No token set!")
        bot["status"] = "stopped"
        return
    
    bot["status"] = "starting"
    logger.info(f"🚀 Starting {bot['name']}...")
    
    try:
        # Get the script content
        script_content = get_bot_script(bot_key, bot["token"])
        
        # Write to file
        script_path = bot["script"]
        with open(script_path, "w") as f:
            f.write(script_content)
        
        # Start process
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=os.environ.copy()
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
    
    if bot["process"] and bot["process"].is_alive():
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
        time.sleep(1)
    
    # Process died
    logger.warning(f"⚠️ {BOTS_CONFIG[bot_key]['name']} died. Restarting...")
    BOTS_CONFIG[bot_key]["status"] = "stopped"
    BOTS_CONFIG[bot_key]["pid"] = None
    
    # Auto-restart
    if BOTS_CONFIG[bot_key]["token"]:
        time.sleep(2)
        start_bot_process(bot_key)

# ==================== BOT SCRIPTS ====================

def get_bot_script(bot_key, token):
    """Return bot script content"""
    
    if bot_key == "flipkart":
        return get_flipkart_script(token)
    elif bot_key == "yogabite":
        return get_yogabite_script(token)
    elif bot_key == "viediet":
        return get_viediet_script(token)
    return ""

def get_flipkart_script(token):
    return f'''#!/usr/bin/env python3
"""
FLIPKART NUMBER CHECKER
"""
import os
import logging
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "{token}"

def check_flipkart(num):
    try:
        num_with_code = "+91" + num
        burp0_url = "https://1.rome.api.flipkart.com:443/api/6/user/signup/status"
        burp0_headers = {{
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json",
            "Referer": "https://www.flipkart.com/",
            "X-User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0 FKUA/website/42/website/Desktop",
            "Origin": "https://www.flipkart.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Te": "trailers",
            "Connection": "close"
        }}
        burp0_json = {{"loginId": [num_with_code], "supportAllStates": True}}
        response = requests.post(burp0_url, headers=burp0_headers, json=burp0_json, timeout=10)
        if response.status_code != 200:
            return f"⚠️ Flipkart : API Blocked (HTTP {{response.status_code}})"
        try:
            jsonData = response.json()
        except ValueError:
            return "⚠️ Flipkart : Did not return JSON."
        response_block = jsonData.get('RESPONSE', {{}})
        user_details = response_block.get('userDetails', {{}})
        status = user_details.get(num_with_code)
        if status == "GUEST":
            return "❌ Flipkart : Not Registered (GUEST)"
        elif status == "VERIFIED":
            return "✅ Flipkart : Registered (VERIFIED)"
        elif status is None:
            return "⚠️ Flipkart : Number not found."
        else:
            return f"ℹ️ Flipkart : Unknown Status ({{status}})"
    except Exception as e:
        return f"⚠️ Flipkart : Error ({{type(e).__name__}}: {{str(e)}})"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a 10-digit number to check on Flipkart.\\n\\nCredit: @ViedietBypass")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    digits = ''.join(filter(str.isdigit, text))
    num = digits[-10:] if len(digits) >= 10 else digits
    if len(num) != 10:
        await update.message.reply_text("⚠️ Please send a valid 10-digit number.")
        return
    status_msg = await update.message.reply_text(f"🔍 Checking {{num}} on Flipkart...")
    result = await asyncio.to_thread(check_flipkart, num)
    await status_msg.edit_text(f"📱 Result for {{num}}:\\n\\n{{result}}\\n\\nCredit: @ViedietBypass")

async def main():
    logger.info("🚀 Flipkart Bot starting...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    logger.info("✅ Flipkart Bot is running!")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
'''

def get_yogabite_script(token):
    return f'''#!/usr/bin/env python3
"""
HABIT.YOGA REFERRAL BOT
"""
import os, re, json, uuid, asyncio, logging, random
from typing import Optional
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ChatMember
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger(__name__)

BOT_TOKEN = "{token}"
DATA_FILE = "yogabite_data.json"
_BOT_USERNAME = ""

REGISTER_URL = "https://auth-service.habuild.in/public/user/v1/register-user"
LOGIN_URL = "https://auth-service.habuild.in/public/auth/v1/login"
VERIFY_URL = "https://auth-service.habuild.in/public/auth/v1/verify-otp"

HEADERS = {{
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://habit.yoga",
    "referer": "https://habit.yoga/",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15"
}}
REG_HEADERS = {{**HEADERS, "authorization": "Bearer"}}

_data = {{"settings": {{"bot_refer_points": 5, "signup_bonus": 0}}, "users": {{}}}}
_lock = asyncio.Lock()

async def load_data():
    global _data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                _data = json.load(f)
            _data.setdefault("settings", {{"bot_refer_points": 5, "signup_bonus": 0}})
            _data.setdefault("users", {{}})
        except Exception as e:
            logger.warning(f"Load failed: {{e}}")

async def save_data():
    async with _lock:
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(_data, f, indent=2)
        except Exception as e:
            logger.error(f"Save failed: {{e}}")

def get_user(uid: int) -> dict:
    key = str(uid)
    if key not in _data["users"]:
        _data["users"][key] = {{"name": "", "refer_code": "", "points": 1, "total_refers": 0, "bot_refers": 0}}
    return _data["users"][key]

def get_brp(): return _data["settings"].get("bot_refer_points", 5)

_session: Optional[aiohttp.ClientSession] = None
async def get_session():
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
    return _session

async def api_post(url, payload, headers):
    s = await get_session()
    try:
        async with s.post(url, json=payload, headers=headers) as r:
            if r.status in (200, 201):
                try: return await r.json(), None
                except: return None, "Invalid JSON"
            return None, f"HTTP {{r.status}}"
    except Exception as e:
        return None, str(e)

async def api_register(phone, code, name, did, sid):
    return await api_post(REGISTER_URL, {{
        "name": name, "phoneNumber": phone, "referredBy": code,
        "sourceData": {{"type": "Referral"}},
        "experimentMetaInfo": {{"deviceId": did, "sessionId": sid}},
    }}, REG_HEADERS)

async def api_send_otp(phone, did, sid):
    resp, err = await api_post(LOGIN_URL, {{
        "method": "phone_otp", "otpChannel": "sms", "phoneNumber": phone,
        "experimentMetaInfo": {{"deviceId": did, "sessionId": sid}},
        "registerUser": False,
    }}, HEADERS)
    if err: return None, err
    if resp and resp.get("message") == "OTP sent to your phone":
        ref = resp.get("data", {{}}).get("refrence_code")
        if ref: return ref, None
    return None, "Failed to send OTP"

async def api_verify_otp(phone, ref, otp, did, sid):
    return await api_post(VERIFY_URL, {{
        "phone": phone, "reference_code": ref, "otp": otp,
        "experimentMetaInfo": {{"deviceId": did, "sessionId": sid}},
        "registerUser": False,
    }}, HEADERS)

NAMES = ["Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Shaurya","Atharva","Yash","Dhruv","Kabir","Reyansh"]
def rand_id(): return str(uuid.uuid4())
def rand_name(): return random.choice(NAMES)
def clear_temp(ctx):
    for k in ["phone", "otp_did", "otp_sid", "otp_ref", "num_type", "refer_code"]:
        ctx.user_data.pop(k, None)

BTN_WORKFLOW = "🚀 Start Workflow"
BTN_STATS = "📊 Total Stats"
BTN_LINK = "🔗 Refer Link"
BTN_CHANGE = "🔄 Code Update"
BTN_HELP = "💡 Help"

def main_menu_kb():
    return ReplyKeyboardMarkup([[BTN_WORKFLOW], [BTN_STATS, BTN_LINK], [BTN_CHANGE, BTN_HELP]], resize_keyboard=True)

def kb_inline(*rows): return InlineKeyboardMarkup(rows)
def kb_cancel(): return kb_inline([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
def kb_number_type():
    return kb_inline(
        [InlineKeyboardButton("🇮🇳 Indian (10 digits)", callback_data="num_type_indian")],
        [InlineKeyboardButton("🌍 International (with +)", callback_data="num_type_intl")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    )
def kb_otp_fail():
    return kb_inline(
        [InlineKeyboardButton("🔄 Naya OTP Bhejo", callback_data="retry_otp")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    )

(ASKING_LINK, ASKING_NUM_TYPE, ASKING_PHONE, ASKING_OTP) = range(4)

async def start_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.effective_user.first_name or ""
    async with _lock:
        u = get_user(uid)
        if not u["name"]:
            u["name"] = name
            u["points"] += _data["settings"].get("signup_bonus", 0)
    asyncio.create_task(save_data())
    clear_temp(ctx)
    await send_main_menu(update, ctx)

async def send_main_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    u = get_user(uid)
    text = f"🏠 *Main Menu*\\n👤 *{{update.effective_user.first_name or 'Dost'}}*\\n\\n💰 *Points:* `{{u.get('points', 0)}}`\\n🎯 *OTP Refers:* `{{u.get('total_refers', 0)}}`"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_kb())

async def btn_workflow(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    u = get_user(uid)
    if not u.get("refer_code"):
        await update.message.reply_text("⚠️ *Pehle apna Habit.Yoga code set karo!*\\n\\nApna referral link bhejo:", parse_mode="Markdown", reply_markup=kb_cancel())
        return ASKING_LINK
    if u.get("points", 0) < 1:
        await update.message.reply_text(f"❌ *Points Khatam!*\\n💡 Refer Link se dost bulao → *+{{get_brp()}} pts*", parse_mode="Markdown")
        return ConversationHandler.END
    ctx.user_data["refer_code"] = u["refer_code"]
    await update.message.reply_text("📞 *Number type select karo:*", parse_mode="Markdown", reply_markup=kb_number_type())
    return ASKING_NUM_TYPE

async def btn_total_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    u = get_user(uid)
    await update.message.reply_text(f"📊 *Stats*\\n👥 Users: `{{len(_data['users'])}}`\\n💰 Points: `{{u.get('points', 0)}}`\\n🎯 OTP Refers: `{{u.get('total_refers', 0)}}`", parse_mode="Markdown")

async def btn_refer_link(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    link = f"https://t.me/{{_BOT_USERNAME}}?start=ref_{{uid}}"
    await update.message.reply_text(f"🔗 *Referral Link*\\n`{{link}}`\\n\\n✅ Dost join kare → *+{{get_brp()}} points*", parse_mode="Markdown")

async def btn_code_update(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 *Naya Habit.Yoga Code Bhejo:*\\n`https://habit.yoga/yourcode`", parse_mode="Markdown", reply_markup=kb_cancel())
    return ASKING_LINK

async def btn_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💡 *Help*\\n🚀 Start Workflow → OTP refer\\n🔗 Refer Link → Dost bulao\\n🔄 Code Update → Naya code set karo", parse_mode="Markdown")

async def receive_link(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    code = text.split("habit.yoga/")[-1].strip() if "habit.yoga/" in text else text.strip()
    if not code:
        await update.message.reply_text("❌ Invalid code!", reply_markup=kb_cancel())
        return ASKING_LINK
    async with _lock:
        u = get_user(uid)
        u["refer_code"] = code
    asyncio.create_task(save_data())
    await update.message.reply_text(f"✅ *Code set!* `{{code}}`", parse_mode="Markdown")
    return ConversationHandler.END

async def receive_number_type(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "cancel":
        await query.edit_message_text("❌ Cancelled.")
        await send_main_menu(update, ctx)
        return ConversationHandler.END
    ctx.user_data["num_type"] = "indian" if data == "num_type_indian" else "international"
    await query.edit_message_text("📱 *Phone number bhejo:*", parse_mode="Markdown", reply_markup=kb_cancel())
    return ASKING_PHONE

async def receive_phone(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    raw = update.message.text.strip().replace(" ", "")
    num_type = ctx.user_data.get("num_type", "indian")
    if num_type == "indian":
        if not raw.isdigit() or len(raw) != 10:
            await update.message.reply_text("❌ 10 digits chahiye!", reply_markup=kb_cancel())
            return ASKING_PHONE
        phone = f"+91{{raw}}"
    else:
        if not raw.startswith("+"):
            await update.message.reply_text("❌ + se start karo!", reply_markup=kb_cancel())
            return ASKING_PHONE
        phone = raw
    ctx.user_data["phone"] = phone
    refer_code = ctx.user_data.get("refer_code") or get_user(uid).get("refer_code", "")
    status = await update.message.reply_text(f"⏳ *Processing...*\\n📱 `{{phone}}`", parse_mode="Markdown")
    did, sid = rand_id(), rand_id()
    reg_resp, reg_err = await api_register(phone, refer_code, rand_name(), did, sid)
    if reg_err or not reg_resp:
        await status.edit_text(f"❌ *Registration failed!*", parse_mode="Markdown", reply_markup=kb_otp_fail())
        return ASKING_OTP
    try:
        is_verified = reg_resp.get("result", {{}}).get("data", {{}}).get("account", {{}}).get("is_phone_number_verified", False)
    except: is_verified = False
    if is_verified:
        await status.edit_text(f"⚠️ *Number already registered!*", parse_mode="Markdown", reply_markup=kb_otp_fail())
        return ASKING_OTP
    await status.edit_text(f"✅ *New user!*\\n📱 `{{phone}}`\\n\\nOTP bhej raha hoon...", parse_mode="Markdown")
    otp_did, otp_sid = rand_id(), rand_id()
    ctx.user_data.update({{"otp_did": otp_did, "otp_sid": otp_sid}})
    otp_ref, err = await api_send_otp(phone, otp_did, otp_sid)
    if err or not otp_ref:
        await status.edit_text(f"⚠️ *OTP Nahi Gaya!*", parse_mode="Markdown", reply_markup=kb_otp_fail())
        return ASKING_OTP
    ctx.user_data["otp_ref"] = otp_ref
    await status.edit_text(f"✅ *OTP Bhej Diya!*\\n📱 `{{phone}}`\\n\\n🔐 *6-digit OTP type karo:*", parse_mode="Markdown", reply_markup=kb_cancel())
    return ASKING_OTP

async def receive_otp(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    otp = update.message.text.strip()
    if not otp.isdigit() or len(otp) != 6:
        await update.message.reply_text("❌ 6 digits chahiye!", reply_markup=kb_otp_fail())
        return ASKING_OTP
    phone = ctx.user_data.get("phone")
    otp_ref = ctx.user_data.get("otp_ref")
    did = ctx.user_data.get("otp_did")
    sid = ctx.user_data.get("otp_sid")
    if not all([phone, otp_ref, did, sid]):
        await update.message.reply_text("❌ Session expire!", reply_markup=main_menu_kb())
        return ConversationHandler.END
    proc = await update.message.reply_text("⏳ *Verify ho raha hai...*", parse_mode="Markdown")
    result, err = await api_verify_otp(phone, otp_ref, otp, did, sid)
    if err or not result:
        await proc.edit_text(f"❌ *OTP Galat!*", parse_mode="Markdown", reply_markup=kb_otp_fail())
        return ASKING_OTP
    async with _lock:
        u = get_user(uid)
        u["points"] = max(0, u["points"] - 1)
        u["total_refers"] = u.get("total_refers", 0) + 1
    asyncio.create_task(save_data())
    u = get_user(uid)
    clear_temp(ctx)
    await proc.edit_text(f"🎉 *REFER COMPLETE!*\\n📱 `{{phone}}`\\n💰 Points: `{{u['points']}}`\\n🎯 Total: `{{u['total_refers']}}`", parse_mode="Markdown")
    return ConversationHandler.END

async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    uid = update.effective_user.id
    if data == "cancel":
        clear_temp(ctx)
        await q.edit_message_text("❌ Cancelled.")
        await send_main_menu(update, ctx)
        return ConversationHandler.END
    elif data == "retry_otp":
        phone = ctx.user_data.get("phone")
        if not phone:
            await q.edit_message_text("📞 *Number type select karo:*", reply_markup=kb_number_type())
            return ASKING_NUM_TYPE
        await q.edit_message_text(f"🔄 *Naya OTP...*\\n📱 `{{phone}}`", parse_mode="Markdown")
        otp_did, otp_sid = rand_id(), rand_id()
        ctx.user_data.update({{"otp_did": otp_did, "otp_sid": otp_sid}})
        otp_ref, err = await api_send_otp(phone, otp_did, otp_sid)
        if err or not otp_ref:
            await q.edit_message_text(f"⚠️ *Phir Nahi Gaya!*", reply_markup=kb_otp_fail())
            return ASKING_OTP
        ctx.user_data["otp_ref"] = otp_ref
        await q.edit_message_text(f"✅ *Naya OTP Bheja!*\\n📱 `{{phone}}`\\n\\n🔐 *OTP type karo:*", parse_mode="Markdown", reply_markup=kb_cancel())
        return ASKING_OTP
    return ConversationHandler.END

async def main():
    global _BOT_USERNAME
    await load_data()
    app = Application.builder().token(BOT_TOKEN).build()
    me = await app.bot.get_me()
    _BOT_USERNAME = me.username
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start_cmd),
            MessageHandler(filters.Regex(f"^{BTN_WORKFLOW}$"), btn_workflow),
            MessageHandler(filters.Regex(f"^{BTN_CHANGE}$"), btn_code_update),
        ],
        states={{
            ASKING_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_link)],
            ASKING_NUM_TYPE: [CallbackQueryHandler(receive_number_type)],
            ASKING_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
            ASKING_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_otp)],
        }},
        fallbacks=[
            MessageHandler(filters.Regex(f"^{BTN_STATS}$"), btn_total_stats),
            MessageHandler(filters.Regex(f"^{BTN_LINK}$"), btn_refer_link),
            MessageHandler(filters.Regex(f"^{BTN_HELP}$"), btn_help),
            CallbackQueryHandler(callback_handler),
        ],
        per_user=True,
        allow_reentry=True,
    )
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_STATS}$"), btn_total_stats))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_LINK}$"), btn_refer_link))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_HELP}$"), btn_help))
    app.add_handler(CallbackQueryHandler(callback_handler))
    logger.info("✅ Habit.Yoga Bot is running!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
'''

def get_viediet_script(token):
    return f'''#!/usr/bin/env python3
"""
VIEDIET BYPASS - Brevistay Auto-Referral Bot
"""
import os
import random
import asyncio
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger(__name__)

BOT_TOKEN = "{token}"
BASE_URL = "https://cst.brevistay.com"
FIRST_NAMES = ["Amit","Rahul","Priya","Neha","Rohan","Anjali","Vikas","Pooja","Arun","Kavita","Rishabh","Sneha","Karan"]
LAST_NAMES = ["Sharma","Verma","Singh","Kumar","Gupta","Patel","Reddy","Jain","Das","Yadav","Mishra","Chauhan"]

def brev_headers():
    return {{
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; Pixel 4)",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }}

def api_login_worker(payload):
    return requests.post(f"{{BASE_URL}}/app-api/login", json=payload, headers=brev_headers(), timeout=45, verify=False)

def api_verify_worker(payload):
    return requests.post(f"{{BASE_URL}}/app-api/verify-user", json=payload, headers=brev_headers(), timeout=45, verify=False)

def generate_name():
    return random.choice(FIRST_NAMES), random.choice(LAST_NAMES)

(PHONE, REFER_CODE, OTP) = range(3)

def cancel_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel_bypass")]])

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Start Bypass", callback_data="bypass_start")],
        [InlineKeyboardButton("📖 Help", callback_data="help")],
    ])

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ *VIEDIET BYPASS* ⚡\\n\\n"
        "Brevistay auto-referral bypass bot.\\n\\n"
        "Use /bypass to start or click the button below.",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Help*\\n\\n"
        "1. Click 'Start Bypass' or use /bypass\\n"
        "2. Enter 10-digit unregistered number\\n"
        "3. Enter your Brevistay referral code\\n"
        "4. Enter OTP received on phone\\n"
        "5. Account created with your referral!\\n\\n"
        "⚠️ Number must be UNREGISTERED.",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

async def bypass_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("📱 *Enter 10-digit unregistered number:*", parse_mode="Markdown", reply_markup=cancel_menu())
    else:
        await update.message.reply_text("📱 *Enter 10-digit unregistered number:*", parse_mode="Markdown", reply_markup=cancel_menu())
    return PHONE

async def bypass_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    if not txt.isdigit() or len(txt) != 10:
        await update.message.reply_text("❌ Invalid. Enter exactly 10 digits.", reply_markup=cancel_menu())
        return PHONE
    context.user_data["mobile"] = txt
    await update.message.reply_text("🎯 *Enter Brevistay referral code:*", parse_mode="Markdown", reply_markup=cancel_menu())
    return REFER_CODE

async def bypass_refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["refer_code"] = update.message.text.strip()
    data = context.user_data
    status = await update.message.reply_text(f"⏳ Requesting OTP for {{data['mobile']}}...")
    payload = {{"is_otp": 1, "is_password": 0, "mobile": int(data["mobile"]), "otp": 123456, "password": ""}}
    try:
        resp = await asyncio.to_thread(api_login_worker, payload)
        resp_data = resp.json()
        if str(resp_data.get("is_user_registered")) == "1":
            await status.edit_text("⚠️ Number already registered!", reply_markup=main_menu())
            return ConversationHandler.END
        if str(resp_data.get("is_otp_sent")) == "1":
            context.user_data["otp_ref"] = resp_data.get("refrence_code")
            await status.edit_text("✅ *OTP Sent!*\\n\\nEnter 6-digit OTP:", parse_mode="Markdown", reply_markup=cancel_menu())
            return OTP
        else:
            await status.edit_text(f"❌ Failed: {{resp_data.get('msg', 'Unknown')}}", reply_markup=main_menu())
            return ConversationHandler.END
    except Exception as e:
        await status.edit_text(f"❌ Error: {{e}}", reply_markup=main_menu())
        return ConversationHandler.END

async def bypass_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    otp = update.message.text.strip()
    if not otp.isdigit() or len(otp) != 6:
        await update.message.reply_text("❌ Enter 6 digits.", reply_markup=cancel_menu())
        return OTP
    data = context.user_data
    fname, lname = generate_name()
    email = f"{{fname.lower()}}{{lname.lower()}}{{random.randint(100,999)}}@gmail.com"
    status = await update.message.reply_text("⏳ Creating account...")
    payload = {{
        "channel": "MOBILE", "email": email, "is_otp": 1, "is_password": 0,
        "lastName": lname, "mobile": int(data["mobile"]), "name": fname,
        "otp": int(otp), "password": "xxxxx",
        "ref_code": data["refer_code"],
        "age": random.randint(20, 35), "gender": random.choice(["MALE", "FEMALE"])
    }}
    try:
        resp = await asyncio.to_thread(api_verify_worker, payload)
        resp_data = resp.json()
        if resp_data.get("status") == "SUCCESS":
            await status.edit_text(
                f"🎉 *ACCOUNT BYPASSED!*\\n\\n"
                f"👤 Name: {{resp_data.get('user_first_name', fname)}}\\n"
                f"📧 Email: {{resp_data.get('user_email_id', email)}}\\n"
                f"🎫 New Code: `{{resp_data.get('user_referral_code', 'N/A')}}`\\n\\n"
                "📢 @ViedietBypass",
                parse_mode="Markdown",
                reply_markup=main_menu()
            )
        else:
            await status.edit_text(f"❌ Failed: {{resp_data.get('msg', 'Unknown')}}", reply_markup=main_menu())
    except Exception as e:
        await status.edit_text(f"❌ Error: {{e}}", reply_markup=main_menu())
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_bypass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("❌ Cancelled.", reply_markup=main_menu())
    else:
        await update.message.reply_text("❌ Cancelled.", reply_markup=main_menu())
    context.user_data.clear()
    return ConversationHandler.END

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "bypass_start":
        return await bypass_start(update, context)
    elif query.data == "help":
        await query.edit_message_text(
            "📖 *Help*\\n\\n1. Start Bypass\\n2. Enter 10-digit number\\n3. Enter referral code\\n4. Enter OTP\\n\\n⚠️ Number must be UNREGISTERED.",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
    elif query.data == "cancel_bypass":
        await query.edit_message_text("❌ Cancelled.", reply_markup=main_menu())
        context.user_data.clear()
        return ConversationHandler.END
    return ConversationHandler.END

async def main():
    if not BOT_TOKEN:
        logger.error("❌ VIEDIET_BOT_TOKEN not set!")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("bypass", bypass_start), CallbackQueryHandler(callback_handler, pattern="^bypass_start$")],
        states={{PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bypass_phone)],
                REFER_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bypass_refer)],
                OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, bypass_otp)]}},
        fallbacks=[CommandHandler("cancel", cancel_bypass), CallbackQueryHandler(callback_handler, pattern="^cancel_bypass$")],
        per_user=True, allow_reentry=True,
    )
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(callback_handler))
    logger.info("✅ Viediet Bypass Bot is running!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
'''

# ==================== TELEGRAM MAIN BOT ====================

async def telegram_main_bot():
    """Main Telegram bot for controlling all bots"""
    if not MAIN_BOT_TOKEN:
        logger.warning("⚠️ MAIN_BOT_TOKEN not set! Web interface only.")
        return
    
    app = Application.builder().token(MAIN_BOT_TOKEN).build()
    
    async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = []
        for key, bot in BOTS_CONFIG.items():
            status = "🟢" if bot["status"] == "running" else "🔴"
            keyboard.append([InlineKeyboardButton(f"{status} {bot['emoji']} {bot['name']}", callback_data=f"bot_{key}")])
        keyboard.append([InlineKeyboardButton("📊 Status", callback_data="status")])
        await update.message.reply_text(
            "🚂 *Viediet Bot Controller*\\n\\nSelect a bot to control:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        
        if data == "status":
            lines = ["📊 *Bot Status*\\n"]
            for key, bot in BOTS_CONFIG.items():
                status = "🟢 Running" if bot["status"] == "running" else "🔴 Stopped"
                lines.append(f"{bot['emoji']} {bot['name']}: {status}")
            await query.edit_message_text("\\n".join(lines), parse_mode="Markdown")
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
                f"{bot['emoji']} *{bot['name']}*\\n"
                f"Status: {'🟢 Running' if bot['status'] == 'running' else '🔴 Stopped'}\\n"
                f"PID: {bot['pid'] or 'N/A'}",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        
        elif data.startswith("start_"):
            bot_key = data[6:]
            start_bot_process(bot_key)
            await query.edit_message_text(f"✅ {BOTS_CONFIG[bot_key]['name']} starting...")
        
        elif data.startswith("stop_"):
            bot_key = data[5:]
            stop_bot_process(bot_key)
            await query.edit_message_text(f"⏹ {BOTS_CONFIG[bot_key]['name']} stopped.")
        
        elif data.startswith("restart_"):
            bot_key = data[8:]
            restart_bot_process(bot_key)
            await query.edit_message_text(f"🔄 {BOTS_CONFIG[bot_key]['name']} restarting...")
        
        elif data == "back":
            await start_cmd(update, context)
    
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    logger.info("✅ Main Telegram bot started!")
    await app.run_polling()

# ==================== MAIN ENTRY ====================

def start_flask():
    """Start Flask web server"""
    flask_app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

def main():
    """Main entry point"""
    logger.info("🚂 Viediet Bot Controller starting...")
    
    # Start Flask in a thread
    flask_thread = Thread(target=start_flask, daemon=True)
    flask_thread.start()
    logger.info(f"🌐 Web interface: http://localhost:{PORT}")
    
    # Auto-start bots with tokens
    for key, bot in BOTS_CONFIG.items():
        if bot["token"]:
            logger.info(f"🚀 Auto-starting {bot['name']}...")
            start_bot_process(key)
    
    # Run main Telegram bot
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