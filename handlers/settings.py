from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from keyboards import get_language_keyboard, get_difficulty_keyboard, get_main_keyboard
from handlers.questions import get_user_data, user_data
from config import ADMIN_ID

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    telegram_lang = update.effective_user.language_code or "en"
    
    # Если язык не задан, устанавливаем по умолчанию на основе языка Telegram пользователя
    lang = context.user_data.get("language")
    if not lang:
        lang = "ru" if telegram_lang.startswith("ru") else "en"
        context.user_data["language"] = lang
    
    # Синхронизируем язык в пользовательских данных (user_data)
    data = get_user_data(user_id)
    data["language"] = lang

    # Формируем текст и кнопки для главного меню настроек
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
    
    # Получаем текущие настройки языка и уровня для данного пользователя
    lang = context.user_data.get("language", "en")
    level = context.user_data.get("level", "easy")
    data = get_user_data(user_id)
    
    # Функция для выбора нужного варианта перевода строк
    def t(ru, en): 
        return ru if lang == "ru" else en

    if query.data == "change_language":
        # Предлагаем выбор языка
        await query.edit_message_text(
            t("🌐 Выберите язык:", "🌐 Choose language:"), 
            reply_markup=get_language_keyboard()
        )
    elif query.data == "change_level":
        # Предлагаем выбор уровня сложности
        await query.edit_message_text(
            t("⚙️ Выберите уровень сложности:", "⚙️ Choose difficulty level:"), 
            reply_markup=get_difficulty_keyboard(lang, current=level)
        )
    elif query.data == "show_progress":
        easy = len(data["easy_done"])
        hard = len(data["hard_done"])
        answer_viewed = data.get("answers_viewed", 0)
        q_trans = data.get("q_translate_count", 0)
        a_trans = data.get("a_translate_count", 0)

        progress = (
            f"{t('📊 Прогресс:', '📊 Progress:')}\n"
            f"🛫 {t('Лёгкие вопросы', 'Easy questions')}: {easy}\n"
            f"🚀 {t('Сложные вопросы', 'Hard questions')}: {hard}\n"
            f"💬 {t('Просмотров ответа', 'Answers viewed')}: {answer_viewed}\n"
            f"🌍 {t('Переводов вопроса', 'Question translations')}: {q_trans}\n"
            f"🇷🇺 {t('Переводов ответа', 'Answer translations')}: {a_trans}"
        )
        await query.edit_message_text(progress)
    elif query.data == "reset_progress":
        # Сбрасываем все данные пользователя и устанавливаем уровень на "easy"
        context.user_data.clear()
        user_data[user_id] = {
            "easy_done": [],
            "hard_done": [],
            "last_question": None,
            "answers_viewed": 0,
            "q_translate_count": 0,
            "a_translate_count": 0,
            "language": lang,
            "level": "easy"
        }
        await query.edit_message_text(
            t("🔁 Прогресс сброшен. Начни сначала!", "🔁 Progress reset. Start over!")
        )
    elif query.data == "leave_feedback":
        # Переводим пользователя в режим оставления отзыва
        context.user_data["feedback_mode"] = True
        await query.edit_message_text(
            t("✍️ Напишите свой отзыв, и он будет отправлен автору.", "✍️ Please write your feedback message.")
        )
    elif query.data == "lang_en":
        # Смена языка на английский
        context.user_data["language"] = "en"
        user_data[user_id]["language"] = "en"
        await query.edit_message_text("🌐 Language set to English.")
        await query.message.reply_text("🔁 Keyboard updated.", reply_markup=get_main_keyboard(user_id, "en"))
    elif query.data == "lang_ru":
        # Смена языка на русский
        context.user_data["language"] = "ru"
        user_data[user_id]["language"] = "ru"
        await query.edit_message_text("🌐 Язык установлен: Русский.")
        await query.message.reply_text("🔁 Клавиатура обновлена.", reply_markup=get_main_keyboard(user_id, "ru"))
    elif query.data == "level_easy":
        # Выбор простых вопросов
        context.user_data["level"] = "easy"
        user_data[user_id]["level"] = "easy"
        await query.edit_message_text(t("🛫 Уровень установлен: Лёгкий", "🛫 Level set: Easy"))
    elif query.data == "level_hard":
        # Выбор сложных вопросов
        context.user_data["level"] = "hard"
        user_data[user_id]["level"] = "hard"
        await query.edit_message_text(t("🚀 Уровень установлен: Сложный", "🚀 Level set: Hard"))
    elif query.data == "switch_to_hard":
        # Переключение пользователя в режим сложных вопросов
        context.user_data["level"] = "hard"
        user_data[user_id]["level"] = "hard"
        await query.edit_message_text(
            "🚀 Режим сложных вопросов активирован!" if lang == "ru" else "🚀 Hard question mode activated!"
        )
        await query.message.reply_text("🔁 Обновляем клавиатуру...", reply_markup=get_main_keyboard(user_id, lang))

def get_settings_handlers():
    """Функция возвращает список обработчиков, чтобы их можно было подключить в main.py."""
    return [
        MessageHandler(filters.Regex("^(⚙️ настройки|⚙️ settings)$"), settings_command),
        CallbackQueryHandler(
            handle_settings_callback,
            pattern="^(change_language|change_level|show_progress|reset_progress|leave_feedback|lang_en|lang_ru|level_easy|level_hard|switch_to_hard)$"
        )
    ]
