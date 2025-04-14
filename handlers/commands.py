from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from keyboards import get_main_keyboard

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang_code = update.effective_user.language_code or "en"
    lang = "ru" if lang_code.startswith("ru") else "en"
    context.user_data["language"] = lang
    context.user_data["level"] = "easy"
    context.user_data["current_question"] = None

    if lang == "ru":
        text = (
            "👋 Привет! Добро пожаловать в Level 4 Trainer – твой персональный тренажер к устной части экзамена ИКАО!\n\n"
            "📋 Ты сможешь:\n"
            "• тренировать ответы на экзаменационные вопросы;\n"
            "• слушать озвучку на английском;\n"
            "• видеть переводы и следить за прогрессом.\n\n"
            "Нажми «Начать», чтобы перейти к первому вопросу 👇"
        )
        button = InlineKeyboardButton("🚀 Начать", callback_data="start_training")
    else:
        text = (
            "👋 Welcome to Level 4 Trainer – your personal ICAO speaking exam trainer!\n\n"
            "📋 You can:\n"
            "• practice answering ICAO-style questions;\n"
            "• hear native-like voiceover in English;\n"
            "• get translations and track your progress.\n\n"
            "Tap “Start” to begin 👇"
        )
        button = InlineKeyboardButton("🚀 Start", callback_data="start_training")

    markup = InlineKeyboardMarkup([[button]])
    await update.message.reply_text(text, reply_markup=markup)
