import os
import uuid
import logging
from gtts import gTTS

def generate_voice(text, lang='en'):
    try:
        os.makedirs("data/tts", exist_ok=True)
        unique_id = uuid.uuid4().hex
        file_path = os.path.join("data/tts", f"voice_{unique_id}.mp3")
        tts = gTTS(text=text, lang=lang)
        tts.save(file_path)
        return open(file_path, "rb")
    except Exception as e:
        logging.error(f"TTS error: {e}")
        return None
