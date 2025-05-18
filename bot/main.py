import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv
from bot.admin import add_classes_command
from bot.database import init_db, add_test_masterclasses
from bot.handlers import list_masterclasses, register, unregister, confirm, my
from bot.handlers.handle_callback import handle_callback
from bot.handlers.callback_router import callback_router
from bot.keyboards import main_menu_keyboard
from bot.handlers.text_handler import handle_text
from telegram import Update
from telegram.ext import ContextTypes

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Единственный start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот PlanGo. Выберите действие:",
        reply_markup=main_menu_keyboard,
    )

def main():
    init_db()
    add_test_masterclasses()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_masterclasses))
    app.add_handler(CommandHandler("my", my))
    app.add_handler(CommandHandler("unregister", unregister))
    app.add_handler(CommandHandler("confirm", confirm))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("add_classes", add_classes_command))

    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Обработка нажатий на кнопки
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
