from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import main_menu_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот PlanGo. Выберите действие:",
        reply_markup=main_menu_keyboard
    )
