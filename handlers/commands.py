from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_main_keyboard

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang_code = update.effective_user.language_code or "en"
    lang = "ru" if lang_code.startswith("ru") else "en"
    context.user_data["language"] = lang
    context.user_data["level"] = "easy"

    welcome = ("✈️ Добро пожаловать в ICAO Bot!\nНажмите 'Следующий вопрос', чтобы начать."
               if lang == "ru" else
               "✈️ Welcome to the ICAO Bot!\nTap 'Next question' to begin.")
    await update.message.reply_text(
        welcome,
        reply_markup=get_main_keyboard(user_id, lang)
    )

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("language", "en")
    text = ("💳 Вы можете поддержать проект здесь:\nhttps://www.sberbank.com/sms/pbpn?requisiteNumber=79155691550"
            if lang == "ru" else
            "💳 You can support the project here:\nhttps://www.sberbank.com/sms/pbpn?requisiteNumber=79155691550")
    await update.message.reply_text(text)
