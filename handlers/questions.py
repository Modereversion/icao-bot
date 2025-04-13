import json
import random
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import QUESTIONS_FILE
from keyboards import get_main_keyboard
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
    # Приводим к нижнему регистру
    msg = update.message.text.strip().lower()
    logging.info(f"[DEBUG] Получено сообщение: '{msg}'")

    user_id = update.effective_user.id
    data = get_user_data(user_id)
    lang = data.get("language", "en")
    level = data.get("level", "easy")

    btn_next    = "✈️ следующий вопрос" if lang == "ru" else "✈️ next question"
    btn_answer  = "💬 ответ" if lang == "ru" else "💬 answer"
    btn_q_trans = "🌍 перевод вопроса" if lang == "ru" else "🌍 translate question"
    btn_a_trans = "🇷🇺 перевод ответа" if lang == "ru" else "🇷🇺 translate answer"
    btn_support = "💳 поддержать проект" if lang == "ru" else "💳 support project"

    logging.info(f"[DEBUG] Ожидаемые кнопки: next='{btn_next}', answer='{btn_answer}', qtrans='{btn_q_trans}', atrans='{btn_a_trans}', support='{btn_support}'")

    # Поддержать проект
    if btn_support in msg:
        text_support = (
            "💳 Вы можете поддержать проект здесь:\nhttps://www.sberbank.com/sms/pbpn?requisiteNumber=79155691550"
            if lang == "ru"
            else
            "💳 You can support the project here:\nhttps://www.sberbank.com/sms/pbpn?requisiteNumber=79155691550"
        )
        await update.message.reply_text(text_support)
        return

    # Следующий вопрос
    if btn_next in msg:
        available = [q for q in QUESTIONS if q["level"] == level and q["id"] not in data[f"{level}_done"]]
        if not available:
            if level == "easy":
                # Предыдущий вариант, без «Перейти к сложным»
                if lang == "ru":
                    prompt = "✅ Все лёгкие вопросы пройдены. Хотите начать сначала?"
                else:
                    prompt = "✅ All easy questions completed. Do you want to start over?"
                await update.message.reply_text(prompt)
            else:
                # Когда сложные вопросы закончились, тоже предлагаем что-то
                if lang == "ru":
                    prompt = "✅ Все вопросы пройдены. Начнём заново?"
                else:
                    prompt = "✅ All questions done. Restart?"
                await update.message.reply_text(prompt)
            return

        question = random.choice(available)
        data[f"{level}_done"].append(question["id"])
        data["last_question"] = question
        data["answer_display_count"] = 0
        data["q_translate_count"] = 0
        data["a_translate_count"] = 0

        await update.message.reply_text(f"📝 {question['question_en']}")
        voice = generate_voice(question['question_en'])
        if voice:
            await update.message.reply_voice(voice)
        return

    # Ответ
    if btn_answer in msg:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
            return
        count = data["answer_display_count"]
        if count == 0:
            await update.message.reply_text(f"✅ {q['answer_en']}")
            voice = generate_voice(q['answer_en'])
            if voice:
                await update.message.reply_voice(voice)
            data["answer_display_count"] = 1
        elif count == 1:
            await update.message.reply_text("❗ Ответ уже выведен" if lang == "ru" else "❗ Answer already displayed")
            data["answer_display_count"] = 2
        else:
            return
        return

    # Перевод вопроса
    if btn_q_trans in msg:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
            return
        q_count = data["q_translate_count"]
        if q_count == 0:
            await update.message.reply_text(f"🌍 {q['question_ru']}")
            data["q_translate_count"] = 1
        elif q_count == 1:
            await update.message.reply_text("❗ Вопрос уже переведен" if lang == "ru" else "❗ Question already translated")
            data["q_translate_count"] = 2
        else:
            return
        return

    # Перевод ответа
    if btn_a_trans in msg:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
            return
        if data["answer_display_count"] == 0:
            await update.message.reply_text("❗ Сначала получите основной ответ" if lang == "ru" else "❗ Please display the main answer first")
            return
        a_count = data["a_translate_count"]
        if a_count == 0:
            await update.message.reply_text(f"🇷🇺 {q['answer_ru']}")
            data["a_translate_count"] = 1
        elif a_count == 1:
            await update.message.reply_text("❗ Ответ уже переведен" if lang == "ru" else "❗ Answer already translated")
            data["a_translate_count"] = 2
        else:
            return
        return

    # Иначе
    await update.message.reply_text(
        "❓ Используй кнопки меню." if lang == "ru" else "❓ Please use the menu buttons."
    )
