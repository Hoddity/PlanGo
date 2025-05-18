import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from bot.database import DB_PATH

ADMIN_IDS = [854059535]  #  Telegram ID организаторов

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return

    if not context.args:
        await update.message.reply_text("Использование: /notify ВАЖНОЕ_СООБЩЕНИЕ")
        return

    message = "🔔 ВАЖНО:\n" + " ".join(context.args)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT user_id FROM registrations")
    users = cur.fetchall()
    conn.close()

    count = 0
    for (user_id,) in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            count += 1
        except Exception:
            pass  # если пользователь заблокировал бота

    await update.message.reply_text(f"Сообщение отправлено {count} участникам.")
