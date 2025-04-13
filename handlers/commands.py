from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_main_keyboard
from handlers.questions import get_user_data
from datetime import datetime

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang_code = update.effective_user.language_code or "en"
    lang = "ru" if lang_code.startswith("ru") else "en"
    context.user_data["language"] = lang
    context.user_data["level"] = "easy"

    # Инициализация данных пользователя (если ещё не сохранены)
    data = get_user_data(user_id)
    if "first_launch" not in data:
        data["first_launch"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["first_name"] = update.effective_user.first_name or "-"
        data["last_name"] = update.effective_user.last_name or "-"
        data["username"] = update.effective_user.username or "-"
        # Для "страны" можно взять language_code, хотя это не страна, а язык
        data["country"] = update.effective_user.language_code or "-"

    welcome = ("✈️ Добро пожаловать в ICAO Bot!\nНажми 'Следующий вопрос', чтобы начать."
               if lang == "ru" else
               "✈️ Welcome to the ICAO Bot!\nTap 'Next question' to begin.")
    await update.message.reply_text(welcome, reply_markup=get_main_keyboard(user_id, lang))
