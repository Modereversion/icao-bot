import json
import random
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import QUESTIONS_FILE, ADMIN_ID
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
            "answer_display_count": 0,     # для кнопки "Ответ"
            "q_translate_count": 0,        # для кнопки "Перевод вопроса"
            "a_translate_count": 0         # для кнопки "Перевод ответа"
        }
    return user_data[user_id]

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text.strip()
    data = get_user_data(user_id)

    # Получаем язык из контекста (тексты вопросов/ответов всегда на английском, интерфейс – в выбранном языке)
    lang = context.user_data.get("language", data.get("language", "en"))
    level = context.user_data.get("level", "easy")
    data["language"] = lang
    context.user_data["language"] = lang

    # Если администратор нажал кнопку "Управление", показываем инлайн-меню для теста
    if user_id == ADMIN_ID and msg in ["🛠️ Управление", "🛠️ Admin Control"]:
        inline_keyboard = InlineKeyboardMarkup([
             [InlineKeyboardButton("1", callback_data="admin_1"), InlineKeyboardButton("2", callback_data="admin_2")],
             [InlineKeyboardButton("3", callback_data="admin_3"), InlineKeyboardButton("4", callback_data="admin_4")],
             [InlineKeyboardButton("5", callback_data="admin_5")]
        ])
        prompt = "Выберите действие:" if lang == "ru" else "Choose an action:"
        await update.message.reply_text(prompt, reply_markup=inline_keyboard)
        return

    # Генерация меток для reply-кнопок (зависят от языка интерфейса)
    btn_next    = "✈️ Следующий вопрос" if lang == "ru" else "✈️ Next question"
    btn_answer  = "💬 Ответ" if lang == "ru" else "💬 Answer"
    btn_q_trans = "🌍 Перевод вопроса" if lang == "ru" else "🌍 Translate question"
    btn_a_trans = "🇷🇺 Перевод ответа" if lang == "ru" else "🇷🇺 Translate answer"
    btn_support = "💳 Поддержать проект" if lang == "ru" else "💳 Support project"

    logging.info(f"[USER {user_id}] Сообщение: {msg} | Язык: {lang} | Уровень: {level}")

    # --- Обработка кнопки "Поддержать проект" ---
    if msg == btn_support:
        support_text = (
            "💳 Вы можете поддержать проект здесь:\nhttps://www.sberbank.com/sms/pbpn?requisiteNumber=79155691550"
            if lang == "ru" else
            "💳 You can support the project here:\nhttps://www.sberbank.com/sms/pbpn?requisiteNumber=79155691550"
        )
        await update.message.reply_text(support_text)
        return

    # --- Обработка кнопки "Следующий вопрос" ---
    if msg == btn_next:
        available = [q for q in QUESTIONS if q["level"] == level and q["id"] not in data[f"{level}_done"]]
        if not available:
            if level == "easy":
                if lang == "ru":
                    button1 = "Перейти к сложным"
                    button2 = "Начать сначала"
                    prompt = "✅ Вы ответили на все простые вопросы. Что хотите сделать дальше?"
                else:
                    button1 = "Switch to hard"
                    button2 = "Start over"
                    prompt = "✅ All easy questions done. Choose next step:"
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(button1, callback_data="switch_to_hard"),
                     InlineKeyboardButton(button2, callback_data="reset_progress")]
                ])
                await update.message.reply_text(prompt, reply_markup=keyboard)
            else:
                if lang == "ru":
                    button = "Начать сначала"
                    prompt = "✅ Все вопросы завершены. Хотите начать сначала?"
                else:
                    button = "Start over"
                    prompt = "✅ All questions completed. Start over?"
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(button, callback_data="reset_progress")]
                ])
                await update.message.reply_text(prompt, reply_markup=keyboard)
            return

        question = random.choice(available)
        data[f"{level}_done"].append(question["id"])
        data["last_question"] = question

        # Сбрасываем все счётчики при выборе нового вопроса
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
            if data.get("answer_display_count") == 0:
                await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
                data["answer_display_count"] = -1
            return
        if data["answer_display_count"] <= 0:
            await update.message.reply_text(f"✅ {q['answer_en']}")
            voice = generate_voice(q['answer_en'])
            if voice:
                await update.message.reply_voice(voice)
            data["answer_display_count"] = 1
        elif data["answer_display_count"] == 1:
            await update.message.reply_text("❗ Ответ уже выведен" if lang == "ru" else "❗ Answer already displayed")
            data["answer_display_count"] = 2
        else:
            return
        return

    # --- Обработка кнопки "Перевод вопроса" ---
    if msg == btn_q_trans:
        q = data.get("last_question")
        if not q:
            if data.get("q_translate_count", 0) == 0:
                await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
                data["q_translate_count"] = -1
            return
        if data["q_translate_count"] == 0:
            await update.message.reply_text(f"🌍 {q['question_ru']}")
            data["q_translate_count"] = 1
        elif data["q_translate_count"] == 1:
            await update.message.reply_text("❗ Вопрос уже переведен" if lang == "ru" else "❗ Question already translated")
            data["q_translate_count"] = 2
        else:
            return
        return

    # --- Обработка кнопки "Перевод ответа" ---
    if msg == btn_a_trans:
        q = data.get("last_question")
        if not q:
            if data.get("a_translate_count", 0) == 0:
                await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
                data["a_translate_count"] = -1
            return
        if data.get("answer_display_count", 0) <= 0:
            if data.get("a_translate_count", 0) == 0:
                await update.message.reply_text("❗ Сначала получите основной ответ" if lang == "ru" else "❗ Please display the main answer first")
                data["a_translate_count"] = -1
            return
        if data["a_translate_count"] == 0:
            await update.message.reply_text(f"🇷🇺 {q['answer_ru']}")
            data["a_translate_count"] = 1
        elif data["a_translate_count"] == 1:
            await update.message.reply_text("❗ Ответ уже переведен" if lang == "ru" else "❗ Answer already translated")
            data["a_translate_count"] = 2
        else:
            return
        return

    await update.message.reply_text("❓ Используй кнопки меню." if lang == "ru" else "❓ Please use the menu buttons.")
