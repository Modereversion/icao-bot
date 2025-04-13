import json
import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID

# Файл, в котором будут сохраняться отзывы
FEEDBACK_FILE = "feedbacks.json"

def load_feedbacks():
    """Загружает список отзывов из FEEDBACK_FILE. Если файл не существует или происходит ошибка, возвращает пустой список."""
    if not os.path.exists(FEEDBACK_FILE):
        return []
    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        logging.error(f"Ошибка чтения файла отзывов: {e}")
        return []

def save_feedbacks(feedbacks):
    """Сохраняет список отзывов в FEEDBACK_FILE."""
    try:
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Ошибка записи файла отзывов: {e}")

def clear_feedbacks():
    """Очищает файл отзывов, записывая в него пустой список."""
    save_feedbacks([])

async def handle_feedback_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("feedback_mode"):
        user = update.effective_user
        feedback_text = update.message.text

        feedback_message = (
            f"Новый отзыв от пользователя {user.full_name} (@{user.username}):\n\n"
            f"{feedback_text}"
        )

        # Отправляем отзыв администратору через Telegram (личное сообщение)
        await context.bot.send_message(chat_id=ADMIN_ID, text=feedback_message)

        # Сохраняем отзыв в файле
        feedbacks = load_feedbacks()
        feedbacks.append(feedback_message)
        save_feedbacks(feedbacks)

        context.user_data["feedback_mode"] = False

        lang = context.user_data.get("language", "en")
        thanks = "🙏 Спасибо за ваш отзыв!" if lang == "ru" else "🙏 Thank you for your feedback!"
        await update.message.reply_text(thanks)
    else:
        return
