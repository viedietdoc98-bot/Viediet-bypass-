# handlers.py
import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMIN_IDS, REFERRAL_REWARD, REFERRED_REWARD
from database import get_user, create_user, update_user_balance, add_referral, get_referral_count, get_api_config, set_api_config
from api_engine import execute_offer
from ui import *
import time
import json
import logging
import re

logger = logging.getLogger(__name__)
bot = telebot.TeleBot(BOT_TOKEN)

# Rate limiting (simple in-memory)
user_last_run = {}

def is_admin(user_id):
    return user_id in ADMIN_IDS

def rate_limit_ok(user_id):
    now = time.time()
    last = user_last_run.get(user_id, 0)
    if now - last < USER_COOLDOWN:
        return False
    user_last_run[user_id] = now
    return True

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    # Check if user exists, create if not
    user = get_user(user_id)
    if not user:
        # Check for referral parameter (from deep link)
        args = message.text.split()
        referrer_id = None
        if len(args) > 1:
            try:
                referrer_id = int(args[1])
            except:
                pass
        create_user(user_id, message.from_user.username, message.from_user.first_name,
                    message.from_user.last_name, referrer_id)
        # If referred, give rewards
        if referrer_id:
            # Give referrer reward
            update_user_balance(referrer_id, REFERRAL_REWARD)
            add_referral(referrer_id, user_id, REFERRAL_REWARD)
            # Give new user reward
            update_user_balance(user_id, REFERRED_REWARD)
            bot.send_message(referrer_id, f"🎉 You earned {REFERRAL_REWARD} points for referring a new user!")
    bot.reply_to(message, format_start_message(message.from_user.first_name), parse_mode='HTML')

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message, format_help(), parse_mode='HTML')

@bot.message_handler(commands=['status'])
def status_cmd(message):
    user = get_user(message.from_user.id)
    if not user:
        bot.reply_to(message, "❌ You are not registered. Use /start first.")
        return
    bot.reply_to(message, format_status(user), parse_mode='HTML')

@bot.message_handler(commands=['referral'])
def referral_cmd(message):
    user_id = message.from_user.id
    link = f"https://t.me/{bot.get_me().username}?start={user_id}"
    bot.reply_to(message, format_referral(user_id, link), parse_mode='HTML')

@bot.message_handler(commands=['run'])
def run_cmd(message):
    user_id = message.from_user.id
    # Check registration
    user = get_user(user_id)
    if not user:
        bot.reply_to(message, "❌ Please /start first.")
        return
    # Check cooldown
    if not rate_limit_ok(user_id):
        bot.reply_to(message, "⏳ Please wait before running again.")
        return
    # Parse arguments: /run phone otp
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "❌ Usage: /run <phone> <otp>\nExample: /run 9876543210 123456")
        return
    phone = parts[1]
    otp = parts[2]
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ Phone must be 10 digits.")
        return
    if not otp.isdigit() or len(otp) != 6:
        bot.reply_to(message, "❌ OTP must be 6 digits.")
        return

    start_time = time.time()
    status_msg = bot.reply_to(message, "⏳ Executing offer...")
    try:
        success, logs = execute_offer(user_id, phone, otp)
        elapsed = time.time() - start_time
        result_card = format_result(phone, success, logs, elapsed)
        bot.edit_message_text(result_card, chat_id=status_msg.chat.id, message_id=status_msg.message_id, parse_mode='HTML')
        # Update balance if success? (optional, depends on offer)
        # Here we just log.
    except Exception as e:
        logger.error(f"Run error for {user_id}: {e}")
        bot.edit_message_text(f"❌ Error: {str(e)}", chat_id=status_msg.chat.id, message_id=status_msg.message_id)

# Admin commands
@bot.message_handler(commands=['config'])
def config_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Admin only.")
        return
    # Show current config and provide inline keyboard to edit
    config = get_api_config() or {}
    config_text = json.dumps(config, indent=2)
    if len(config_text) > 4000:
        config_text = config_text[:4000] + "..."
    bot.reply_to(message, f"<b>Current Config</b>:\n<pre>{config_text}</pre>\n\nSend new config as JSON to update.", parse_mode='HTML')

@bot.message_handler(commands=['setconfig'])
def setconfig_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Admin only.")
        return
    # Expect JSON in message text after command
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "❌ Provide JSON config.\nExample: /setconfig {\"base_url\":\"...\"}")
        return
    try:
        new_config = json.loads(parts[1])
        # Merge with defaults? We'll just store as is.
        set_api_config(new_config)
        bot.reply_to(message, "✅ Config updated successfully.")
    except json.JSONDecodeError as e:
        bot.reply_to(message, f"❌ Invalid JSON: {e}")

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Admin only.")
        return
    from database import get_db
    with get_db() as conn:
        total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        total_runs = conn.execute('SELECT COUNT(*) FROM usage_logs').fetchone()[0]
        bot.reply_to(message, f"📊 <b>Bot Stats</b>\n👥 Total Users: {total_users}\n🔄 Total Runs: {total_runs}", parse_mode='HTML')

# Default fallback
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(message, "❓ Unknown command. Use /help.")
