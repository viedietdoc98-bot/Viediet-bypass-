#!/usr/bin/env python3
"""
⚡ VIEDIET BYPASS - All-in-One Bot
Features:
1. 🔄 Brevistay Auto-Referral Bypass
2. 🛒 Flipkart Number Checker
3. 🧘 Habit.Yoga Referral Bot

Channel: @viedietlooters
Group: @viedietlooterschat
"""

import os
import re
import json
import uuid
import random
import asyncio
import logging
import requests
import aiohttp
from typing import Optional
from datetime import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ChatMember
)
from telegram.ext import (
    Application, CommandHandler, ConversationHandler,
    MessageHandler, CallbackQueryHandler, filters, ContextTypes,
)

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger(__name__)

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BASE_URL = "https://cst.brevistay.com"

# Channel and Group
FORCE_CHANNELS = ["viedietlooters"]
FORCE_GROUP = "viedietlooterschat"

# ==================== KEYBOARDS ====================

def main_menu():
    """Main menu with all 3 features"""
    return ReplyKeyboardMarkup(
        [
            ["🔄 Brevistay Bypass"],
            ["🛒 Flipkart Checker"],
            ["🧘 Habit.Yoga Referral"],
            ["📊 Status", "📢 Channel"]
        ],
        resize_keyboard=True,
        is_persistent=True
    )

def cancel_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])

def back_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ])

# ==================== FORCE JOIN CHECK ====================

async def is_channel_member(bot, user_id: int) -> bool:
    """Check if user has joined required channel"""
    for ch in FORCE_CHANNELS:
        try:
            member = await bot.get_chat_member(f"@{ch}", user_id)
            if member.status in (ChatMember.LEFT, ChatMember.KICKED, ChatMember.BANNED):
                return False
        except Exception:
            return False
    return True

def force_join_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/viedietlooters")],
        [InlineKeyboardButton("💬 Join Group", url="https://t.me/viedietlooterschat")],
        [InlineKeyboardButton("✅ I Have Joined", callback_data="check_joined")],
    ])

# ==================== 1️⃣ BREVISTAY BYPASS ====================

BREVISTAY_FIRST_NAMES = ["Amit", "Rahul", "Priya", "Neha", "Rohan", "Anjali", "Vikas", "Pooja", "Arun", "Kavita"]
BREVISTAY_LAST_NAMES = ["Sharma", "Verma", "Singh", "Kumar", "Gupta", "Patel", "Reddy", "Jain", "Das", "Yadav"]

(PHONE, REFER_CODE, OTP) = range(3, 6)

def brev_headers():
    return {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; Pixel 4)",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def api_login_worker(payload):
    return requests.post(f"{BASE_URL}/app-api/login", json=payload, headers=brev_headers(), timeout=45, verify=False)

def api_verify_worker(payload):
    return requests.post(f"{BASE_URL}/app-api/verify-user", json=payload, headers=brev_headers(), timeout=45, verify=False)

async def brev_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start Brevistay bypass"""
    await update.message.reply_text(
        "🔄 *Brevistay Bypass*\n\n"
        "Enter 10-digit unregistered number:",
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    )
    return PHONE

async def brev_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    if not txt.isdigit() or len(txt) != 10:
        await update.message.reply_text("❌ Invalid. Enter exactly 10 digits.", reply_markup=cancel_menu())
        return PHONE
    context.user_data["mobile"] = txt
    await update.message.reply_text(
        "🎯 *Enter Brevistay referral code:*",
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    )
    return REFER_CODE

async def brev_refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["refer_code"] = update.message.text.strip()
    data = context.user_data
    status = await update.message.reply_text(f"⏳ Requesting OTP for {data['mobile']}...")
    
    payload = {"is_otp": 1, "is_password": 0, "mobile": int(data["mobile"]), "otp": 123456, "password": ""}
    
    try:
        resp = await asyncio.to_thread(api_login_worker, payload)
        resp_data = resp.json()
        
        if str(resp_data.get("is_user_registered")) == "1":
            await status.edit_text("⚠️ Number already registered!", reply_markup=back_menu())
            return ConversationHandler.END
        
        if str(resp_data.get("is_otp_sent")) == "1":
            context.user_data["otp_ref"] = resp_data.get("refrence_code")
            await status.edit_text("✅ *OTP Sent!*\n\nEnter 6-digit OTP:", parse_mode="Markdown", reply_markup=cancel_menu())
            return OTP
        else:
            await status.edit_text(f"❌ Failed: {resp_data.get('msg', 'Unknown')}", reply_markup=back_menu())
            return ConversationHandler.END
    except Exception as e:
        await status.edit_text(f"❌ Error: {e}", reply_markup=back_menu())
        return ConversationHandler.END

async def brev_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    otp = update.message.text.strip()
    if not otp.isdigit() or len(otp) != 6:
        await update.message.reply_text("❌ Enter 6 digits.", reply_markup=cancel_menu())
        return OTP
    
    data = context.user_data
    fname = random.choice(BREVISTAY_FIRST_NAMES)
    lname = random.choice(BREVISTAY_LAST_NAMES)
    email = f"{fname.lower()}{lname.lower()}{random.randint(100, 999)}@gmail.com"
    
    status = await update.message.reply_text("⏳ Creating account...")
    
    payload = {
        "channel": "MOBILE", "email": email, "is_otp": 1, "is_password": 0,
        "lastName": lname, "mobile": int(data["mobile"]), "name": fname,
        "otp": int(otp), "password": "xxxxx",
        "ref_code": data["refer_code"],
        "age": random.randint(20, 35), "gender": random.choice(["MALE", "FEMALE"])
    }
    
    try:
        resp = await asyncio.to_thread(api_verify_worker, payload)
        resp_data = resp.json()
        
        if resp_data.get("status") == "SUCCESS":
            await status.edit_text(
                f"🎉 *ACCOUNT BYPASSED!*\n\n"
                f"👤 Name: {resp_data.get('user_first_name', fname)}\n"
                f"📧 Email: {resp_data.get('user_email_id', email)}\n"
                f"🎫 New Code: `{resp_data.get('user_referral_code', 'N/A')}`\n\n"
                "📢 @viedietlooters",
                parse_mode="Markdown",
                reply_markup=back_menu()
            )
        else:
            await status.edit_text(f"❌ Failed: {resp_data.get('msg', 'Unknown')}", reply_markup=back_menu())
    except Exception as e:
        await status.edit_text(f"❌ Error: {e}", reply_markup=back_menu())
    
    context.user_data.clear()
    return ConversationHandler.END

# ==================== 2️⃣ FLIPKART CHECKER ====================

def check_flipkart(num):
    """Check if number is registered on Flipkart"""
    try:
        num_with_code = "+91" + num
        burp0_url = "https://1.rome.api.flipkart.com:443/api/6/user/signup/status"
        burp0_headers = {
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
        }
        burp0_json = {"loginId": [num_with_code], "supportAllStates": True}

        response = requests.post(burp0_url, headers=burp0_headers, json=burp0_json, timeout=10)

        if response.status_code != 200:
            return f"⚠️ Flipkart : API Blocked (HTTP {response.status_code})"

        try:
            jsonData = response.json()
        except ValueError:
            return "⚠️ Flipkart : Did not return JSON. IP might be temporarily blocked."

        response_block = jsonData.get('RESPONSE', {})
        user_details = response_block.get('userDetails', {})
        status = user_details.get(num_with_code)

        if status == "GUEST":
            return "❌ Flipkart : Not Registered (GUEST)"
        elif status == "VERIFIED":
            return "✅ Flipkart : Registered (VERIFIED)"
        elif status is None:
            return "⚠️ Flipkart : Number not found."
        else:
            return f"ℹ️ Flipkart : Unknown Status ({status})"

    except Exception as e:
        return f"⚠️ Flipkart : Error ({type(e).__name__}: {str(e)})"

async def flipkart_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start Flipkart checker"""
    await update.message.reply_text(
        "🛒 *Flipkart Checker*\n\n"
        "Send me a 10-digit number to check:",
        parse_mode="Markdown"
    )
    return ConversationHandler.END  # Message handler will handle

async def flipkart_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Flipkart check"""
    text = update.message.text
    digits = ''.join(filter(str.isdigit, text))
    num = digits[-10:] if len(digits) >= 10 else digits
    
    if len(num) != 10:
        await update.message.reply_text("⚠️ Please send a valid 10-digit number.")
        return
    
    status_msg = await update.message.reply_text(f"🔍 Checking {num} on Flipkart...")
    result = await asyncio.to_thread(check_flipkart, num)
    await status_msg.edit_text(
        f"📱 *Result for {num}:*\n\n{result}\n\n📢 @viedietlooters",
        parse_mode="Markdown"
    )

# ==================== 3️⃣ HABIT.YOGA REFERRAL ====================

YOGABITE_DATA_FILE = "yogabite_data.json"
_yogabite_data = {
    "settings": {"bot_refer_points": 5, "signup_bonus": 0},
    "users": {},
}
_yogabite_lock = asyncio.Lock()
_YOGABITE_USERNAME = ""

REGISTER_URL = "https://auth-service.habuild.in/public/user/v1/register-user"
LOGIN_URL = "https://auth-service.habuild.in/public/auth/v1/login"
VERIFY_URL = "https://auth-service.habuild.in/public/auth/v1/verify-otp"

YOGA_HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://habit.yoga",
    "referer": "https://habit.yoga/",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15"
}
YOGA_REG_HEADERS = {**YOGA_HEADERS, "authorization": "Bearer"}

async def yoga_load_data():
    global _yogabite_data
    if os.path.exists(YOGABITE_DATA_FILE):
        try:
            with open(YOGABITE_DATA_FILE, "r") as f:
                _yogabite_data = json.load(f)
            _yogabite_data.setdefault("settings", {"bot_refer_points": 5, "signup_bonus": 0})
            _yogabite_data.setdefault("users", {})
        except Exception as e:
            logger.warning(f"Load failed: {e}")

async def yoga_save_data():
    async with _yogabite_lock:
        try:
            with open(YOGABITE_DATA_FILE, "w") as f:
                json.dump(_yogabite_data, f, indent=2)
        except Exception as e:
            logger.error(f"Save failed: {e}")

def yoga_get_user(uid: int) -> dict:
    key = str(uid)
    if key not in _yogabite_data["users"]:
        _yogabite_data["users"][key] = {
            "name": "", "refer_code": "", "points": 1,
            "total_refers": 0, "bot_refers": 0
        }
    return _yogabite_data["users"][key]

_yoga_session: Optional[aiohttp.ClientSession] = None

async def yoga_get_session():
    global _yoga_session
    if _yoga_session is None or _yoga_session.closed:
        _yoga_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
    return _yoga_session

async def yoga_api_post(url, payload, headers):
    s = await yoga_get_session()
    try:
        async with s.post(url, json=payload, headers=headers) as r:
            if r.status in (200, 201):
                try:
                    return await r.json(), None
                except:
                    return None, "Invalid JSON"
            return None, f"HTTP {r.status}"
    except Exception as e:
        return None, str(e)

async def yoga_register(phone, code, name, did, sid):
    return await yoga_api_post(REGISTER_URL, {
        "name": name, "phoneNumber": phone, "referredBy": code,
        "sourceData": {"type": "Referral"},
        "experimentMetaInfo": {"deviceId": did, "sessionId": sid},
    }, YOGA_REG_HEADERS)

async def yoga_send_otp(phone, did, sid):
    resp, err = await yoga_api_post(LOGIN_URL, {
        "method": "phone_otp", "otpChannel": "sms", "phoneNumber": phone,
        "experimentMetaInfo": {"deviceId": did, "sessionId": sid},
        "registerUser": False,
    }, YOGA_HEADERS)
    if err:
        return None, err
    if resp and resp.get("message") == "OTP sent to your phone":
        ref = resp.get("data", {}).get("refrence_code")
        if ref:
            return ref, None
    return None, "Failed to send OTP"

async def yoga_verify_otp(phone, ref, otp, did, sid):
    return await yoga_api_post(VERIFY_URL, {
        "phone": phone, "reference_code": ref, "otp": otp,
        "experimentMetaInfo": {"deviceId": did, "sessionId": sid},
        "registerUser": False,
    }, YOGA_HEADERS)

YOGA_NAMES = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Shaurya", "Atharva", "Yash", "Dhruv"]

(YOGA_LINK, YOGA_NUM_TYPE, YOGA_PHONE, YOGA_OTP) = range(6, 10)

async def yoga_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start Yoga workflow"""
    await update.message.reply_text(
        "🧘 *Habit.Yoga Referral*\n\n"
        "First, send your Habit.Yoga referral code:\n"
        "`https://habit.yoga/yourcode`",
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    )
    return YOGA_LINK

async def yoga_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    code = text.split("habit.yoga/")[-1].strip() if "habit.yoga/" in text else text.strip()
    if not code:
        await update.message.reply_text("❌ Invalid code!", reply_markup=cancel_menu())
        return YOGA_LINK
    
    async with _yogabite_lock:
        u = yoga_get_user(uid)
        u["refer_code"] = code
    asyncio.create_task(yoga_save_data())
    
    await update.message.reply_text(
        "✅ *Code set!*\n\n"
        "📞 *Select number type:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🇮🇳 Indian (10 digits)", callback_data="yoga_indian")],
            [InlineKeyboardButton("🌍 International (+)", callback_data="yoga_intl")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ])
    )
    return YOGA_NUM_TYPE

async def yoga_num_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "cancel":
        await query.edit_message_text("❌ Cancelled.", reply_markup=back_menu())
        return ConversationHandler.END
    
    context.user_data["yoga_num_type"] = "indian" if data == "yoga_indian" else "international"
    await query.edit_message_text(
        "📱 *Enter phone number:*",
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    )
    return YOGA_PHONE

async def yoga_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    raw = update.message.text.strip().replace(" ", "")
    num_type = context.user_data.get("yoga_num_type", "indian")
    
    if num_type == "indian":
        if not raw.isdigit() or len(raw) != 10:
            await update.message.reply_text("❌ 10 digits chahiye!", reply_markup=cancel_menu())
            return YOGA_PHONE
        phone = f"+91{raw}"
    else:
        if not raw.startswith("+"):
            await update.message.reply_text("❌ + se start karo!", reply_markup=cancel_menu())
            return YOGA_PHONE
        phone = raw
    
    context.user_data["yoga_phone"] = phone
    refer_code = context.user_data.get("yoga_refer_code") or yoga_get_user(uid).get("refer_code", "")
    
    status = await update.message.reply_text(f"⏳ *Processing...*\n📱 `{phone}`", parse_mode="Markdown")
    
    did, sid = str(uuid.uuid4()), str(uuid.uuid4())
    reg_resp, reg_err = await yoga_register(phone, refer_code, random.choice(YOGA_NAMES), did, sid)
    
    if reg_err or not reg_resp:
        await status.edit_text("❌ *Registration failed!*", parse_mode="Markdown", reply_markup=back_menu())
        return ConversationHandler.END
    
    try:
        is_verified = reg_resp.get("result", {}).get("data", {}).get("account", {}).get("is_phone_number_verified", False)
    except:
        is_verified = False
    
    if is_verified:
        await status.edit_text("⚠️ *Number already registered!*", parse_mode="Markdown", reply_markup=back_menu())
        return ConversationHandler.END
    
    await status.edit_text(f"✅ *New user!*\n📱 `{phone}`\n\nOTP bhej raha hoon...", parse_mode="Markdown")
    
    otp_did, otp_sid = str(uuid.uuid4()), str(uuid.uuid4())
    context.user_data.update({"yoga_otp_did": otp_did, "yoga_otp_sid": otp_sid})
    otp_ref, err = await yoga_send_otp(phone, otp_did, otp_sid)
    
    if err or not otp_ref:
        await status.edit_text("⚠️ *OTP Nahi Gaya!*", parse_mode="Markdown", reply_markup=back_menu())
        return ConversationHandler.END
    
    context.user_data["yoga_otp_ref"] = otp_ref
    await status.edit_text(
        f"✅ *OTP Bhej Diya!*\n📱 `{phone}`\n\n🔐 *6-digit OTP:*",
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    )
    return YOGA_OTP

async def yoga_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    otp = update.message.text.strip()
    
    if not otp.isdigit() or len(otp) != 6:
        await update.message.reply_text("❌ 6 digits chahiye!", reply_markup=cancel_menu())
        return YOGA_OTP
    
    phone = context.user_data.get("yoga_phone")
    otp_ref = context.user_data.get("yoga_otp_ref")
    did = context.user_data.get("yoga_otp_did")
    sid = context.user_data.get("yoga_otp_sid")
    
    if not all([phone, otp_ref, did, sid]):
        await update.message.reply_text("❌ Session expire!", reply_markup=back_menu())
        return ConversationHandler.END
    
    proc = await update.message.reply_text("⏳ *Verify ho raha hai...*", parse_mode="Markdown")
    result, err = await yoga_verify_otp(phone, otp_ref, otp, did, sid)
    
    if err or not result:
        await proc.edit_text("❌ *OTP Galat!*", parse_mode="Markdown", reply_markup=back_menu())
        return YOGA_OTP
    
    async with _yogabite_lock:
        u = yoga_get_user(uid)
        u["points"] = max(0, u["points"] - 1)
        u["total_refers"] = u.get("total_refers", 0) + 1
    asyncio.create_task(yoga_save_data())
    
    u = yoga_get_user(uid)
    context.user_data.clear()
    
    await proc.edit_text(
        f"🎉 *REFER COMPLETE!*\n\n"
        f"📱 `{phone}`\n"
        f"💰 Points: `{u['points']}`\n"
        f"🎯 Total: `{u['total_refers']}`\n\n"
        f"📢 @viedietlooters",
        parse_mode="Markdown",
        reply_markup=back_menu()
    )
    return ConversationHandler.END

# ==================== MAIN START COMMAND ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main start command with force join"""
    user_id = update.effective_user.id
    
    if not await is_channel_member(context.bot, user_id):
        await update.message.reply_text(
            "⚡ *VIEDIET BYPASS* ⚡\n\n"
            "🔒 *Access Denied!*\n\n"
            "Please join our channel and group first:\n\n"
            "📢 @viedietlooters\n"
            "💬 @viedietlooterschat",
            parse_mode="Markdown",
            reply_markup=force_join_menu()
        )
        return
    
    await update.message.reply_text(
        "⚡ *VIEDIET BYPASS* ⚡\n\n"
        "Select a feature below:\n\n"
        "📢 @viedietlooters",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

async def check_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if user joined channel"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    if await is_channel_member(context.bot, user_id):
        await query.edit_message_text(
            "✅ *Thanks for joining!*\n\nSelect a feature:",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
    else:
        await query.edit_message_text(
            "❌ *Join channel first!*\n\n📢 @viedietlooters",
            parse_mode="Markdown",
            reply_markup=force_join_menu()
        )

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot status"""
    await update.message.reply_text(
        "📊 *Bot Status*\n\n"
        "✅ Bot is running!\n"
        "🔹 Brevistay Bypass: Active\n"
        "🔹 Flipkart Checker: Active\n"
        "🔹 Habit.Yoga Referral: Active\n\n"
        "📢 @viedietlooters",
        parse_mode="Markdown"
    )

async def channel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show channel info"""
    await update.message.reply_text(
        "📢 *Join Our Channels*\n\n"
        "Channel: @viedietlooters\n"
        "Group: @viedietlooterschat",
        parse_mode="Markdown"
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries"""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "check_joined":
        return await check_joined(update, context)
    
    elif data == "cancel":
        await query.edit_message_text("❌ Cancelled.", reply_markup=back_menu())
        context.user_data.clear()
        return ConversationHandler.END
    
    elif data == "main_menu":
        context.user_data.clear()
        await query.edit_message_text(
            "⚡ *VIEDIET BYPASS* ⚡\n\nSelect a feature:",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
        return ConversationHandler.END
    
    elif data.startswith("yoga_"):
        return await yoga_num_type(update, context)
    
    return ConversationHandler.END

# ==================== CONVERSATION HANDLER ====================

conv_handler = ConversationHandler(
    entry_points=[
        # Brevistay
        MessageHandler(filters.Regex("^🔄 Brevistay Bypass$"), brev_start),
        # Yoga
        MessageHandler(filters.Regex("^🧘 Habit.Yoga Referral$"), yoga_start),
    ],
    states={
        # Brevistay states
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, brev_phone)],
        REFER_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, brev_refer)],
        OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, brev_otp)],
        # Yoga states
        YOGA_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, yoga_link)],
        YOGA_NUM_TYPE: [CallbackQueryHandler(callback_handler)],
        YOGA_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, yoga_phone)],
        YOGA_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, yoga_otp)],
    },
    fallbacks=[
        CallbackQueryHandler(callback_handler),
        MessageHandler(filters.Regex("^🛒 Flipkart Checker$"), flipkart_start),
        MessageHandler(filters.Regex("^📊 Status$"), status_cmd),
        MessageHandler(filters.Regex("^📢 Channel$"), channel_cmd),
    ],
    per_user=True,
    allow_reentry=True,
)

# ==================== MAIN ====================

async def main():
    """Main entry point"""
    global _YOGABITE_USERNAME
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set!")
        return
    
    await yoga_load_data()
    
    app = Application.builder().token(BOT_TOKEN).build()
    me = await app.bot.get_me()
    _YOGABITE_USERNAME = me.username
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    
    # Flipkart handler (separate)
    app.add_handler(MessageHandler(filters.Regex("^🛒 Flipkart Checker$"), flipkart_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, flipkart_check))
    
    # Other handlers
    app.add_handler(MessageHandler(filters.Regex("^📊 Status$"), status_cmd))
    app.add_handler(MessageHandler(filters.Regex("^📢 Channel$"), channel_cmd))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    logger.info("✅ Viediet Bypass Bot is running!")
    logger.info("📢 Channel: @viedietlooters")
    logger.info("💬 Group: @viedietlooterschat")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())