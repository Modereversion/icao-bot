import json
import random
import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import QUESTIONS_FILE
from keyboards import get_main_keyboard
from utils.tts import generate_voice

# Загрузка вопросов из файла
try:
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        QUESTIONS = json.load(f)
except Exception as e:
    logging.error(f"Ошибка загрузки файла вопросов: {e}")
    QUESTIONS = []

# Словарь для хранения данных пользователей
user_data = {}

def get_user_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "easy_done": [],
            "hard_done": [],
            "last_question": None,
            "language": "en",
            "auto_repeat": False,
        }
    return user_data[user_id]

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text.strip()
    data = get_user_data(user_id)

    # Получаем язык из контекста, но для вопросов и ответов всегда используем английский.
    lang = context.user_data.get("language", data.get("language", "en"))
    level = context.user_data.get("level", "easy")
    data["language"] = lang
    context.user_data["language"] = lang

    # Генерация меток для кнопок (при этом кнопки отображаются согласно языку интерфейса)
    btn_next = "✈️ Следующий вопрос" if lang == "ru" else "✈️ Next question"
    btn_answer = "💬 Ответ" if lang == "ru" else "💬 Answer"
    btn_q_trans = "🌍 Перевод вопроса" if lang == "ru" else "🌍 Translate question"
    btn_a_trans = "🇷🇺 Перевод ответа" if lang == "ru" else "🇷🇺 Translate answer"

    logging.info(f"[USER {user_id}] Сообщение: {msg} | Язык: {lang} | Уровень: {level}")

    # Обработка кнопки "Следующий вопрос"
    if msg == btn_next:
        available = [q for q in QUESTIONS if q["level"] == level and q["id"] not in data[f"{level}_done"]]
        if not available:
            if level == "easy":
                context.user_data["level"] = "hard"
                await update.message.reply_text(
                    "🎉 Вы прошли все простые вопросы. Перехожу к сложным!" if lang == "ru"
                    else "🎉 All easy questions done. Switching to hard questions!"
                )
            else:
                await update.message.reply_text(
                    "✅ Все вопросы завершены. Хотите начать сначала?" if lang == "ru"
                    else "✅ All questions completed. Want to start over?"
                )
            return

        question = random.choice(available)
        data[f"{level}_done"].append(question["id"])
        data["last_question"] = question

        # Всегда отправляем вопрос на английском независимо от языка интерфейса
        await update.message.reply_text(f"📝 {question['question_en']}")
        voice = generate_voice(question['question_en'])
        if voice:
            await update.message.reply_voice(voice)
        return

    # Обработка кнопки "Ответ"
    if msg == btn_answer:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
            return
        # Всегда отправляем ответ на английском независимо от языка интерфейса
        await update.message.reply_text(f"✅ {q['answer_en']}")
        voice = generate_voice(q['answer_en'])
        if voice:
            await update.message.reply_voice(voice)
        return

    # Обработка кнопки "Перевод вопроса" (показываем русский вариант вопроса)
    if msg == btn_q_trans:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
            return
        await update.message.reply_text(f"🌍 {q['question_ru']}")
        return

    # Обработка кнопки "Перевод ответа" (показываем русский вариант ответа)
    if msg == btn_a_trans:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
            return
        await update.message.reply_text(f"🇷🇺 {q['answer_ru']}")
        return

    await update.message.reply_text("❓ Используй кнопки меню." if lang == "ru" else "❓ Please use the menu buttons.")
