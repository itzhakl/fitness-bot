import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain.chat_models import ChatAnthropic
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts.prompt import PromptTemplate
import re

# טעינת משתני הסביבה
load_dotenv()

# הגדרת לוגים
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# הגדרת Anthropic API
chat = ChatAnthropic(anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"), max_tokens_to_sample=1000)

# client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# מילון לשמירת זיכרון השיחה עבור כל משתמש
user_memories = {}

# תבנית לשיחה
template = """אתה מאמן כושר וירטואלי מקצועי שעוזר למשתמשים להשיג את מטרות הכושר והבריאות שלהם. תפקידך לספק ייעוץ מדויק, מועיל ומותאם אישית. הקפד על הכללים הבאים:

1. ענה תמיד בעברית.
2. השתדל לתת תשובות קצרות עד בינוניות, ממוקדות ויעילות.
3. התייחס להיסטוריית השיחה ולמידע קודם שסופק על ידי המשתמש.
4. הצע עצות מעשיות וברורות שניתנות ליישום מיידי.
5. עודד את המשתמש ותן לו חיזוקים חיוביים.
6. אם חסר לך מידע חיוני, שאל שאלות קצרות וממוקדות כדי להשלים אותו.
7. הימנע מלתת עצות רפואיות מורכבות. במקרים של בעיות בריאות מורכבות, המלץ להתייעץ עם רופא.

היסטוריית השיחה:
{history}


אדם: {input}
מאמן: """

prompt = PromptTemplate(input_variables=["history", "input"], template=template)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    if user_id not in user_memories:
        user_memories[user_id] = ConversationBufferMemory(human_prefix="אדם", ai_prefix="מאמן")
    await update.message.reply_html(
        f"שלום {user.mention_html()}! אני הבוט המאמן האישי שלך. איך אוכל לעזור לך היום?"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("אני יכול לעזור לך בנושאי כושר ותזונה. פשוט שאל אותי כל שאלה!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user_id = update.effective_user.id
    
    if user_id not in user_memories:
        user_memories[user_id] = ConversationBufferMemory(human_prefix="אדם", ai_prefix="מאמן")
    
    conversation = ConversationChain(
        llm=chat,
        memory=user_memories[user_id],
        prompt=prompt,
        verbose=True
    )
    
    try:
        response = conversation.predict(input=user_message)
        logger.info(f"אורך התשובה מ-Claude: {len(response)} תווים")
        
        # שליחת התשובה בחלקים
        for i in range(0, len(response), 4000):
            chunk = response[i:i+4000]
            await update.message.reply_text(chunk)
            logger.info(f"נשלח חלק באורך {len(chunk)} תווים")
        
    except Exception as e:
        logger.error(f"שגיאה בקבלת או שליחת תשובה: {str(e)}", exc_info=True)
        await update.message.reply_text("מצטער, נתקלתי בבעיה. אנא נסה שוב מאוחר יותר.")

def main() -> None:
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
