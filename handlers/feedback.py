from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID

# Глобальный список отзывов
feedback_list = []

async def handle_feedback_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("feedback_mode"):
        user = update.effective_user
        feedback_text = update.message.text

        feedback_message = (
            f"Новый отзыв от пользователя {user.full_name} (@{user.username}):\n\n"
            f"{feedback_text}"
        )
        # Сохраняем отзыв для админа
        feedback_list.append(feedback_message)
        # Отправляем отзыв администратору (лишь если личный чат существует у админа)
        await context.bot.send_message(chat_id=ADMIN_ID, text=feedback_message)
        context.user_data["feedback_mode"] = False

        lang = context.user_data.get("language", "en")
        thanks = "🙏 Спасибо за ваш отзыв!" if lang == "ru" else "🙏 Thank you for your feedback!"
        await update.message.reply_text(thanks)
    else:
        return
