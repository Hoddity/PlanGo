import sqlite3
import time
from telegram import Update
from telegram.ext import ContextTypes
from bot.database import DB_PATH

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Использование: /register <ID мастер-класса>")
        return

    masterclass_id = int(context.args[0])
    user_id = update.effective_user.id

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT capacity FROM masterclasses WHERE id=?", (masterclass_id,))
    row = cur.fetchone()
    if not row:
        await update.message.reply_text("Мастер-класс с таким ID не найден.")
        conn.close()
        return

    capacity = row[0]

    cur.execute("SELECT COUNT(*) FROM registrations WHERE masterclass_id=? AND status='registered'", (masterclass_id,))
    registered_count = cur.fetchone()[0]

    cur.execute("SELECT status FROM registrations WHERE user_id=? AND masterclass_id=?", (user_id, masterclass_id))
    existing = cur.fetchone()
    if existing:
        await update.message.reply_text(f"Вы уже записаны со статусом: {existing[0]}")
        conn.close()
        return

    timestamp = int(time.time())
    if registered_count < capacity:
        cur.execute("INSERT INTO registrations (user_id, masterclass_id, status, timestamp) VALUES (?, ?, 'registered', ?)",
                    (user_id, masterclass_id, timestamp))
        await update.message.reply_text("Вы успешно записаны на мастер-класс!")
    else:
        cur.execute("INSERT INTO registrations (user_id, masterclass_id, status, timestamp) VALUES (?, ?, 'waitlist', ?)",
                    (user_id, masterclass_id, timestamp))

        cur.execute("SELECT COUNT(*) FROM registrations WHERE masterclass_id=? AND status='waitlist' AND timestamp<=?",
                    (masterclass_id, timestamp))
        position = cur.fetchone()[0]

        await update.message.reply_text(
            f"Все места заняты. Вы добавлены в лист ожидания. Ваша позиция: {position}"
        )

    conn.commit()
    conn.close()
