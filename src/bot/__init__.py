from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL
from bot.handlers import handle_message
from bot.commands import start, help, about, settings, profile
from bot.change_info import update_personal_info_handler

def setup_bot():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # הוספת מטפלים לפקודות
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(update_personal_info_handler)
    
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