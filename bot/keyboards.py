from telegram import ReplyKeyboardMarkup, KeyboardButton

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📅 Мероприятия"), KeyboardButton("📝 Мои записи")],
        [KeyboardButton("ℹ️ Организация")]
    ],
    resize_keyboard=True
)
