import os
import speech_recognition as sr
from telegram import Update
from pydub import AudioSegment
from logger import logger

async def handle_voice_message(update: Update) -> str:
    # הורדת קובץ ההודעה הקולית
    voice_file = await update.message.voice.get_file()

    # שמירת הקובץ באופן זמני בפורמט OGG
    ogg_path = "voice_message.ogg"
    await voice_file.download_to_drive(ogg_path)

    # המרת הקובץ מ-OGG ל-WAV באמצעות pydub
    wav_path = "voice_message.wav"
    try:
        # שימוש ב-pydub להמרת OGG ל-WAV
        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(wav_path, format="wav")

        # המרת ההודעה הקולית לטקסט באמצעות זיהוי דיבור
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            try:
                # שימוש ב- Google Speech Recognition API
                text = recognizer.recognize_google(audio_data, language="he-IL")
                logger.info(f"Voice message converted to text: {text}")
                return text
            except sr.UnknownValueError:
                return "לא הצלחתי להבין את ההודעה הקולית שלך."
            except sr.RequestError as e:
                logger.error(f"Error during speech recognition: {e}")
                return "אירעה שגיאה בעת עיבוד ההודעה הקולית שלך."

    except Exception as e:
        logger.error(f"Error during audio conversion: {e}")
        return "אירעה שגיאה בהמרת קובץ הקול."

    finally:
        # מחיקת קבצים זמניים
        if os.path.exists(ogg_path):
            os.remove(ogg_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)
