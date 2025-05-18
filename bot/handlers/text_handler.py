from telegram import Update
from telegram.ext import ContextTypes
from bot.handlers import list_masterclasses, my

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📅 Мероприятия":
        await list_masterclasses(update, context)

    elif text == "📝 Мои записи":
        await my(update, context)

    elif text == "ℹ️ О проекте":
        await update.message.reply_text(
            "Проект PlanGo — это умный бот для записи на мероприятия и управления регистрациями!"
        )

    else:
        await update.message.reply_text("Неизвестная команда. Пожалуйста, используйте кнопки.")
