import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from conversation import handle_conversation, initialize_user_history
from config import TELEGRAM_BOT_TOKEN
from logger import logger

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    initialize_user_history(user.id)
    await update.message.reply_html(
        f"שלום {user.mention_html()}! אני אלון, מאמן הכושר הווירטואלי שלך. כאן כדי לעזור לך להגיע ליעדים שלך. אשמח לדעת קצת יותר עליך כדי להתאים לך תכנית אישית. שנתחיל?"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("אני יכול לעזור לך בנושאי כושר ותזונה. פשוט שאל אותי כל שאלה!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user_id = update.effective_user.id
    
    # קבלת 10 ההודעות האחרונות מהצ'אט
    # last_10_messages = await get_last_10_messages(update, context)
    
    # העברת ההודעות האחרונות לתוך פונקציית הטיפול בשיחה
    response = handle_conversation(user_id, user_message)
    
    # Send the response in chunks
    for i in range(0, len(response), 4000):
        chunk = response[i:i+4000]
        await update.message.reply_text(chunk)
        logger.info(f"נשלח חלק באורך {len(chunk)} תווים")

# async def get_last_10_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> list:
#     chat_id = update.message.chat_id

#     # רשימת ההודעות האחרונות
#     last_10_messages = []

#     # קבלת עד 10 ההודעות האחרונות מתוך הצ'אט
#     async for message in context.bot.get_chat(chat_id).iter_history(limit=10):
#         if message.text:  # רק אם מדובר בהודעה טקסטואלית
#             last_10_messages.append(message.text)

#     return last_10_messages


def setup_bot() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
