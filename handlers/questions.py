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
    logging.error(f"Ошибка загрузки вопросов: {e}")
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
            "last_display": "question",  # question / answer / q_trans / a_trans
            "shown_ids": set()
        }
    return user_data[user_id]

# 👋 Приветствие
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang_code = update.effective_user.language_code or "en"
    lang = "ru" if lang_code.startswith("ru") else "en"
    context.user_data["language"] = lang

    data = get_user_data(user_id)
    data["language"] = lang
    data["done_ids"] = []
    data["postponed"] = []
    data["last_question"] = None
    data["last_msg_id"] = None
    data["last_display"] = "question"

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

# 🔄 Выбор нового вопроса
async def send_new_question(update, context, user_id, lang):
    data = get_user_data(user_id)
    level = data.get("level", "easy")
    available = [q for q in QUESTIONS if q["level"] == level and q["id"] not in data["done_ids"]]

    if not available and data["postponed"]:
        available = data["postponed"]
        data["postponed"] = []

    if not available:
        await update.callback_query.message.reply_text("✅ Все вопросы пройдены!" if lang == "ru" else "✅ All questions completed!")
        return

    question = random.choice(available)
    data["last_question"] = question
    data["last_display"] = "question"

    # Если он из postponed — не учитывать в статистике
    if question not in data["postponed"]:
        data["done_ids"].append(question["id"])

    text = f"📝 {question['question_en']}"
    voice = generate_voice(question["question_en"])
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✈️ Следующий вопрос" if lang == "ru" else "✈️ Next", callback_data="next_question"),
            InlineKeyboardButton("💬 Ответ" if lang == "ru" else "💬 Answer", callback_data="show_answer")
        ],
        [
            InlineKeyboardButton("🌍 Перевод вопроса" if lang == "ru" else "🌍 Translate Q", callback_data="translate_q"),
            InlineKeyboardButton("🇷🇺 Перевод ответа" if lang == "ru" else "🇷🇺 Translate A", callback_data="translate_a")
        ],
        [
            InlineKeyboardButton("🔁 Ответить позже" if lang == "ru" else "🔁 Answer later", callback_data="postpone")
        ]
    ])

    sent = await update.callback_query.message.reply_text(text, reply_markup=keyboard)
    if voice:
        await update.callback_query.message.reply_voice(voice)

    data["last_msg_id"] = sent.message_id

# 🔘 Обработка всех inline-кнопок
async def handle_inline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = context.user_data.get("language", "en")
    data = get_user_data(user_id)
    await query.answer()

    code = query.data
    q = data.get("last_question")
    current_display = data.get("last_display")
    msg = query.message

    if code == "start_training" or code == "next_question":
        await send_new_question(update, context, user_id, lang)
        return

    if not q:
        await msg.reply_text("❗ Сначала получите вопрос." if lang == "ru" else "❗ Please start with a question.")
        return

    if code == "show_answer":
        if current_display == "answer":
            return
        text = f"💬 {q['answer_en']}"
        voice = generate_voice(q["answer_en"])
        await msg.edit_text(text, reply_markup=msg.reply_markup)
        if voice:
            await msg.reply_voice(voice)
        data["last_display"] = "answer"

    elif code == "translate_q":
        if current_display == "q_trans":
            return
        text = f"🌍 {q['question_ru']}"
        voice = generate_voice(q["question_en"])
        await msg.edit_text(text, reply_markup=msg.reply_markup)
        if voice:
            await msg.reply_voice(voice)
        data["last_display"] = "q_trans"

    elif code == "translate_a":
        if current_display == "a_trans":
            return
        if current_display != "answer":
            await msg.reply_text("❗ Сначала покажите ответ." if lang == "ru" else "❗ Please view the answer first.")
            return
        text = f"🇷🇺 {q['answer_ru']}"
        voice = generate_voice(q["answer_en"])
        await msg.edit_text(text, reply_markup=msg.reply_markup)
        if voice:
            await msg.reply_voice(voice)
        data["last_display"] = "a_trans"

    elif code == "postpone":
        if q not in data["postponed"]:
            data["postponed"].append(q)
        await msg.reply_text("📌 Вопрос отложен. Переходим к следующему!" if lang == "ru" else "📌 Question saved for later. Moving on!")
        await send_new_question(update, context, user_id, lang)
