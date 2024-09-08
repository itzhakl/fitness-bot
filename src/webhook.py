from flask import Flask, request
from telegram import Update
from config import TELEGRAM_BOT_TOKEN

def create_webhook_app(bot):
    app = Flask(__name__)

    @app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
    def webhook_handler():
        update = Update.de_json(request.get_json(force=True), bot.bot)
        bot.create_task(bot.process_update(update))
        return 'OK'

    return app