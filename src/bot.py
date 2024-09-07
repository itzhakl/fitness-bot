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
    
    # שליחת פעולת "מקליד..."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # העברת ההודעות האחרונות לתוך פונקציית הטיפול בשיחה
    response = handle_conversation(user_id, user_message)
    
    # Send the response in chunks
    for i in range(0, len(response), 4000):
        chunk = response[i:i+4000]
        await update.message.reply_text(chunk)
        logger.info(f"נשלח חלק באורך {len(chunk)} תווים")

def setup_bot() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
