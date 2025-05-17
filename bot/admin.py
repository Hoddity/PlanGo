from telegram import Update
from telegram.ext import ContextTypes
from bot.database import add_test_masterclasses

ADMIN_IDS = [854059535] # ← замени на свой ID

async def add_classes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return

    add_test_masterclasses()
    await update.message.reply_text("✅ Мастер-классы успешно добавлены.")
