import logging
import smtplib
from email.mime.text import MIMEText
from telegram import Update
from telegram.ext import ContextTypes
from config import EMAIL, EMAIL_PASSWORD

async def handle_feedback_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("feedback_mode"):
        user = update.effective_user
        feedback_text = update.message.text
        message = f"Новый отзыв от пользователя {user.full_name} (@{user.username}):\n\n{feedback_text}"
        subject = "Новый отзыв от пользователя"
        send_email(subject, message)
        # Сбрасываем режим отзывов после обработки
        context.user_data["feedback_mode"] = False
        lang = context.user_data.get("language", "en")
        thanks = "🙏 Спасибо за ваш отзыв!" if lang == "ru" else "🙏 Thank you for your feedback!"
        await update.message.reply_text(thanks)
    else:
        # Если feedback_mode не активен, этот обработчик не будет вызван из-за фильтра
        return

def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL
        msg["To"] = EMAIL
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            if EMAIL_PASSWORD:
                server.login(EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        logging.error(f"Ошибка при отправке email: {e}")
