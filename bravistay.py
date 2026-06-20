#!/usr/bin/env python3
"""
🔄 BREVISTAY BYPASS - Feature Module
"""
import os
import random
import asyncio
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)

BASE_URL = "https://cst.brevistay.com"
FIRST_NAMES = ["Amit", "Rahul", "Priya", "Neha", "Rohan", "Anjali", "Vikas", "Pooja"]
LAST_NAMES = ["Sharma", "Verma", "Singh", "Kumar", "Gupta", "Patel", "Reddy", "Jain"]

(PHONE, REFER_CODE, OTP) = range(3)

def cancel_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="main_menu")]
    ])

def brev_headers():
    return {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; Pixel 4)",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

async def brevistay_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start Brevistay bypass"""
    await update.message.reply_text(
        "🔄 *Brevistay Bypass*\n\n"
        "Enter 10-digit unregistered number:",
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    )
    context.user_data["brev_state"] = PHONE
    return PHONE

async def brev_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    if not txt.isdigit() or len(txt) != 10:
        await update.message.reply_text("❌ Enter exactly 10 digits.", reply_markup=cancel_menu())
        return PHONE
    
    context.user_data["brev_mobile"] = txt
    await update.message.reply_text(
        "🎯 *Enter Brevistay referral code:*",
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    )
    context.user_data["brev_state"] = REFER_CODE
    return REFER_CODE

async def brev_refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["brev_code"] = update.message.text.strip()
    data = context.user_data
    
    status = await update.message.reply_text(f"⏳ Requesting OTP for {data['brev_mobile']}...")
    
    payload = {
        "is_otp": 1,
        "is_password": 0,
        "mobile": int(data["brev_mobile"]),
        "otp": 123456,
        "password": ""
    }
    
    try:
        resp = await asyncio.to_thread(
            lambda: requests.post(f"{BASE_URL}/app-api/login", json=payload, headers=brev_headers(), timeout=45, verify=False)
        )
        resp_data = resp.json()
        
        if str(resp_data.get("is_user_registered")) == "1":
            await status.edit_text("⚠️ Number already registered!", reply_markup=cancel_menu())
            context.user_data.clear()
            return ConversationHandler.END
        
        if str(resp_data.get("is_otp_sent")) == "1":
            context.user_data["brev_otp_ref"] = resp_data.get("refrence_code")
            await status.edit_text("✅ *OTP Sent!*\n\nEnter 6-digit OTP:", parse_mode="Markdown", reply_markup=cancel_menu())
            context.user_data["brev_state"] = OTP
            return OTP
        else:
            await status.edit_text(f"❌ Failed: {resp_data.get('msg', 'Unknown')}", reply_markup=cancel_menu())
            context.user_data.clear()
            return ConversationHandler.END
    except Exception as e:
        await status.edit_text(f"❌ Error: {e}", reply_markup=cancel_menu())
        context.user_data.clear()
        return ConversationHandler.END

async def brev_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    otp = update.message.text.strip()
    if not otp.isdigit() or len(otp) != 6:
        await update.message.reply_text("❌ Enter 6 digits.", reply_markup=cancel_menu())
        return OTP
    
    data = context.user_data
    fname = random.choice(FIRST_NAMES)
    lname = random.choice(LAST_NAMES)
    email = f"{fname.lower()}{lname.lower()}{random.randint(100,999)}@gmail.com"
    
    status = await update.message.reply_text("⏳ Creating account...")
    
    payload = {
        "channel": "MOBILE", "email": email, "is_otp": 1, "is_password": 0,
        "lastName": lname, "mobile": int(data["brev_mobile"]), "name": fname,
        "otp": int(otp), "password": "xxxxx",
        "ref_code": data["brev_code"],
        "age": random.randint(20, 35), "gender": random.choice(["MALE", "FEMALE"])
    }
    
    try:
        resp = await asyncio.to_thread(
            lambda: requests.post(f"{BASE_URL}/app-api/verify-user", json=payload, headers=brev_headers(), timeout=45, verify=False)
        )
        resp_data = resp.json()
        
        if resp_data.get("status") == "SUCCESS":
            await status.edit_text(
                f"🎉 *ACCOUNT BYPASSED!*\n\n"
                f"👤 Name: {resp_data.get('user_first_name', fname)}\n"
                f"📧 Email: {resp_data.get('user_email_id', email)}\n"
                f"🎫 New Code: `{resp_data.get('user_referral_code', 'N/A')}`\n\n"
                "📢 @viedietlooters",
                parse_mode="Markdown",
                reply_markup=cancel_menu()
            )
        else:
            await status.edit_text(f"❌ Failed: {resp_data.get('msg', 'Unknown')}", reply_markup=cancel_menu())
    except Exception as e:
        await status.edit_text(f"❌ Error: {e}", reply_markup=cancel_menu())
    
    context.user_data.clear()
    return ConversationHandler.END

async def brev_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Brevistay callbacks"""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "brev_cancel" or data == "main_menu":
        await query.edit_message_text("❌ Cancelled.", reply_markup=cancel_menu())
        context.user_data.clear()
        return ConversationHandler.END
