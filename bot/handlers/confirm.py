import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from bot.database import DB_PATH

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /confirm <id>")
        return

    masterclass_id = context.args[0]
    user_id = update.effective_user.id

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT status FROM registrations 
        WHERE user_id=? AND masterclass_id=?
    """, (user_id, masterclass_id))
    row = cur.fetchone()

    if not row:
        await update.message.reply_text("Вы не в листе ожидания на этот мастер-класс.")
        conn.close()
        return

    if row[0] != 'confirmed':
        await update.message.reply_text("Сейчас вы не можете подтвердить участие.")
        conn.close()
        return

    await update.message.reply_text("Ваше участие подтверждено!")
    conn.close()
