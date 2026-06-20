#!/usr/bin/env python3
"""
⚡ VIEDIET BYPASS - Main Controller
Teeno features ek saath, alag-alag files mein
Channel: @viedietlooters
"""

import os
import asyncio
import logging
import importlib.util
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== LOGGING ====================
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger(__name__)

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not set!")
    exit(1)

# ==================== KEYBOARDS ====================

def main_menu():
    return ReplyKeyboardMarkup(
        [
            ["🔄 Brevistay Bypass"],
            ["🛒 Flipkart Checker"],
            ["🧘 Habit.Yoga Referral"],
            ["📊 Status"]
        ],
        resize_keyboard=True,
        is_persistent=True
    )

# ==================== LOAD FEATURES DYNAMICALLY ====================

async def load_feature(module_name, function_name, *args, **kwargs):
    """Dynamically load and call a function from a feature module"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, f"{module_name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        func = getattr(module, function_name)
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error loading {module_name}: {e}")
        return None

# ==================== BOT HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main start command"""
    await update.message.reply_text(
        "⚡ *VIEDIET BYPASS* ⚡\n\n"
        "Select a feature below:\n\n"
        "📢 @viedietlooters",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks - route to respective feature"""
    text = update.message.text
    
    if text == "🔄 Brevistay Bypass":
        await load_feature("brevistay", "brevistay_start", update, context)
    
    elif text == "🛒 Flipkart Checker":
        await update.message.reply_text(
            "🛒 *Flipkart Checker*\n\nSend me a 10-digit number:",
            parse_mode="Markdown"
        )
        context.user_data["feature"] = "flipkart"
    
    elif text == "🧘 Habit.Yoga Referral":
        await load_feature("yogahabit", "yoga_start", update, context)
    
    elif text == "📊 Status":
        await update.message.reply_text(
            "📊 *Bot Status*\n\n"
            "✅ Bot is running!\n"
            "🔹 Brevistay Bypass: Active\n"
            "🔹 Flipkart Checker: Active\n"
            "🔹 Habit.Yoga Referral: Active\n\n"
            "📢 @viedietlooters",
            parse_mode="Markdown"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle normal messages"""
    feature = context.user_data.get("feature")
    
    if feature == "flipkart":
        await load_feature("flipkart", "flipkart_check", update, context)
    else:
        await update.message.reply_text("Use the buttons below:", reply_markup=main_menu())

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries"""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "main_menu":
        await query.edit_message_text(
            "⚡ *VIEDIET BYPASS* ⚡\n\nSelect a feature:",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
        return
    
    # Route to respective feature
    if data.startswith("brev_"):
        await load_feature("brevistay", "brev_callback", update, context)
    elif data.startswith("yoga_"):
        await load_feature("yogahabit", "yoga_callback", update, context)

# ==================== MAIN ====================

async def main():
    """Main entry point"""
    logger.info("⚡ Viediet Bypass Controller starting...")
    logger.info("📢 Channel: @viedietlooters")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^(🔄 Brevistay Bypass|🛒 Flipkart Checker|🧘 Habit.Yoga Referral|📊 Status)$"), button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    logger.info("✅ Bot is running!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
