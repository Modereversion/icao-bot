from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from keyboards import get_language_keyboard, get_difficulty_keyboard, get_main_keyboard
from handlers.questions import get_user_data, user_data
from config import ADMIN_ID

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    telegram_lang = update.effective_user.language_code or "en"
    
    lang = context.user_data.get("language")
    if not lang:
        lang = "ru" if telegram_lang.startswith("ru") else "en"
        context.user_data["language"] = lang
    
    data = get_user_data(user_id)
    data["language"] = lang

    text = "⚙️ Настройки:" if lang == "ru" else "⚙️ Settings:"
    buttons = [
        [InlineKeyboardButton("🌐 Язык" if lang == "ru" else "🌐 Language", callback_data="change_language")],
        [InlineKeyboardButton("⚙️ Сложность" if lang == "ru" else "⚙️ Difficulty", callback_data="change_level")],
        [InlineKeyboardButton("📊 Прогресс" if lang == "ru" else "📊 Progress", callback_data="show_progress")],
        [InlineKeyboardButton("🔁 Начать сначала" if lang == "ru" else "🔁 Start over", callback_data="reset_progress")],
        [InlineKeyboardButton("🗣️ Оставить отзыв" if lang == "ru" else "🗣️ Leave feedback", callback_data="leave_feedback")]
    ]
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text, reply_markup=markup)

async def handle_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    lang = context.user_data.get("language", "en")
    level = context.user_data.get("level", "easy")
    data = get_user_data(user_id)
    
    def t(ru, en):
        return ru if lang == "ru"
