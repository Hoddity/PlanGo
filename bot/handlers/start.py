from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import main_menu_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот *PlanGo* — твой помощник на мероприятии.\n\n"
        "Вот что я умею:\n"
        "📋 *Мероприятия* — покажу все мастер-классы, доступные для записи\n"
        "✅ *Мои записи* — твой список зарегистрированных мастер-классов\n"
        "ℹ️ *Организация* — вся нужная информация: место, время, контакты\n"
        "🔔 *Уведомления* — сообщу, если освободится место или изменится расписание\n\n"
        "Выбери действие с помощью меню ниже 👇",
        reply_markup=main_menu_keyboard,
        parse_mode="Markdown"
    )
