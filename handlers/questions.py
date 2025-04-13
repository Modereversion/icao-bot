import json
import random
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import QUESTIONS_FILE
from keyboards import get_main_keyboard
from utils.tts import generate_voice

# Хранилище вопросов
try:
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        QUESTIONS = json.load(f)
except Exception as e:
    logging.error(f"Ошибка загрузки файла вопросов: {e}")
    QUESTIONS = []

# Глобальное хранилище состояний пользователя
user_data = {}

def get_user_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "easy_done": [],
            "hard_done": [],
            "last_question": None,
            "language": "en",
            "auto_repeat": False,
            "answer_display_count": 0,
            "q_translate_count": 0,
            "a_translate_count": 0,
            "level": "easy"
        }
    return user_data[user_id]

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает текстовые сообщения от пользователя, в том числе кнопки из Reply-клавиатуры.
    """
    msg = update.message.text.strip().lower()
    logging.info(f"[DEBUG] Получено сообщение: '{msg}'")
    
    user_id = update.effective_user.id
    data = get_user_data(user_id)
    lang = data.get("language", "en")
    level = data.get("level", "easy")

    # Ожидаемые тексты кнопок
    btn_next    = "✈️ следующий вопрос" if lang == "ru" else "✈️ next question"
    btn_answer  = "💬 ответ" if lang == "ru" else "💬 answer"
    btn_q_trans = "🌍 перевод вопроса" if lang == "ru" else "🌍 translate question"
    btn_a_trans = "🇷🇺 перевод ответа" if lang == "ru" else "🇷🇺 translate answer"
    btn_support = "💳 поддержать проект" if lang == "ru" else "💳 support project"

    # Аналогично вашей логике – проверяем, содержит ли msg подстроку
    if btn_support in msg:
        # ...
        return

    if btn_next in msg:
        # ...
        return

    if btn_answer in msg:
        # ...
        return

    if btn_q_trans in msg:
        # ...
        return

    if btn_a_trans in msg:
        # ...
        return

    # Если не совпало – предлагаем пользоваться кнопками
    await update.message.reply_text("❓ Используй кнопки меню." if lang == "ru" else "❓ Please use the menu buttons.")


# === НОВАЯ ФУНКЦИЯ для обрабоки inline‑колбэков switch_to_hard и reset_progress ===
async def handle_questions_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка inline-колбэков, связанных с вопросами:
    - switch_to_hard (перейти к сложным вопросам)
    - reset_progress (сбросить прогресс)
    """
    query = update.callback_query
    user_id = query.from_user.id
    data = get_user_data(user_id)

    await query.answer()

    lang = data.get("language", "en")

    if query.data == "switch_to_hard":
        data["level"] = "hard"
        context.user_data["level"] = "hard"
        text = "Теперь будут сложные вопросы!" if lang == "ru" else "Now you're in hard question mode!"
        await query.edit_message_text(text)
        # Если хотите, можете отправить новое сообщение:
        # await query.message.reply_text("...")

    elif query.data == "reset_progress":
        # Сбрасываем все данные для пользователя
        data["easy_done"] = []
        data["hard_done"] = []
        data["last_question"] = None
        data["answer_display_count"] = 0
        data["q_translate_count"] = 0
        data["a_translate_count"] = 0
        data["level"] = "easy"
        # Редактируем сообщение
        text = "Прогресс сброшен, возврат к лёгким вопросам" if lang == "ru" else "Progress reset, back to easy questions"
        await query.edit_message_text(text)
