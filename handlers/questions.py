import json
import random
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
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
            # Счётчики переводов: изначально 0
            "q_translate_count": 0,
            "a_translate_count": 0,
        }
    return user_data[user_id]

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text.strip()
    data = get_user_data(user_id)

    # Получаем язык из контекста, но для вопросов и ответов всегда используем английский
    lang = context.user_data.get("language", data.get("language", "en"))
    level = context.user_data.get("level", "easy")
    data["language"] = lang
    context.user_data["language"] = lang

    # Генерация меток для кнопок (отображаются согласно языку интерфейса)
    btn_next = "✈️ Следующий вопрос" if lang == "ru" else "✈️ Next question"
    btn_answer = "💬 Ответ" if lang == "ru" else "💬 Answer"
    btn_q_trans = "🌍 Перевод вопроса" if lang == "ru" else "🌍 Translate question"
    btn_a_trans = "🇷🇺 Перевод ответа" if lang == "ru" else "🇷🇺 Translate answer"

    logging.info(f"[USER {user_id}] Сообщение: {msg} | Язык: {lang} | Уровень: {level}")

    # --- Обработка кнопки "Следующий вопрос" ---
    if msg == btn_next:
        available = [q for q in QUESTIONS if q["level"] == level and q["id"] not in data[f"{level}_done"]]
        if not available:
            # Если закончились простые вопросы, отправляем инлайн-клавиатуру для выбора дальнейшего действия
            if level == "easy":
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("Перейти к сложным", callback_data="switch_to_hard"),
                        InlineKeyboardButton("Начать сначала", callback_data="reset_progress")
                    ]
                ])
                await update.message.reply_text(
                    "✅ Вы ответили на все простые вопросы. Что хотите сделать дальше?",
                    reply_markup=keyboard
                )
            else:
                # Если закончились сложные вопросы, предлагаем только начать сначала
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Начать сначала", callback_data="reset_progress")]
                ])
                await update.message.reply_text(
                    "✅ Все вопросы завершены. Хотите начать сначала?",
                    reply_markup=keyboard
                )
            return

        question = random.choice(available)
        data[f"{level}_done"].append(question["id"])
        data["last_question"] = question

        # Сбрасываем счетчики переводов при выборе нового вопроса
        data["q_translate_count"] = 0
        data["a_translate_count"] = 0

        # Всегда отправляем вопрос на английском независимо от выбранного языка интерфейса
        await update.message.reply_text(f"📝 {question['question_en']}")
        voice = generate_voice(question['question_en'])
        if voice:
            await update.message.reply_voice(voice)
        return

    # --- Обработка кнопки "Ответ" ---
    if msg == btn_answer:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
            return
        await update.message.reply_text(f"✅ {q['answer_en']}")
        voice = generate_voice(q['answer_en'])
        if voice:
            await update.message.reply_voice(voice)
        return

    # --- Обработка кнопки "Перевод вопроса" ---
    if msg == btn_q_trans:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
            return
        q_trans_count = data.get("q_translate_count", 0)
        if q_trans_count == 0:
            # Первый перевод – отправляем перевод вопроса
            await update.message.reply_text(f"🌍 {q['question_ru']}")
            data["q_translate_count"] = 1
        elif q_trans_count == 1:
            # Второе нажатие – сообщаем, что вопрос уже переведен
            await update.message.reply_text("❗ Вопрос уже переведен" if lang == "ru" else "❗ Question already translated")
            data["q_translate_count"] = 2
        else:
            # Третье и последующие нажатия – ничего не делаем
            return
        return

    # --- Обработка кнопки "Перевод ответа" ---
    if msg == btn_a_trans:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
            return
        a_trans_count = data.get("a_translate_count", 0)
        if a_trans_count == 0:
            # Первый перевод – отправляем перевод ответа
            await update.message.reply_text(f"🇷🇺 {q['answer_ru']}")
            data["a_translate_count"] = 1
        elif a_trans_count == 1:
            # Второе нажатие – сообщаем, что ответ уже переведен
            await update.message.reply_text("❗ Ответ уже переведен" if lang == "ru" else "❗ Answer already translated")
            data["a_translate_count"] = 2
        else:
            # Третье и последующие – ничего не делаем
            return
        return

    await update.message.reply_text("❓ Используй кнопки меню." if lang == "ru" else "❓ Please use the menu buttons.")
