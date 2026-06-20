#!/usr/bin/env python3
"""
🛒 FLIPKART CHECKER - Feature Module
"""
import asyncio
import logging
import requests
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

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
            return "⚠️ Flipkart : Did not return JSON."

        response_block = jsonData.get('RESPONSE', {})
        user_details = response_block.get('userDetails', {})
        status = user_details.get(num_with_code)

        if status == "GUEST":
            return "❌ Flipkart : Not Registered (GUEST)"
        elif status == "VERIFIED":
            return "✅ Flipkart : Registered (VERIFIED)"
        else:
            return f"ℹ️ Flipkart : Unknown Status ({status})"

    except Exception as e:
        return f"⚠️ Flipkart : Error ({type(e).__name__}: {str(e)})"

async def flipkart_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Flipkart number check"""
    text = update.message.text
    digits = ''.join(filter(str.isdigit, text))
    num = digits[-10:] if len(digits) >= 10 else digits
    
    if len(num) != 10:
        await update.message.reply_text("⚠️ Send a valid 10-digit number.")
        return
    
    status_msg = await update.message.reply_text(f"🔍 Checking {num}...")
    result = await asyncio.to_thread(check_flipkart, num)
    await status_msg.edit_text(
        f"📱 *Result for {num}:*\n\n{result}\n\n📢 @viedietlooters",
        parse_mode="Markdown"
    )
    context.user_data["feature"] = None
