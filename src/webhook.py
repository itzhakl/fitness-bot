from flask import Flask, request, abort
from telegram import Update
from config import TELEGRAM_BOT_TOKEN
import logging

def create_webhook_app(bot):
    app = Flask(__name__)

    @app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
    def webhook_handler():
        try:
            # Ensure that the request is JSON
            if not request.is_json:
                abort(400, description="Invalid data format")

            update = Update.de_json(request.get_json(force=True), bot.bot)

            # Asynchronously process the update
            bot.create_task(bot.process_update(update))
            
        except Exception as e:
            logging.error(f"Error handling webhook: {str(e)}", exc_info=True)
            abort(500, description="Internal Server Error")

        return 'OK', 200

    return app
