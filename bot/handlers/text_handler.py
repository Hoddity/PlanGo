from telegram import Update
from telegram.ext import ContextTypes
from bot.handlers import list_masterclasses, my

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📅 Мероприятия":
        await list_masterclasses(update, context)

    elif text == "📝 Мои записи":
        await my(update, context)


    elif text == "ℹ️ Организация":

        await update.message.reply_text(

            "📌 Организационная информация:\n"

            "— Время сбора: 10:00 у входа в зал\n"

            "— Контакт организатора: @user\n"

            "— Что взять с собой: блокнот, ручку, хорошее настроение!"

        )


    else:
        await update.message.reply_text("Неизвестная команда. Пожалуйста, используйте кнопки.")
