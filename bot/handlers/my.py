import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from bot.database import DB_PATH

async def my(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT m.id, m.title, m.time, m.location, r.status
        FROM registrations r
        JOIN masterclasses m ON r.masterclass_id = m.id
        WHERE r.user_id=?
        ORDER BY m.time
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("Вы ещё не записаны ни на один мастер-класс.")
        return

    text = "Ваши записи:\n\n"
    for r in rows:
        text += (f"ID: {r[0]}\nНазвание: {r[1]}\nВремя: {r[2]}\nМесто: {r[3]}\nСтатус: {r[4]}\n\n")

    await update.message.reply_text(text)
