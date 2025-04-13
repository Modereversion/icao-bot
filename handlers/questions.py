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

# Глобальный словарь для хранения данных пользователей
user_data = {}

def get_user_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "easy_done": [],
            "hard_done": [],
            "last_question": None,
            "language": "en",
            "auto_repeat": False,
            # Счётчики для текущего вопроса:
            "answer_display_count": 0,   # для кнопки "Ответ"
            "q_translate_count": 0,      # для кнопки "Перевод вопроса"
            "a_translate_count": 0,      # для кнопки "Перевод ответа"
        }
    return user_data[user_id]

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text.strip().lower()  # приводим к нижнему регистру и убираем лишние пробелы
    logging.info(f"[DEBUG] Получено сообщение: '{msg}'")
    
    data = get_user_data(user_id)
    lang = context.user_data.get("language", data.get("language", "en"))
    level = context.user_data.get("level", "easy")
    data["language"] = lang
    context.user_data["language"] = lang

    # Устанавливаем текст кнопок в зависимости от языка
    btn_next    = ("✈️ следующий вопрос" if lang == "ru" else "✈️ next question")
    btn_answer  = ("💬 ответ" if lang == "ru" else "💬 answer")
    btn_q_trans = ("🌍 перевод вопроса" if lang == "ru" else "🌍 translate question")
    btn_a_trans = ("🇷🇺 перевод ответа" if lang == "ru" else "🇷🇺 translate answer")
    btn_support = ("💳 поддержать проект" if lang == "ru" else "💳 support project")

    logging.info(f"[DEBUG] Ожидаемые кнопки: btn_next='{btn_next}', btn_answer='{btn_answer}', btn_q_trans='{btn_q_trans}', btn_a_trans='{btn_a_trans}', btn_support='{btn_support}'")

    # --- Обработка кнопки "Поддержать проект" ---
    if msg == btn_support:
        support_text = ("💳 Вы можете поддержать проект здесь:\nhttps://www.sberbank.com/sms/pbpn?requisiteNumber=79155691550" 
                        if lang == "ru" 
                        else "💳 You can support the project here:\nhttps://www.sberbank.com/sms/pbpn?requisiteNumber=79155691550")
        await update.message.reply_text(support_text)
        return

    # --- Обработка кнопки "Следующий вопрос" ---
    if msg == btn_next:
        available = [q for q in QUESTIONS if q["level"] == level and q["id"] not in data[f"{level}_done"]]
        if not available:
            if level == "easy":
                if lang == "ru":
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("Перейти к сложным", callback_data="switch_to_hard"),
                         InlineKeyboardButton("Начать сначала", callback_data="reset_progress")]
                    ])
                    prompt = "✅ Вы ответили на все простые вопросы. Что хотите сделать дальше?"
                else:
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("Switch to hard", callback_data="switch_to_hard"),
                         InlineKeyboardButton("Start over", callback_data="reset_progress")]
                    ])
                    prompt = "✅ All easy questions done. Choose next step:"
                await update.message.reply_text(prompt, reply_markup=keyboard)
            else:
                if lang == "ru":
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("Начать сначала", callback_data="reset_progress")]
                    ])
                    prompt = "✅ Все вопросы завершены. Хотите начать сначала?"
                else:
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("Start over", callback_data="reset_progress")]
                    ])
                    prompt = "✅ All questions completed. Start over?"
                await update.message.reply_text(prompt, reply_markup=keyboard)
            return

        question = random.choice(available)
        data[f"{level}_done"].append(question["id"])
        data["last_question"] = question

        # Сбрасываем все счётчики для нового вопроса
        data["answer_display_count"] = 0
        data["q_translate_count"] = 0
        data["a_translate_count"] = 0

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
        answer_count = data.get("answer_display_count", 0)
        if answer_count == 0:
            await update.message.reply_text(f"✅ {q['answer_en']}")
            voice = generate_voice(q['answer_en'])
            if voice:
                await update.message.reply_voice(voice)
            data["answer_display_count"] = 1
        elif answer_count == 1:
            await update.message.reply_text("❗ Ответ уже выведен" if lang == "ru" else "❗ Answer already displayed")
            data["answer_display_count"] = 2
        else:
            return
        return

    # --- Обработка кнопки "Перевод вопроса" ---
    if msg == btn_q_trans:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
            return
        q_trans_count = data.get("q_translate_count", 0)
        if q_trans_count == 0:
            await update.message.reply_text(f"🌍 {q['question_ru']}")
            data["q_translate_count"] = 1
        elif q_trans_count == 1:
            await update.message.reply_text("❗ Вопрос уже переведен" if lang == "ru" else "❗ Question already translated")
            data["q_translate_count"] = 2
        else:
            return
        return

    # --- Обработка кнопки "Перевод ответа" ---
    if msg == btn_a_trans:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
            return
        if data.get("answer_display_count", 0) == 0:
            await update.message.reply_text("❗ Сначала получите основной ответ" if lang == "ru" else "❗ Please display the main answer first")
            return
        a_trans_count = data.get("a_translate_count", 0)
        if a_trans_count == 0:
            await update.message.reply_text(f"🇷🇺 {q['answer_ru']}")
            data["a_translate_count"] = 1
        elif a_trans_count == 1:
            await update.message.reply_text("❗ Ответ уже переведен" if lang == "ru" else "❗ Answer already translated")
            data["a_translate_count"] = 2
        else:
            return
        return

    await update.message.reply_text("❓ Используй кнопки меню." if lang == "ru" else "❓ Please use the menu buttons.")
