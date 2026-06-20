# ui.py
from datetime import datetime

BRAND = "🛡️ Viediet Bypass"

def format_start_message(user_first_name):
    return (
        f"{BRAND}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 Welcome, {user_first_name}!\n"
        f"⚡ Automate offers with ease.\n\n"
        f"📌 Use /help to see commands.\n"
        f"🔹 /start – Restart bot\n"
        f"🔹 /help – Show help\n"
        f"🔹 /run <phone> <otp> – Execute offer\n"
        f"🔹 /status – Your stats\n"
        f"🔹 /referral – Get referral link\n"
        f"🔹 /config – (Admin) Update API config\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

def format_help():
    return (
        f"{BRAND}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📘 <b>How to use</b>\n\n"
        f"1. /run 9876543210 123456\n"
        f"   → Provide phone & OTP.\n"
        f"2. The bot will execute the configured offer.\n"
        f"3. You will receive a result card.\n\n"
        f"👥 Referral: /referral to get your link.\n"
        f"📊 Stats: /status\n"
        f"⚙️ Admin: /config (for admins)\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

def format_result(phone, success, logs, execution_time):
    status_emoji = "✅" if success else "❌"
    status_text = "Success" if success else "Failed"
    # Build details from logs
    details = "\n".join([f"• {k}: {v}" for k, v in logs.items()])
    card = (
        f"{BRAND}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{status_emoji} <b>VIEDIET RUN COMPLETED</b>\n\n"
        f"📞 Account: {phone}\n"
        f"🎁 Offer: {status_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{details}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⏱ Execution Time: {execution_time:.2f}s\n"
        f"🛡 Status: {status_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    return card

def format_status(user):
    return (
        f"{BRAND}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Your Stats</b>\n\n"
        f"👤 User ID: {user['user_id']}\n"
        f"💰 Balance: {user['balance']} points\n"
        f"📦 Total Runs: {user['total_uses']}\n"
        f"🕒 Last Use: {user['last_use'] or 'Never'}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

def format_referral(user_id, link):
    return (
        f"{BRAND}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Referral Program</b>\n\n"
        f"Share your unique link:\n"
        f"<code>{link}</code>\n\n"
        f"🔹 You get {REFERRAL_REWARD} points per referral.\n"
        f"🔹 New user gets {REFERRED_REWARD} points.\n"
        f"🔹 Your total referrals: {get_referral_count(user_id)}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
