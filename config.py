import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

QUESTIONS_FILE = "questions.json"
TIPS_FILE = "icao_tips.json"
