from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from keyboards import get_main_keyboard

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang_code = update.effective_user.language_code or "en"
    lang = "ru" if lang_code.startswith("ru") else "en"
    context.user_data["language"] = lang
    context.user_data["level"] = "easy"

    welcome = (
        "👋 Привет! Добро пожаловать в Level 4 Trainer – твой тренажер к устной части экзамена ИКАО! ✈️\n\n"
        "Нажми «Следующий вопрос», чтобы начать 🚀"
        if lang == "ru" else
        "👋 Welcome to Level 4 Trainer – your personal ICAO speaking exam trainer! ✈️\n\n"
        "Tap 'Next question' to get started 🚀"
    )

    await update.message.reply_text(welcome, reply_markup=get_main_keyboard(user_id, lang))

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("language", "en")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Поддержать" if lang == "ru" else "💳 Support", callback_data="show_support_link")],
        [InlineKeyboardButton("🔙 Назад" if lang == "ru" else "🔙 Back", callback_data="back_to_main")]
    ])

    await update.message.reply_text(
        "💙 Спасибо за желание поддержать проект!" if lang == "ru"
        else "💙 Thank you for wanting to support the project!",
        reply_markup=keyboard
    )

async def handle_support_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = context.user_data.get("language", "en")
    await query.answer()

    if query.data == "show_support_link":
        text = (
            "🙏 Этот бот был создан одним человеком с нуля — с любовью к авиации и стремлением помочь другим в подготовке к экзамену ICAO.\n\n"
            "Если он оказался полезен — поддержать можно переводом на Сбер:\n"
            "https://www.sberbank.com/sms/pbpn?requisiteNumber=79155691550"
            if lang == "ru" else
            "🙏 This bot was built entirely by one person — with a love for aviation and a passion to help others prepare for the ICAO exam.\n\n"
            "If you found it helpful, you can support it via Sber transfer:\n"
            "https://www.sberbank.com/sms/pbpn?requisiteNumber=79155691550"
        )
        await query.edit_message_text(text)
    elif query.data == "back_to_main":
        text = (
            "🔙 Возвращаемся к обучению! Желаю отличной практики ✈️"
            if lang == "ru" else
            "🔙 Back to training! Wishing you a great practice session ✈️"
        )
        await query.edit_message_text(text)
