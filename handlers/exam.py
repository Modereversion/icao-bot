import random
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from handlers.questions import get_user_data
from utils.tts import generate_voice

async def start_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get("language", "en")
    data = get_user_data(user_id)

    level = context.user_data.get("level", "easy")
    available = [q for q in context.bot_data["questions"] if q["level"] == level]
    if len(available) < 5:
        await update.callback_query.message.reply_text("❗ Недостаточно вопросов для экзамена." if lang == "ru"
                                                       else "❗ Not enough questions for the exam.")
        return

    await update.callback_query.message.reply_text("🎓 Экзамен начался! Ты услышишь 5 вопросов. На каждый — 29 секунд." if lang == "ru"
                                                   else "🎓 Exam started! You will hear 5 questions. You have 29 seconds for each.")

    exam_questions = random.sample(available, 5)
    for idx, question in enumerate(exam_questions, 1):
        await update.callback_query.message.reply_text(f"📝 Вопрос {idx}: {question['question_en']}" if lang == "ru"
                                                       else f"📝 Question {idx}: {question['question_en']}")
        voice = generate_voice(question["question_en"])
        if voice:
            await update.callback_query.message.reply_voice(voice)
        await asyncio.sleep(29)

    data["exams_passed"] = data.get("exams_passed", 0) + 1
    await update.callback_query.message.reply_text("✅ Экзамен завершён! Молодец!" if lang == "ru"
                                                   else "✅ Exam completed! Well done!")
