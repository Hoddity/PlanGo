import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv
from bot.admin import add_classes_command
from bot.database import init_db, add_test_masterclasses
from bot.handlers import list_masterclasses, register, unregister, confirm, my
from bot.handlers.handle_callback import handle_callback


load_dotenv()
init_db()
TOKEN = os.getenv("BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("Добро пожаловать! Используй /list чтобы увидеть мастер-классы.")

def main():
    init_db()
    add_test_masterclasses()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_masterclasses))
    app.add_handler(CommandHandler("unregister", unregister))  # /unregister <id>
    app.add_handler(CommandHandler("confirm", confirm))  # /confirm <id>
    app.add_handler(CommandHandler("add_classes", add_classes_command))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("my", my))
    app.add_handler(CommandHandler("masterclasses", list_masterclasses))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
