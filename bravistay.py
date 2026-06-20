#!/usr/bin/env python3
"""
⚡ VIEDIET BYPASS - Brevistay Auto-Referral Bot
Brevistay auto-referral bypass with channel force join
Channel: @viedietlooters
Group: @viedietlooterschat
"""

import os
import random
import asyncio
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ContextTypes, ConversationHandler, MessageHandler, filters
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger(__name__)

# ==================== TOKEN ====================
# 🔑 YAHAN TOKEN DALO - Environment Variable se le raha hai
BOT_TOKEN = os.environ.get("VIEDIET_BOT_TOKEN", "")

# Agar direct dalna hai toh comment karke ye use karo:
# BOT_TOKEN = "YOUR_VIEDIET_BOT_TOKEN_HERE"

# ==================== CONFIG ====================
BASE_URL = "https://cst.brevistay.com"

# Force Join Channels
FORCE_CHANNELS = ["viedietlooters"]
FORCE_GROUP = "viedietlooterschat"

FIRST_NAMES = ["Amit", "Rahul", "Priya", "Neha", "Rohan", "Anjali", "Vikas", "Pooja", "Arun", "Kavita", "Rishabh", "Sneha", "Karan"]
LAST_NAMES = ["Sharma", "Verma", "Singh", "Kumar", "Gupta", "Patel", "Reddy", "Jain", "Das", "Yadav", "Mishra", "Chauhan"]

# ==================== API FUNCTIONS ====================

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

def generate_name():
    return random.choice(FIRST_NAMES), random.choice(LAST_NAMES)

# ==================== STATES ====================
(PHONE, REFER_CODE, OTP) = range(3)

# ==================== KEYBOARDS ====================

def cancel_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_bypass")]
    ])

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Start Bypass", callback_data="bypass_start")],
        [InlineKeyboardButton("📖 Help", callback_data="help")],
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/viedietlooters")],
        [InlineKeyboardButton("💬 Join Group", url="https://t.me/viedietlooterschat")],
    ])

def force_join_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/viedietlooters")],
        [InlineKeyboardButton("💬 Join Group", url="https://t.me/viedietlooterschat")],
        [InlineKeyboardButton("✅ I Have Joined", callback_data="check_joined")],
    ])

# ==================== FORCE JOIN CHECK ====================

async def is_channel_member(bot, user_id: int) -> bool:
    """Check if user has joined required channel"""
    for ch in FORCE_CHANNELS:
        try:
            member = await bot.get_chat_member(f"@{ch}", user_id)
            if member.status in (ChatMember.LEFT, ChatMember.KICKED, ChatMember.BANNED):
                return False
        except Exception as e:
            logger.warning(f"Channel check error: {e}")
            return False
    return True

# ==================== BOT HANDLERS ====================

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command with force join"""
    user_id = update.effective_user.id
    
    # Check if user has joined channel
    if not await is_channel_member(context.bot, user_id):
        await update.message.reply_text(
            "⚡ *VIEDIET BYPASS* ⚡\n\n"
            "🔒 *Access Denied!*\n\n"
            "Please join our channel and group first to use this bot:\n\n"
            "📢 @viedietlooters\n"
            "💬 @viedietlooterschat",
            parse_mode="Markdown",
            reply_markup=force_join_menu()
        )
        return
    
    await update.message.reply_text(
        "⚡ *VIEDIET BYPASS* ⚡\n\n"
        "Brevistay auto-referral bypass bot.\n\n"
        "📢 @viedietlooters\n"
        "💬 @viedietlooterschat",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "📖 *Help*\n\n"
        "1. Click 'Start Bypass' or use /bypass\n"
        "2. Enter 10-digit unregistered number\n"
        "3. Enter your Brevistay referral code\n"
        "4. Enter OTP received on phone\n"
        "5. Account created with your referral!\n\n"
        "⚠️ Number must be UNREGISTERED.\n\n"
        "📢 @viedietlooters",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

async def bypass_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start bypass conversation with force join check"""
    user_id = update.effective_user.id
    
    # Check force join
    if not await is_channel_member(context.bot, user_id):
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                "🔒 *Access Denied!*\n\nJoin channel first:\n📢 @viedietlooters",
                parse_mode="Markdown",
                reply_markup=force_join_menu()
            )
        else:
            await update.message.reply_text(
                "🔒 *Access Denied!*\n\nJoin channel first:\n📢 @viedietlooters",
                parse_mode="Markdown",
                reply_markup=force_join_menu()
            )
        return ConversationHandler.END
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "📱 *Enter 10-digit unregistered number:*",
            parse_mode="Markdown",
            reply_markup=cancel_menu()
        )
    else:
        await update.message.reply_text(
            "📱 *Enter 10-digit unregistered number:*",
            parse_mode="Markdown",
            reply_markup=cancel_menu()
        )
    return PHONE

async def check_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if user joined channel"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    if await is_channel_member(context.bot, user_id):
        await query.edit_message_text(
            "✅ *Thanks for joining!*\n\n"
            "Now you can use the bot.\n\n"
            "⚡ @viedietlooters",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
    else:
        await query.edit_message_text(
            "❌ *You haven't joined yet!*\n\n"
            "Please join:\n📢 @viedietlooters\n💬 @viedietlooterschat",
            parse_mode="Markdown",
            reply_markup=force_join_menu()
        )

async def bypass_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive phone number"""
    txt = update.message.text.strip()
    if not txt.isdigit() or len(txt) != 10:
        await update.message.reply_text(
            "❌ Invalid. Enter exactly 10 digits.",
            reply_markup=cancel_menu()
        )
        return PHONE
    
    context.user_data["mobile"] = txt
    await update.message.reply_text(
        "🎯 *Enter Brevistay referral code:*",
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    )
    return REFER_CODE

async def bypass_refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive referral code"""
    context.user_data["refer_code"] = update.message.text.strip()
    data = context.user_data
    
    status = await update.message.reply_text(
        f"⏳ Requesting OTP for {data['mobile']}..."
    )
    
    payload = {
        "is_otp": 1,
        "is_password": 0,
        "mobile": int(data["mobile"]),
        "otp": 123456,
        "password": ""
    }
    
    try:
        resp = await asyncio.to_thread(api_login_worker, payload)
        resp_data = resp.json()
        
        if str(resp_data.get("is_user_registered")) == "1":
            await status.edit_text(
                "⚠️ Number already registered!\n\nTry another number.",
                reply_markup=main_menu()
            )
            return ConversationHandler.END
        
        if str(resp_data.get("is_otp_sent")) == "1":
            context.user_data["otp_ref"] = resp_data.get("refrence_code")
            await status.edit_text(
                "✅ *OTP Sent!*\n\nEnter 6-digit OTP:",
                parse_mode="Markdown",
                reply_markup=cancel_menu()
            )
            return OTP
        else:
            await status.edit_text(
                f"❌ Failed: {resp_data.get('msg', 'Unknown')}",
                reply_markup=main_menu()
            )
            return ConversationHandler.END
            
    except Exception as e:
        await status.edit_text(
            f"❌ Error: {e}",
            reply_markup=main_menu()
        )
        return ConversationHandler.END

async def bypass_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive OTP and complete bypass"""
    otp = update.message.text.strip()
    if not otp.isdigit() or len(otp) != 6:
        await update.message.reply_text(
            "❌ Enter 6 digits.",
            reply_markup=cancel_menu()
        )
        return OTP
    
    data = context.user_data
    fname, lname = generate_name()
    email = f"{fname.lower()}{lname.lower()}{random.randint(100, 999)}@gmail.com"
    
    status = await update.message.reply_text("⏳ Creating account...")
    
    payload = {
        "channel": "MOBILE",
        "email": email,
        "is_otp": 1,
        "is_password": 0,
        "lastName": lname,
        "mobile": int(data["mobile"]),
        "name": fname,
        "otp": int(otp),
        "password": "xxxxx",
        "ref_code": data["refer_code"],
        "age": random.randint(20, 35),
        "gender": random.choice(["MALE", "FEMALE"])
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
                "⚡ *Viediet Bypass*\n"
                "📢 @viedietlooters",
                parse_mode="Markdown",
                reply_markup=main_menu()
            )
        else:
            await status.edit_text(
                f"❌ Failed: {resp_data.get('msg', 'Unknown')}",
                reply_markup=main_menu()
            )
            
    except Exception as e:
        await status.edit_text(
            f"❌ Error: {e}",
            reply_markup=main_menu()
        )
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_bypass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel bypass"""
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "❌ Cancelled.",
            reply_markup=main_menu()
        )
    else:
        await update.message.reply_text(
            "❌ Cancelled.",
            reply_markup=main_menu()
        )
    context.user_data.clear()
    return ConversationHandler.END

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_joined":
        return await check_joined(update, context)
    
    if query.data == "bypass_start":
        return await bypass_start(update, context)
    
    if query.data == "help":
        await query.edit_message_text(
            "📖 *Help*\n\n"
            "1. Start Bypass\n"
            "2. Enter 10-digit number\n"
            "3. Enter referral code\n"
            "4. Enter OTP\n\n"
            "⚠️ Number must be UNREGISTERED.\n\n"
            "📢 @viedietlooters",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
    
    if query.data == "cancel_bypass":
        await query.edit_message_text(
            "❌ Cancelled.",
            reply_markup=main_menu()
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    return ConversationHandler.END

# ==================== MAIN ====================

async def main():
    """Main entry point"""
    if not BOT_TOKEN:
        logger.error("❌ VIEDIET_BOT_TOKEN not set!")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("bypass", bypass_start),
            CallbackQueryHandler(callback_handler, pattern="^bypass_start$"),
        ],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bypass_phone)],
            REFER_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bypass_refer)],
            OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, bypass_otp)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_bypass),
            CallbackQueryHandler(callback_handler, pattern="^cancel_bypass$"),
        ],
        per_user=True,
        allow_reentry=True,
    )
    
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    logger.info("✅ Viediet Bypass Bot is running!")
    logger.info("📢 Channel: @viedietlooters")
    logger.info("💬 Group: @viedietlooterschat")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())