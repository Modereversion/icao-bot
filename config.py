import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
SUPPORT_LINK = os.getenv("SUPPORT_LINK", "")
EMAIL = os.getenv("EMAIL", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

QUESTIONS_FILE = "questions.json"
TIPS_FILE = "icao_tips.json"