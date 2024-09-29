from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction, ParseMode

from config import AUTHORISATION_CODE
from .speech_utils import handle_voice_message
from conversation.conversation_handler import handle_conversation
from logger import logger
from bot.authorization import add_authorized_user


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user_message: str) -> None:
    
    # שליחת פעולת "מקליד..."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    user_id = update.effective_user.id
    print(f"User {user_id} sent message: {user_message}")
    if context.user_data.get('waiting_for_code', True):
        code = update.message.text
        if code == AUTHORISATION_CODE:
            add_authorized_user(user_id)
            context.user_data['waiting_for_code'] = False
            await update.message.reply_text("קוד נכון! אתה מורשה להשתמש בבוט.")
        else:
            await update.message.reply_text("קוד שגוי ):")
    else:
        # העברת ההודעות האחרונות לתוך פונקציית הטיפול בשיחה
        response = handle_conversation(user_id, user_message)

        await update.message.reply_text(response)
        logger.info(f"sent {len(response)} charts length")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.voice:  # אם התקבלה הודעה קולית
        text: str = await handle_voice_message(update)
        await handle_text_message(update, context, text)
    elif update.message.text:  # אם התקבלה הודעת טקסט
        user_message = update.message.text
        await handle_text_message(update, context, user_message)
    else:
        await update.message.reply_text("אני מבין רק הודעות קוליות או טקסט בשלב זה")
