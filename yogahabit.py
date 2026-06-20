#!/usr/bin/env python3
"""
🧘 HABIT.YOGA REFERRAL BOT
Auto-referral bot for Habit.Yoga
Channel: @viedietlooters
"""

import os
import re
import json
import uuid
import asyncio
import logging
import random
from typing import Optional
import aiohttp
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ChatMember,
)
from telegram.ext import (
    Application, CommandHandler, ConversationHandler,
    MessageHandler, CallbackQueryHandler, filters, ContextTypes,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("7893651923:AAGGxbRIqZEMCWF2rSNF8a4NxhpHaAnpRl0", "")
DATA_FILE = "yogabite_data.json"
_BOT_USERNAME = ""

REGISTER_URL = "https://auth-service.habuild.in/public/user/v1/register-user"
LOGIN_URL = "https://auth-service.habuild.in/public/auth/v1/login"
VERIFY_URL = "https://auth-service.habuild.in/public/auth/v1/verify-otp"

HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://habit.yoga",
    "referer": "https://habit.yoga/",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15"
}
REG_HEADERS = {**HEADERS, "authorization": "Bearer"}

# Data store
_data = {
    "settings": {
        "bot_refer_points": 5,
        "signup_bonus": 0,
    },
    "users": {},
}
_lock = asyncio.Lock()

async def load_data():
    global _data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                _data = json.load(f)
            _data.setdefault("settings", {"bot_refer_points": 5, "signup_bonus": 0})
            _data.setdefault("users", {})
        except Exception as e:
            logger.warning(f"Load failed: {e}")

async def save_data():
    async with _lock:
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(_data, f, indent=2)
        except Exception as e:
            logger.error(f"Save failed: {e}")

def get_user(uid: int) -> dict:
    key = str(uid)
    if key not in _data["users"]:
        _data["users"][key] = {
            "name": "",
            "refer_code": "",
            "points": 1,
            "total_refers": 0,
            "bot_refers": 0
        }
    return _data["users"][key]

def get_brp():
    return _data["settings"].get("bot_refer_points", 5)

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
                try:
                    return await r.json(), None
                except:
                    return None, "Invalid JSON"
            return None, f"HTTP {r.status}"
    except Exception as e:
        return None, str(e)

async def api_register(phone, code, name, did, sid):
    return await api_post(REGISTER_URL, {
        "name": name,
        "phoneNumber": phone,
        "referredBy": code,
        "sourceData": {"type": "Referral"},
        "experimentMetaInfo": {"deviceId": did, "sessionId": sid},
    }, REG_HEADERS)

async def api_send_otp(phone, did, sid):
    resp, err = await api_post(LOGIN_URL, {
        "method": "phone_otp",
        "otpChannel": "sms",
        "phoneNumber": phone,
        "experimentMetaInfo": {"deviceId": did, "sessionId": sid},
        "registerUser": False,
    }, HEADERS)
    if err:
        return None, err
    if resp and resp.get("message") == "OTP sent to your phone":
        ref = resp.get("data", {}).get("refrence_code")
        if ref:
            return ref, None
    return None, "Failed to send OTP"

async def api_verify_otp(phone, ref, otp, did, sid):
    return await api_post(VERIFY_URL, {
        "phone": phone,
        "reference_code": ref,
        "otp": otp,
        "experimentMetaInfo": {"deviceId": did, "sessionId": sid},
        "registerUser": False,
    }, HEADERS)

NAMES = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Shaurya", "Atharva", "Yash", "Dhruv", "Kabir", "Reyansh"]

def rand_id():
    return str(uuid.uuid4())

def rand_name():
    return random.choice(NAMES)

def clear_temp(ctx):
    for k in ["phone", "otp_did", "otp_sid", "otp_ref", "num_type", "refer_code"]:
        ctx.user_data.pop(k, None)

# Keyboard buttons
BTN_WORKFLOW = "🚀 Start Workflow"
BTN_STATS = "📊 Total Stats"
BTN_LINK = "🔗 Refer Link"
BTN_CHANGE = "🔄 Code Update"
BTN_HELP = "💡 Help"

def main_menu_kb():
    return ReplyKeyboardMarkup(
        [[BTN_WORKFLOW], [BTN_STATS, BTN_LINK], [BTN_CHANGE, BTN_HELP]],
        resize_keyboard=True
    )

def kb_inline(*rows):
    return InlineKeyboardMarkup(rows)

def kb_cancel():
    return kb_inline([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])

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
    text = (
        f"🧘 *Habit.Yoga Referral Bot*\n\n"
        f"👤 *{update.effective_user.first_name or 'Dost'}*\n"
        f"💰 *Points:* `{u.get('points', 0)}`\n"
        f"🎯 *OTP Refers:* `{u.get('total_refers', 0)}`\n\n"
        f"📢 @viedietlooters"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_kb())

async def btn_workflow(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    u = get_user(uid)
    if not u.get("refer_code"):
        await update.message.reply_text(
            "⚠️ *Pehle apna Habit.Yoga code set karo!*\n\n"
            "Apna referral link bhejo:",
            parse_mode="Markdown",
            reply_markup=kb_cancel()
        )
        return ASKING_LINK
    if u.get("points", 0) < 1:
        await update.message.reply_text(
            f"❌ *Points Khatam!*\n\n"
            f"💡 Refer Link se dost bulao → *+{get_brp()} pts*",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    ctx.user_data["refer_code"] = u["refer_code"]
    await update.message.reply_text(
        "📞 *Number type select karo:*",
        parse_mode="Markdown",
        reply_markup=kb_number_type()
    )
    return ASKING_NUM_TYPE

async def btn_total_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    u = get_user(uid)
    await update.message.reply_text(
        f"📊 *Total Stats*\n\n"
        f"👥 Users: `{len(_data['users'])}`\n"
        f"💰 Points: `{u.get('points', 0)}`\n"
        f"🎯 OTP Refers: `{u.get('total_refers', 0)}`\n\n"
        f"📢 @viedietlooters",
        parse_mode="Markdown"
    )

async def btn_refer_link(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    link = f"https://t.me/{_BOT_USERNAME}?start=ref_{uid}"
    await update.message.reply_text(
        f"🔗 *Referral Link*\n\n"
        f"`{link}`\n\n"
        f"✅ Dost join kare → *+{get_brp()} points*\n\n"
        f"📢 @viedietlooters",
        parse_mode="Markdown"
    )

async def btn_code_update(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔄 *Naya Habit.Yoga Code Bhejo:*\n\n"
        "`https://habit.yoga/yourcode`\n\n"
        "📢 @viedietlooters",
        parse_mode="Markdown",
        reply_markup=kb_cancel()
    )
    return ASKING_LINK

async def btn_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💡 *Help*\n\n"
        "🚀 Start Workflow → OTP refer\n"
        "🔗 Refer Link → Dost bulao\n"
        "🔄 Code Update → Naya code set karo\n\n"
        "📢 @viedietlooters",
        parse_mode="Markdown"
    )

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
    await update.message.reply_text(
        f"✅ *Code set!* `{code}`\n\n📢 @viedietlooters",
        parse_mode="Markdown"
    )
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
    await query.edit_message_text(
        "📱 *Phone number bhejo:*",
        parse_mode="Markdown",
        reply_markup=kb_cancel()
    )
    return ASKING_PHONE

async def receive_phone(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    raw = update.message.text.strip().replace(" ", "")
    num_type = ctx.user_data.get("num_type", "indian")
    
    if num_type == "indian":
        if not raw.isdigit() or len(raw) != 10:
            await update.message.reply_text("❌ 10 digits chahiye!", reply_markup=kb_cancel())
            return ASKING_PHONE
        phone = f"+91{raw}"
    else:
        if not raw.startswith("+"):
            await update.message.reply_text("❌ + se start karo!", reply_markup=kb_cancel())
            return ASKING_PHONE
        phone = raw
    
    ctx.user_data["phone"] = phone
    refer_code = ctx.user_data.get("refer_code") or get_user(uid).get("refer_code", "")
    
    status = await update.message.reply_text(
        f"⏳ *Processing...*\n📱 `{phone}`",
        parse_mode="Markdown"
    )
    
    did, sid = rand_id(), rand_id()
    reg_resp, reg_err = await api_register(phone, refer_code, rand_name(), did, sid)
    
    if reg_err or not reg_resp:
        await status.edit_text(
            "❌ *Registration failed!*",
            parse_mode="Markdown",
            reply_markup=kb_otp_fail()
        )
        return ASKING_OTP
    
    try:
        is_verified = reg_resp.get("result", {}).get("data", {}).get("account", {}).get("is_phone_number_verified", False)
    except:
        is_verified = False
    
    if is_verified:
        await status.edit_text(
            "⚠️ *Number already registered!*",
            parse_mode="Markdown",
            reply_markup=kb_otp_fail()
        )
        return ASKING_OTP
    
    await status.edit_text(
        f"✅ *New user!*\n📱 `{phone}`\n\nOTP bhej raha hoon...",
        parse_mode="Markdown"
    )
    
    otp_did, otp_sid = rand_id(), rand_id()
    ctx.user_data.update({"otp_did": otp_did, "otp_sid": otp_sid})
    otp_ref, err = await api_send_otp(phone, otp_did, otp_sid)
    
    if err or not otp_ref:
        await status.edit_text(
            "⚠️ *OTP Nahi Gaya!*",
            parse_mode="Markdown",
            reply_markup=kb_otp_fail()
        )
        return ASKING_OTP
    
    ctx.user_data["otp_ref"] = otp_ref
    await status.edit_text(
        f"✅ *OTP Bhej Diya!*\n📱 `{phone}`\n\n🔐 *6-digit OTP type karo:*",
        parse_mode="Markdown",
        reply_markup=kb_cancel()
    )
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
        await proc.edit_text(
            "❌ *OTP Galat!*",
            parse_mode="Markdown",
            reply_markup=kb_otp_fail()
        )
        return ASKING_OTP
    
    async with _lock:
        u = get_user(uid)
        u["points"] = max(0, u["points"] - 1)
        u["total_refers"] = u.get("total_refers", 0) + 1
    asyncio.create_task(save_data())
    
    u = get_user(uid)
    clear_temp(ctx)
    
    await proc.edit_text(
        f"🎉 *REFER COMPLETE!*\n\n"
        f"📱 `{phone}`\n"
        f"💰 Points: `{u['points']}`\n"
        f"🎯 Total: `{u['total_refers']}`\n\n"
        f"📢 @viedietlooters",
        parse_mode="Markdown"
    )
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
            await q.edit_message_text(
                "📞 *Number type select karo:*",
                reply_markup=kb_number_type()
            )
            return ASKING_NUM_TYPE
        
        await q.edit_message_text(
            f"🔄 *Naya OTP...*\n📱 `{phone}`",
            parse_mode="Markdown"
        )
        otp_did, otp_sid = rand_id(), rand_id()
        ctx.user_data.update({"otp_did": otp_did, "otp_sid": otp_sid})
        otp_ref, err = await api_send_otp(phone, otp_did, otp_sid)
        
        if err or not otp_ref:
            await q.edit_message_text(
                "⚠️ *Phir Nahi Gaya!*",
                reply_markup=kb_otp_fail()
            )
            return ASKING_OTP
        
        ctx.user_data["otp_ref"] = otp_ref
        await q.edit_message_text(
            f"✅ *Naya OTP Bheja!*\n📱 `{phone}`\n\n🔐 *OTP type karo:*",
            parse_mode="Markdown",
            reply_markup=kb_cancel()
        )
        return ASKING_OTP
    
    return ConversationHandler.END

async def main():
    global _BOT_USERNAME
    
    if not BOT_TOKEN:
        logger.error("❌ YOGABITE_BOT_TOKEN not set!")
        return
    
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
        states={
            ASKING_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_link)],
            ASKING_NUM_TYPE: [CallbackQueryHandler(receive_number_type)],
            ASKING_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
            ASKING_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_otp)],
        },
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