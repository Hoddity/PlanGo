from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database import DB_PATH
import sqlite3

async def list_masterclasses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, title, time, location, capacity FROM masterclasses")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("Мастер-классы пока не добавлены.")
        return

    for r in rows:
        masterclass_id = r[0]
        title = r[1]
        time = r[2]
        location = r[3]
        capacity = r[4]

        text = f"🆔 ID: {masterclass_id}\n📌 Название: {title}\n🕒 Время: {time}\n📍 Место: {location}\n👥 Свободных мест: {capacity}"

        keyboard = [
            [InlineKeyboardButton("✅ Записаться", callback_data=f"register:{masterclass_id}")],
            [InlineKeyboardButton("❌ Отписаться", callback_data=f"unregister:{masterclass_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(text, reply_markup=reply_markup)
