import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from config import BOT_TOKEN
from handlers.commands import start_command, support_command
from handlers.feedback import handle_feedback_message
from handlers.questions import handle_user_message, handle_questions_callback
from handlers.settings import get_settings_handlers

logging.basicConfig(level=logging.INFO)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("support", support_command))

for handler in get_settings_handlers():
    app.add_handler(handler)

# Регистрируем inline-колбэки для switch_to_hard и reset_progress
app.add_handler(CallbackQueryHandler(handle_questions_callback, pattern="^(switch_to_hard|reset_progress)$"))

async def message_dispatcher(update, context):
    if context.user_data.get("feedback_mode"):
        await handle_feedback_message(update, context)
    else:
        await handle_user_message(update, context)

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_dispatcher))

app.run_polling()
