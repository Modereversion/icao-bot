import json
import random
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import QUESTIONS_FILE, ADMIN_ID
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
            "answers_viewed": 0,
            "q_translations": 0,
            "a_translations": 0,
            "last_question_msg_id": None
        }
    return user_data[user_id]

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text.strip()
    data = get_user_data(user_id)

    lang = context.user_data.get("language", data.get("language", "en"))
    level = context.user_data.get("level", "easy")
    data["language"] = lang
    context.user_data["language"] = lang

    btn_next    = "✈️ Следующий вопрос" if lang == "ru" else "✈️ Next question"
    btn_answer  = "💬 Ответ" if lang == "ru" else "💬 Answer"
    btn_q_trans = "🌍 Перевод вопроса" if lang == "ru" else "🌍 Translate question"
    btn_a_trans = "🇷🇺 Перевод ответа" if lang == "ru" else "🇷🇺 Translate answer"
    btn_support = "💳 Поддержать проект" if lang == "ru" else "💳 Support project"

    if user_id == ADMIN_ID and msg in ["🛠️ Управление", "🛠️ Admin Control"]:
        inline_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("1", callback_data="admin_1"), InlineKeyboardButton("2", callback_data="admin_2")],
            [InlineKeyboardButton("3", callback_data="admin_3"), InlineKeyboardButton("4", callback_data="admin_4")],
            [InlineKeyboardButton("5", callback_data="admin_5")]
        ])
        prompt = "Выберите действие:" if lang == "ru" else "Choose an action:"
        await update.message.reply_text(prompt, reply_markup=inline_keyboard)
        return

    if msg == btn_support:
        from handlers.commands import support_command
        await support_command(update, context)
        return

    if msg == btn_next:
        available = [q for q in QUESTIONS if q["level"] == level and q["id"] not in data[f"{level}_done"]]
        if not available:
            if level == "easy":
                button1 = "Перейти к сложным" if lang == "ru" else "Switch to hard"
                button2 = "Начать сначала" if lang == "ru" else "Start over"
                prompt = "✅ Вы ответили на все простые вопросы. Что хотите сделать дальше?" if lang == "ru" else "✅ All easy questions done. Choose next step:"
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(button1, callback_data="switch_to_hard"),
                     InlineKeyboardButton(button2, callback_data="reset_progress")]
                ])
            else:
                button = "Начать сначала" if lang == "ru" else "Start over"
                prompt = "✅ Все вопросы завершены. Хотите начать сначала?" if lang == "ru" else "✅ All questions completed. Start over?"
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(button, callback_data="reset_progress")]])
            await update.message.reply_text(prompt, reply_markup=keyboard)
            return

        question = random.choice(available)
        data[f"{level}_done"].append(question["id"])
        data["last_question"] = question
        data["answer_display_count"] = 0
        data["q_translate_count"] = 0
        data["a_translate_count"] = 0

        sent_msg = await update.message.reply_text(f"📝 {question['question_en']}")
        data["last_question_msg_id"] = sent_msg.message_id

        voice = generate_voice(question['question_en'])
        if voice:
            await update.message.reply_voice(voice)
        return

    if msg == btn_answer:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
            return

        if data["answer_display_count"] == 0:
            if data.get("last_question_msg_id") and update.message.message_id - data["last_question_msg_id"] > 1:
                await update.message.reply_text(f"🔁 {q['question_en']}")
                voice = generate_voice(q["question_en"])
                if voice:
                    await update.message.reply_voice(voice)

            await update.message.reply_text(f"✅ {q['answer_en']}")
            voice = generate_voice(q['answer_en'])
            if voice:
                await update.message.reply_voice(voice)
            data["answer_display_count"] = 1
            data["answers_viewed"] += 1
        else:
            await update.message.reply_text("❗ Ответ уже получен." if lang == "ru" else "❗ Answer already shown.")
        return

    if msg == btn_q_trans:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
            return

        if data["q_translate_count"] == 0:
            if data.get("last_question_msg_id") and update.message.message_id - data["last_question_msg_id"] > 1:
                await update.message.reply_text(f"🔁 {q['question_en']}")
                voice = generate_voice(q["question_en"])
                if voice:
                    await update.message.reply_voice(voice)

            await update.message.reply_text(f"🌍 {q['question_ru']}")
            data["q_translate_count"] = 1
            data["q_translations"] += 1
        else:
            await update.message.reply_text("❗ Вопрос уже переведён." if lang == "ru" else "❗ Question already translated.")
        return

    if msg == btn_a_trans:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text("❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first.")
            return

        if data["answer_display_count"] == 0:
            await update.message.reply_text("❗ Сначала посмотрите ответ." if lang == "ru" else "❗ Please view the answer first.")
            return

        if data["a_translate_count"] == 0:
            if data.get("last_question_msg_id") and update.message.message_id - data["last_question_msg_id"] > 1:
                await update.message.reply_text(f"🔁 {q['question_en']}")
                voice = generate_voice(q["question_en"])
                if voice:
                    await update.message.reply_voice(voice)

            await update.message.reply_text(f"🇷🇺 {q['answer_ru']}")
            data["a_translate_count"] = 1
            data["a_translations"] += 1
        else:
            await update.message.reply_text("❗ Ответ уже переведён." if lang == "ru" else "❗ Answer already translated.")
        return

    await update.message.reply_text("❓ Используй кнопки меню." if lang == "ru" else "❓ Please use the menu buttons.")
