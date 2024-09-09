from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from .speech_utils import handle_voice_message
from conversation.conversation_handler import handle_conversation
from logger import logger

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user_message: str) -> None:
    user_id = update.effective_user.id
    
    # שליחת פעולת "מקליד..."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    # העברת ההודעות האחרונות לתוך פונקציית הטיפול בשיחה
    response = handle_conversation(user_id, user_message)
    
    # שליחת התשובה בחלקים אם היא ארוכה מדי
    for i in range(0, len(response), 4000):
        chunk = response[i:i+4000]
        await update.message.reply_text(chunk)
        logger.info(f"נשלח חלק באורך {len(chunk)} תווים")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.voice:  # אם התקבלה הודעה קולית
        text = await handle_voice_message(update)
        await handle_text_message(update, context, text)
    elif update.message.text:  # אם התקבלה הודעת טקסט
        user_message = update.message.text
        await handle_text_message(update, context, user_message)
