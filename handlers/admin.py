from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CommandHandler, filters
from config import ADMIN_ID
from handlers.questions import user_data

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get("language", "en")
    if str(user_id) != str(ADMIN_ID):
        return
    text = "🛠️ Админ-панель:" if lang == "ru" else "🛠️ Admin panel:"
    await update.message.reply_text(text + "\n📊 /stats — Статистика", reply_markup=None)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if str(user_id) != str(ADMIN_ID):
        return
    total_users = len(user_data)
    active_users = sum(1 for u in user_data.values() if u["easy_done"] or u["hard_done"])
    text = f"📈 Всего пользователей: {total_users}\n🟢 Активных пользователей: {active_users}"
    await update.message.reply_text(text)

def get_admin_handlers():
    return [
        MessageHandler(filters.Regex("🛠️ Управление|🛠️ Admin"), admin_command),
        CommandHandler("stats", stats_command),
    ]
