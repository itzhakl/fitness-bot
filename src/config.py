import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
def get_webhook_url():
    env = os.getenv("ENV")
    if env == "prod":
        return os.getenv("WEBHOOK_URL")
    else:
        return os.getenv("WEBHOOK_URL_DEV")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = get_webhook_url()
PORT = os.getenv("PORT") | 8443
AUTHORISATION_CODE = os.getenv("AUTHORISATION_CODE")