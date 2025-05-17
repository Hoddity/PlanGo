import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from bot.database import DB_PATH

async def unregister(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /unregister <id>")
        return

    masterclass_id = context.args[0]
    user_id = update.effective_user.id

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT status FROM registrations WHERE user_id=? AND masterclass_id=?", (user_id, masterclass_id))
    row = cur.fetchone()

    if not row:
        await update.message.reply_text("Вы не записаны на этот мастер-класс.")
        conn.close()
        return

    cur.execute("DELETE FROM registrations WHERE user_id=? AND masterclass_id=?", (user_id, masterclass_id))
    conn.commit()

    cur.execute("""
        SELECT user_id FROM registrations
        WHERE masterclass_id=? AND status='waitlist'
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
    conn.close()
