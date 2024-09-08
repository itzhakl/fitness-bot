from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL
from bot.handlers import start_command, help_command, handle_message

def setup_bot():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # הוספת מטפלים לפקודות
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # הוספת מטפל להודעות טקסט וקול
    application.add_handler(MessageHandler(filters.TEXT | filters.VOICE, handle_message))

    return application

def run_webhook(application):
    application.run_webhook(
        listen='0.0.0.0',
        port=8443,
        url_path=TELEGRAM_BOT_TOKEN,
        webhook_url=f'{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}'
    )