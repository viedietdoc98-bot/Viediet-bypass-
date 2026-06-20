#!/usr/bin/env python3
"""
🧘 HABIT.YOGA REFERRAL - Feature Module
"""
import os
import json
import uuid
import random
import asyncio
import logging
import aiohttp
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)

(YOGA_LINK, YOGA_NUM_TYPE, YOGA_PHONE, YOGA_OTP) = range(4)

REGISTER_URL = "https://auth-service.habuild.in/public/user/v1/register-user"
LOGIN_URL = "https://auth-service.habuild.in/public/auth/v1/login"
VERIFY_URL = "https://auth-service.habuild.in/public/auth/v1/verify-otp"

YOGA_HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://habit.yoga",
    "referer": "https://habit.yoga/",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5)"
}
YOGA_REG_HEADERS = {**YOGA_HEADERS, "authorization": "Bearer"}

YOGA_NAMES = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Shaurya", "Atharva"]

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

def cancel_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="main_menu")]
    ])

def back_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ])

async def yoga_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start Yoga workflow"""
    await update.message.reply_text(
        "🧘 *Habit.Yoga Referral*\n\n"
        "Send your Habit.Yoga referral code:\n"
        "`https://habit.yoga/yourcode`",
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    )
    context.user_data["yoga_state"] = YOGA_LINK
    return YOGA_LINK

async def yoga_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    code = text.split("habit.yoga/")[-1].strip() if "habit.yoga/" in text else text.strip()
    
    if not code:
        await update.message.reply_text("❌ Invalid code!", reply_markup=cancel_menu())
        return YOGA_LINK
    
    context.user_data["yoga_code"] = code
    context.user_data["yoga_state"] = YOGA_NUM_TYPE
    
    await update.message.reply_text(
        "✅ *Code set!*\n\n📞 *Select number type:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🇮🇳 Indian (10 digits)", callback_data="yoga_indian")],
            [InlineKeyboardButton("🌍 International (+)", callback_data="yoga_intl")],
            [InlineKeyboardButton("❌ Cancel", callback_data="main_menu")],
        ])
    )
    return YOGA_NUM_TYPE

async def yoga_num_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "main_menu":
        await query.edit_message_text("❌ Cancelled.", reply_markup=back_menu())
        context.user_data.clear()
        return ConversationHandler.END
    
    context.user_data["yoga_num_type"] = "indian" if data == "yoga_indian" else "international"
    await query.edit_message_text(
        "📱 *Enter phone number:*",
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    )
    context.user_data["yoga_state"] = YOGA_PHONE
    return YOGA_PHONE

async def yoga_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    refer_code = context.user_data.get("yoga_code", "")
    
    status = await update.message.reply_text(f"⏳ *Processing...*\n📱 `{phone}`", parse_mode="Markdown")
    
    did, sid = str(uuid.uuid4()), str(uuid.uuid4())
    reg_resp, reg_err = await yoga_api_post(REGISTER_URL, {
        "name": random.choice(YOGA_NAMES),
        "phoneNumber": phone,
        "referredBy": refer_code,
        "sourceData": {"type": "Referral"},
        "experimentMetaInfo": {"deviceId": did, "sessionId": sid},
    }, YOGA_REG_HEADERS)
    
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
    
    otp_resp, otp_err = await yoga_api_post(LOGIN_URL, {
        "method": "phone_otp",
        "otpChannel": "sms",
        "phoneNumber": phone,
        "experimentMetaInfo": {"deviceId": otp_did, "sessionId": otp_sid},
        "registerUser": False,
    }, YOGA_HEADERS)
    
    if otp_err or not otp_resp:
        await status.edit_text("⚠️ *OTP Nahi Gaya!*", parse_mode="Markdown", reply_markup=back_menu())
        return ConversationHandler.END
    
    otp_ref = otp_resp.get("data", {}).get("refrence_code")
    if not otp_ref:
        await status.edit_text("⚠️ *OTP Nahi Gaya!*", parse_mode="Markdown", reply_markup=back_menu())
        return ConversationHandler.END
    
    context.user_data["yoga_otp_ref"] = otp_ref
    await status.edit_text(
        f"✅ *OTP Bhej Diya!*\n📱 `{phone}`\n\n🔐 *6-digit OTP:*",
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    )
    context.user_data["yoga_state"] = YOGA_OTP
    return YOGA_OTP

async def yoga_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    verify_resp, verify_err = await yoga_api_post(VERIFY_URL, {
        "phone": phone,
        "reference_code": otp_ref,
        "otp": otp,
        "experimentMetaInfo": {"deviceId": did, "sessionId": sid},
        "registerUser": False,
    }, YOGA_HEADERS)
    
    if verify_err or not verify_resp:
        await proc.edit_text("❌ *OTP Galat!*", parse_mode="Markdown", reply_markup=back_menu())
        return YOGA_OTP
    
    await proc.edit_text(
        f"🎉 *REFER COMPLETE!*\n\n"
        f"📱 `{phone}`\n\n"
        f"📢 @viedietlooters",
        parse_mode="Markdown",
        reply_markup=back_menu()
    )
    context.user_data.clear()
    return ConversationHandler.END

async def yoga_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Yoga callbacks"""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "main_menu":
        await query.edit_message_text("❌ Cancelled.", reply_markup=back_menu())
        context.user_data.clear()
        return ConversationHandler.END
