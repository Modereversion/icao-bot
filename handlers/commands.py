from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_main_keyboard

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang_code = update.effective_user.language_code or "en"
    # Если пользователь использует русскую раскладку, выбираем ru, иначе en
    lang = "ru" if lang_code.startswith("ru") else "en"
    context.user_data["language"] = lang
    context.user_data["level"] = "easy"

    if lang == "ru":
        welcome = (
            "👋 Привет! Добро пожаловать в **Level 4 Trainer** – твой персональный тренажер к сдаче устной части экзамена ИКАО! ✈️💼\n\n"
            "Здесь ты сможешь:\n"
            "• Тренировать ответы на экзаменационные вопросы 🎯\n"
            "• Получать голосовое сопровождение вопросов и ответов на английском языке 🔊🇬🇧\n"
            "• Переводить вопросы и ответы на русский язык 🌐🇷🇺\n"
            "• Отслеживать свой прогресс 📊 и совершенствовать навыки 🚀\n\n"
            "Нажми «Следующий вопрос», чтобы начать! 🌟"
        )
    else:
        welcome = (
            "👋 Hello! Welcome to **Level 4 Trainer** – your personal trainer for the ICAO oral exam! ✈️💼\n\n"
            "With this bot, you can:\n"
            "• Practice answers for exam questions 🎯\n"
            "• Receive voice support for questions and answers in English 🔊🇬🇧\n"
            "• Translate questions and answers into Russian 🌐🇷🇺\n"
            "• Track your progress 📊 and improve your skills 🚀\n\n"
            "Tap 'Next question' to get started! 🌟"
        )

    await update.message.reply_text(
        welcome,
        reply_markup=get_main_keyboard(user_id, lang)
    )
