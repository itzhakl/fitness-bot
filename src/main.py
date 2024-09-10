from bot import setup_bot, run_webhook
from webhook import create_webhook_app
from logger import logger
from config import PORT

if __name__ == '__main__':
    bot = setup_bot()
    app = create_webhook_app(bot)
    run_webhook(bot)
    app.run(port=PORT)
    logger.info(f"Server is running on port {PORT}")
