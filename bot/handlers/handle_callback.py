import sqlite3
import time
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from bot.database import DB_PATH

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    action, masterclass_id = data.split(":")
    masterclass_id = int(masterclass_id)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if action == "register":
        cur.execute("SELECT capacity FROM masterclasses WHERE id=?", (masterclass_id,))
        row = cur.fetchone()
        if not row:
            await query.edit_message_text("Мастер-класс не найден.")
            return

        capacity = row[0]

        cur.execute("SELECT COUNT(*) FROM registrations WHERE masterclass_id=? AND status='registered'", (masterclass_id,))
        registered_count = cur.fetchone()[0]

        cur.execute("SELECT status FROM registrations WHERE user_id=? AND masterclass_id=?", (user_id, masterclass_id))
        existing = cur.fetchone()
        if existing:
            await query.edit_message_text(f"Вы уже записаны. Статус: {existing[0]}")
            return

        timestamp = int(time.time())
        if registered_count < capacity:
            cur.execute("INSERT INTO registrations (user_id, masterclass_id, status, timestamp) VALUES (?, ?, 'registered', ?)",
                        (user_id, masterclass_id, timestamp))
            await query.edit_message_text("Вы успешно записались на мастер-класс!")
        else:
            cur.execute("INSERT INTO registrations (user_id, masterclass_id, status, timestamp) VALUES (?, ?, 'waitlist', ?)",
                        (user_id, masterclass_id, timestamp))

            cur.execute("SELECT COUNT(*) FROM registrations WHERE masterclass_id=? AND status='waitlist' AND timestamp<=?",
                        (masterclass_id, timestamp))
            position = cur.fetchone()[0]

            await query.edit_message_text(
                f"Все места заняты. Вы добавлены в лист ожидания. Ваша позиция: {position}"
            )

    elif action == "unregister":
        cur.execute("SELECT status FROM registrations WHERE user_id=? AND masterclass_id=?", (user_id, masterclass_id))
        row = cur.fetchone()

        if not row:
            await query.edit_message_text("Вы не записаны на этот мастер-класс.")
            return

        cur.execute("DELETE FROM registrations WHERE user_id=? AND masterclass_id=?", (user_id, masterclass_id))
        await query.edit_message_text("Вы успешно отписались от мастер-класса.")

        # Освободилось место — предложим следующему в очереди
        cur.execute("""SELECT user_id FROM registrations
                       WHERE masterclass_id=? AND status='waitlist'
                       ORDER BY timestamp ASC LIMIT 1""", (masterclass_id,))
        next_user = cur.fetchone()
        if next_user:
            next_id = next_user[0]
            cur.execute("""UPDATE registrations SET status='registered' 
                           WHERE user_id=? AND masterclass_id=?""", (next_id, masterclass_id))
            await context.bot.send_message(
                chat_id=next_id,
                text=f"📢 Освободилось место на мастер-класс #{masterclass_id}!\n"
                     f"Подтвердите участие в течение 15 минут командой:\n"
                     f"/confirm {masterclass_id}"
            )

    conn.commit()
    conn.close()
