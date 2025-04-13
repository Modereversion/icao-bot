from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID

async def handle_feedback_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("feedback_mode"):
        user = update.effective_user
        feedback_text = update.message.text

        # Формируем сообщение для администратора
        feedback_message = (
            f"Новый отзыв от пользователя {user.full_name} (@{user.username}):\n\n"
            f"{feedback_text}"
        )
        
        # Отправляем отзыв администратору через личные сообщения (chat_id = ADMIN_ID)
        await context.bot.send_message(chat_id=ADMIN_ID, text=feedback_message)

        context.user_data["feedback_mode"] = False

        lang = context.user_data.get("language", "en")
        thanks = "🙏 Спасибо за ваш отзыв!" if lang == "ru" else "🙏 Thank you for your feedback!"
        await update.message.reply_text(thanks)
    else:
        return
