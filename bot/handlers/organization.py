from telegram import Update
from telegram.ext import ContextTypes

async def organization_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Организационная информация:\n\n"
        "🕒 Время: 25 мая, с 12:00 до 18:00\n"
        "📍 Место: Центр \"Созидание\", ул. Примерная, 12\n"
        "📱 Контакт: +7 900 123-45-67\n"
        "🎒 Возьмите с собой: блокнот, ручку и хорошее настроение 😊"
    )
