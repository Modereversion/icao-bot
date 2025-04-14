import datetime
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID

async def handle_feedback_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("feedback_mode"):
        user = update.effective_user
        feedback_text = update.message.text

        # Формируем сообщение с временной меткой и информацией о пользователе
        feedback_message = (
            f"{datetime.datetime.now().isoformat()} - Новый отзыв от {user.full_name} (@{user.username}):\n"
            f"{feedback_text}\n"
            "----------------------------------------"
        )
        
        # Сохраняем отзыв в файл, чтобы не терять данные при перезапуске бота
        save_feedback(feedback_message)
        
        # Отправляем отзыв администратору через личные сообщения (chat_id = ADMIN_ID)
        await context.bot.send_message(chat_id=ADMIN_ID, text=feedback_message)

        # Выключаем режим отзыва
        context.user_data["feedback_mode"] = False

        lang = context.user_data.get("language", "en")
        thanks = "🙏 Спасибо за ваш отзыв!" if lang == "ru" else "🙏 Thank you for your feedback!"
        await update.message.reply_text(thanks)
    else:
        return

def save_feedback(feedback_message: str):
    try:
        with open("feedbacks.txt", "a", encoding="utf-8") as f:
            f.write(feedback_message + "\n")
    except Exception as e:
        print(f"Ошибка при сохранении отзыва: {e}")
