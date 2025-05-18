from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import sqlite3
from bot.database import DB_PATH

from bot.handlers.handle_callback import handle_callback  # рег/отмена

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "list":
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, title, time FROM masterclasses")
        rows = cur.fetchall()
        conn.close()

        if not rows:
            await query.edit_message_text("Пока нет доступных мастер-классов.")
            return

        text = "📋 Доступные мастер-классы:\n\n"
        keyboard = []

        for row in rows:
            masterclass_id, title, time = row
            text += f"ID: {masterclass_id}\nНазвание: {title}\nВремя: {time}\n\n"
            keyboard.append([
                InlineKeyboardButton("✅ Записаться", callback_data=f"register:{masterclass_id}"),
                InlineKeyboardButton("❌ Отписаться", callback_data=f"unregister:{masterclass_id}")
            ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)

    elif data == "my":
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT m.title, m.time, m.location, r.status
            FROM registrations r
            JOIN masterclasses m ON r.masterclass_id = m.id
            WHERE r.user_id=?
            ORDER BY m.time
        """, (user_id,))
        rows = cur.fetchall()
        conn.close()

        if not rows:
            await query.edit_message_text("Вы не записаны ни на один мастер-класс.")
            return

        text = "👤 Ваши записи:\n\n"
        for r in rows:
            title, time, location, status = r
            text += f"Название: {title}\nВремя: {time}\nМесто: {location}\nСтатус: {status}\n\n"

        await query.edit_message_text(text)

    elif ":" in data:
        # делегируем обработку рег/отмены
        await handle_callback(update, context)
