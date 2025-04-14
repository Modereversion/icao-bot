import datetime
import os
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID

async def handle_feedback_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("feedback_mode"):
        user = update.effective_user
        feedback_text = update.message.text
        timestamp = datetime.datetime.now().isoformat()

        # Формируем текст отзыва
        feedback_message = (
            f"{timestamp} - Новый отзыв от {user.full_name} (@{user.username}):\n"
            f"{feedback_text}\n"
            "----------------------------------------"
        )

        # Сохраняем в файл
        save_feedback(feedback_message)

        # Отправляем администратору в личные сообщения
        await context.bot.send_message(chat_id=ADMIN_ID, text=feedback_message)

        # Завершаем режим сбора отзывов
        context.user_data["feedback_mode"] = False

        lang = context.user_data.get("language", "en")
        thanks = "🙏 Спасибо за ваш отзыв!" if lang == "ru" else "🙏 Thank you for your feedback!"
        await update.message.reply_text(thanks)

def save_feedback(feedback_message: str):
    try:
        file_path = os.path.join(os.getcwd(), "feedbacks.txt")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(feedback_message + "\n")
        print(f"Отзыв сохранён в {file_path}")
    except Exception as e:
        print(f"Ошибка при сохранении отзыва: {e}")
