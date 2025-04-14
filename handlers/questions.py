import json
import random
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Message
from telegram.ext import ContextTypes
from config import QUESTIONS_FILE
from utils.tts import generate_voice

try:
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        QUESTIONS = json.load(f)
except Exception as e:
    logging.error(f"Ошибка загрузки файла вопросов: {e}")
    QUESTIONS = []

user_data = {}

def get_user_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "language": "en",
            "level": "easy",
            "done_ids": [],
            "postponed": [],
            "last_question": None,
            "last_msg_id": None,
            "state": None
        }
    return user_data[user_id]

# 👋 Приветствие и запуск
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang_code = update.effective_user.language_code or "en"
    lang = "ru" if lang_code.startswith("ru") else "en"
    context.user_data["language"] = lang

    data = get_user_data(user_id)
    data["language"] = lang
    data["state"] = "start"

    welcome = (
        "👋 Привет! Добро пожаловать в **Level 4 Trainer** – твой тренажёр для устной части экзамена ИКАО!\n\n"
        "Нажми «🚀 Начать тренировку», чтобы приступить к первому вопросу."
        if lang == "ru" else
        "👋 Welcome to **Level 4 Trainer** – your ICAO speaking exam training assistant!\n\n"
        "Press «🚀 Start training» to begin."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Начать тренировку" if lang == "ru" else "🚀 Start training", callback_data="start_training")]
    ])

    await update.message.reply_text(welcome, reply_markup=keyboard)
