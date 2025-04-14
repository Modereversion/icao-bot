import json
import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import QUESTIONS_FILE
from utils.tts import generate_voice

# Загрузка вопросов
with open(QUESTIONS_FILE, encoding="utf-8") as f:
    QUESTIONS = json.load(f)

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
            "last_voice_id": None,
            "last_display": "question"
        }
    return user_data[user_id]

# Приветствие
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang_code = update.effective_user.language_code or "en"
    lang = "ru" if lang_code.startswith("ru") else "en"
    context.user_data["language"] = lang
    data = get_user_data(user_id)

    # Очистка и сброс
    data.update({
        "done_ids": [],
        "postponed": [],
        "last_question": None,
        "last_msg_id": None,
        "last_voice_id": None,
        "last_display": "question"
    })

    text = (
        "👋 Привет! Добро пожаловать в Level 4 Trainer – твой тренажёр к экзамену ИКАО!\n\n"
        "Нажми «🚀 Начать тренировку», чтобы приступить к первому вопросу."
        if lang == "ru" else
        "👋 Welcome to Level 4 Trainer – your ICAO speaking exam trainer!\n\n"
        "Press «🚀 Start training» to begin."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Начать тренировку" if lang == "ru" else "🚀 Start training", callback_data="start_training")]
    ])

    await update.message.reply_text(text, reply_markup=keyboard)

# Новый вопрос
async def send_new_question(update, context, user_id, lang):
    data = get_user_data(user_id)

    # Удаление старой озвучки и кнопок
    try:
        if data.get("last_voice_id"):
            await context.bot.delete_message(chat_id=user_id, message_id=data["last_voice_id"])
        if data.get("last_msg_id"):
            await context.bot.edit_message_reply_markup(chat_id=user_id, message_id=data["last_msg_id"], reply_markup=None)
    except:
        pass

    level = data.get("level", "easy")
    available = [q for q in QUESTIONS if q["level"] == level and q["id"] not in data["done_ids"]]

    if not available and data["postponed"]:
        available = data["postponed"]
        data["postponed"] = []

    if not available:
        await update.callback_query.message.reply_text("✅ Все вопросы завершены!" if lang == "ru" else "✅ All questions completed!")
        return

    question = random.choice(available)
    if question not in data["postponed"]:
        data["done_ids"].append(question["id"])

    data["last_question"] = question
    data["last_display"] = "question"

    text = f"📝 {question['question_en']}"
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
    voice = generate_voice(question["question_en"])
    if voice:
        voice_msg = await update.callback_query.message.reply_voice(voice)
        data["last_voice_id"] = voice_msg.message_id
    data["last_msg_id"] = sent.message_id

# Inline-кнопки
async def handle_inline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = context.user_data.get("language", "en")
    data = get_user_data(user_id)
    await query.answer()

    code = query.data
    q = data.get("last_question")
    msg = query.message

    # Начать тренировку / Следующий вопрос
    if code == "start_training" or code == "next_question":
        await send_new_question(update, context, user_id, lang)
        return

    if not q:
        await msg.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
        return

    # Удаляем старое голосовое
    try:
        if data.get("last_voice_id"):
            await context.bot.delete_message(chat_id=user_id, message_id=data["last_voice_id"])
    except:
        pass

    if code == "show_answer":
        if data["last_display"] == "answer":
            return
        text = f"💬 {q['answer_en']}"
        voice = generate_voice(q['answer_en'])
        await msg.edit_text(text, reply_markup=msg.reply_markup)
        if voice:
            voice_msg = await msg.reply_voice(voice)
            data["last_voice_id"] = voice_msg.message_id
        data["last_display"] = "answer"

    elif code == "translate_q":
        if data["last_display"] == "q_trans":
            return
        text = f"🌍 {q['question_ru']}"
        voice = generate_voice(q["question_en"])
        await msg.edit_text(text, reply_markup=msg.reply_markup)
        if voice:
            voice_msg = await msg.reply_voice(voice)
            data["last_voice_id"] = voice_msg.message_id
        data["last_display"] = "q_trans"

    elif code == "translate_a":
        if data["last_display"] == "a_trans":
            return
        if data["last_display"] != "answer":
            await msg.reply_text("❗ Сначала посмотрите ответ." if lang == "ru" else "❗ Please view the answer first.")
            return
        text = f"🇷🇺 {q['answer_ru']}"
        voice = generate_voice(q["answer_en"])
        await msg.edit_text(text, reply_markup=msg.reply_markup)
        if voice:
            voice_msg = await msg.reply_voice(voice)
            data["last_voice_id"] = voice_msg.message_id
        data["last_display"] = "a_trans"

    elif code == "postpone":
        if q not in data["postponed"]:
            data["postponed"].append(q)
        await msg.reply_text("📌 Вопрос отложен. Переходим к следующему!" if lang == "ru" else "📌 Question saved for later. Moving on!")
        await send_new_question(update, context, user_id, lang)
