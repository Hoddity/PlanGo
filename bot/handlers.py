# bot/handlers.py
import sqlite3
import time
from telegram import Update
from telegram.ext import ContextTypes
from bot.database import DB_PATH

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Используй /list чтобы увидеть мастер-классы.")

async def list_masterclasses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, title, time, location, capacity FROM masterclasses")
        rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        await update.message.reply_text("Мастер-классы пока не добавлены.")
        return

    text = "Список мастер-классов:\n\n"
    for r in rows:
        text += (
            f"ID: {r[0]}\n"
            f"Название: {r[1]}\n"
            f"Время: {r[2]}\n"
            f"Место: {r[3]}\n"
            f"Свободных мест: {r[4]}\n\n"
        )
    await update.message.reply_text(text)

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Использование: /register <ID мастер-класса>")
        return

    masterclass_id = int(context.args[0])
    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("SELECT capacity FROM masterclasses WHERE id=?", (masterclass_id,))
        row = cur.fetchone()
        if not row:
            await update.message.reply_text("Мастер-класс с таким ID не найден.")
            return

        capacity = row[0]
        cur.execute(
            "SELECT COUNT(*) FROM registrations WHERE masterclass_id=? AND status='registered'",
            (masterclass_id,)
        )
        registered_count = cur.fetchone()[0]

        cur.execute(
            "SELECT status FROM registrations WHERE user_id=? AND masterclass_id=?",
            (user_id, masterclass_id)
        )
        existing = cur.fetchone()
        if existing:
            await update.message.reply_text(f"Вы уже записаны со статусом: {existing[0]}")
            return

        timestamp = int(time.time())
        if registered_count < capacity:
            cur.execute("""
                INSERT INTO registrations (user_id, masterclass_id, status, timestamp)
                VALUES (?, ?, 'registered', ?)
            """, (user_id, masterclass_id, timestamp))
            await update.message.reply_text("Вы успешно записаны на мастер-класс!")
        else:
            cur.execute("""
                INSERT INTO registrations (user_id, masterclass_id, status, timestamp)
                VALUES (?, ?, 'waiting', ?)
            """, (user_id, masterclass_id, timestamp))
            cur.execute("""
                SELECT COUNT(*) FROM registrations 
                WHERE masterclass_id=? AND status='waiting' AND timestamp<=?
            """, (masterclass_id, timestamp))
            position = cur.fetchone()[0]
            await update.message.reply_text(
                f"Все места заняты. Вы добавлены в лист ожидания. Ваша позиция: {position}"
            )

        conn.commit()
    finally:
        conn.close()

async def unregister(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /unregister <id>")
        return

    masterclass_id = context.args[0]
    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT status FROM registrations 
            WHERE user_id=? AND masterclass_id=?
        """, (user_id, masterclass_id))
        row = cur.fetchone()

        if not row:
            await update.message.reply_text("Вы не записаны на этот мастер-класс.")
            return

        cur.execute("""
            DELETE FROM registrations WHERE user_id=? AND masterclass_id=?
        """, (user_id, masterclass_id))
        conn.commit()

        cur.execute("""
            SELECT user_id FROM registrations
            WHERE masterclass_id=? AND status='waiting'
            ORDER BY timestamp ASC LIMIT 1
        """, (masterclass_id,))
        next_in_line = cur.fetchone()

        if next_in_line:
            next_user_id = next_in_line[0]
            cur.execute("""
                UPDATE registrations SET status='confirmed' 
                WHERE user_id=? AND masterclass_id=?
            """, (next_user_id, masterclass_id))
            conn.commit()

            await context.bot.send_message(
                chat_id=next_user_id,
                text=f"Освободилось место на мастер-класс #{masterclass_id}!\n"
                     f"Вы можете подтвердить участие в течение 15 минут командой:\n"
                     f"/confirm {masterclass_id}"
            )

        await update.message.reply_text("Вы успешно отписались от мастер-класса.")
    finally:
        conn.close()

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /confirm <id>")
        return

    masterclass_id = context.args[0]
    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT status FROM registrations 
            WHERE user_id=? AND masterclass_id=?
        """, (user_id, masterclass_id))
        row = cur.fetchone()

        if not row:
            await update.message.reply_text("Вы не в листе ожидания на этот мастер-класс.")
            return

        if row[0] != 'confirmed':
            await update.message.reply_text("Сейчас вы не можете подтвердить участие.")
            return

        cur.execute("""
            UPDATE registrations SET status='registered' 
            WHERE user_id=? AND masterclass_id=?
        """, (user_id, masterclass_id))
        conn.commit()
        await update.message.reply_text("Ваше участие подтверждено!")
    finally:
        conn.close()

async def my(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT m.id, m.title, m.time, m.location, r.status
            FROM registrations r
            JOIN masterclasses m ON r.masterclass_id = m.id
            WHERE r.user_id=?
            ORDER BY m.time
        """, (user_id,))
        rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        await update.message.reply_text("Вы ещё не записаны ни на один мастер-класс.")
        return

    text = "Ваши записи:\n\n"
    for r in rows:
        text += (
            f"ID: {r[0]}\n"
            f"Название: {r[1]}\n"
            f"Время: {r[2]}\n"
            f"Место: {r[3]}\n"
            f"Статус: {r[4]}\n\n"
        )
    await update.message.reply_text(text)
