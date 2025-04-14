from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID

def get_main_keyboard(user_id, lang="en"):
    keyboard = []

    # ⚙️ Настройки
    row = ["⚙️ Настройки" if lang == "ru" else "⚙️ Settings"]

    # 💳 Поддержать
    row.append("💳 Поддержать проект" if lang == "ru" else "💳 Support project")
    keyboard.append(row)

    # 🛠️ Админ-панель (только для ADMIN_ID)
    if user_id == ADMIN_ID:
        admin_text = "🛠️ Управление" if lang == "ru" else "🛠️ Admin"
        keyboard.append([admin_text])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_language_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ])

def get_difficulty_keyboard(lang="en", current=None):
    emoji_easy = "🛫"
    emoji_hard = "🚀"
    text_easy = f"{emoji_easy} Лёгкий" if lang == "ru" else f"{emoji_easy} Easy"
    text_hard = f"{emoji_hard} Сложный" if lang == "ru" else f"{emoji_hard} Hard"
    if current == "easy":
        text_easy += " ✅"
    if current == "hard":
        text_hard += " ✅"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text_easy, callback_data="level_easy"),
         InlineKeyboardButton(text_hard, callback_data="level_hard")]
    ])
