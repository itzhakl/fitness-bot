import os
import logging
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain.chat_models import ChatAnthropic
from langchain.schema import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
import re

# טעינת משתני הסביבה
load_dotenv()

# הגדרת לוגים
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# הגדרת Anthropic API
chat = ChatAnthropic(anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"), max_tokens_to_sample=500)

# מילון לשמירת היסטוריית השיחה ומידע המשתמש עבור כל משתמש
user_histories = {}
user_data = {}

# תבנית לשיחה
template = """אתה מאמן כושר וירטואלי מקצועי בשם אלון שעוזר למשתמשים להשיג את מטרות הכושר והבריאות שלהם. תפקידך לספק ייעוץ מדויק, מועיל ומותאם אישית. הקפד על הכללים הבאים:

1. ענה תמיד בעברית.
2. השתדל לתת תשובות קצרות עד בינוניות, ממוקדות ויעילות.
3. התייחס להיסטוריית השיחה ולמידע קודם שסופק על ידי המשתמש.
4. הצע עצות מעשיות וברורות שניתנות ליישום מיידי.
5. עודד את המשתמש ותן לו חיזוקים חיוביים.
6. אם חסר לך מידע חיוני, שאל שאלות קצרות וממוקדות כדי להשלים אותו.
7. הימנע מלתת עצות רפואיות מורכבות. במקרים של בעיות בריאות מורכבות, המלץ להתייעץ עם רופא.
8. פנה למשתמש בשמו הפרטי אם ידוע.

מידע על המשתמש:
שם: {user_name}
מגדר: {gender}
גיל: {age}
גובה: {height}
משקל: {weight}
רמת פעילות: {activity_level}
מטרות כושר: {fitness_goals}

לפני שתענה למשתמש, נתח את הטקסט שלו וחלץ כל מידע חדש או מעודכן על המשתמש. החזר את המידע המעודכן בפורמט JSON בתחילת תשובתך, מוקף בתגיות <USER_INFO> </USER_INFO>. אם לא התקבל מידע חדש, החזר JSON ריק. לדוגמה:

<USER_INFO>
{{
    "user_name": "דני",
    "gender": "זכר",
    "age": 30,
    "height": 175,
    "weight": 70,
    "activity_level": "בינונית",
    "fitness_goals": "לבנות שריר"
}}
</USER_INFO>

לאחר מכן, המשך עם תשובתך הרגילה למשתמש.

אדם: {human_input}
אלון: """

prompt = ChatPromptTemplate.from_template(template)

def extract_user_info(response):
    match = re.search(r'<USER_INFO>(.*?)</USER_INFO>', response, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            user_info = json.loads(json_str)
            # הסר את ה-JSON מהתשובה
            response = re.sub(r'<USER_INFO>.*?</USER_INFO>', '', response, flags=re.DOTALL).strip()
            return user_info, response
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from AI response")
    return None, response

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    if user_id not in user_histories:
        user_histories[user_id] = ChatMessageHistory()
    if user_id not in user_data:
        user_data[user_id] = {"user_name": "", "gender": "", "age": None, "height": None, "weight": None, "activity_level": "", "fitness_goals": ""}
    await update.message.reply_html(
        f"שלום {user.mention_html()}! אני אלון, המאמן האישי שלך. איך אוכל לעזור לך היום?"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("אני יכול לעזור לך בנושאי כושר ותזונה. פשוט שאל אותי כל שאלה!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user_id = update.effective_user.id
    
    # Initialize user history and data if not already present
    if user_id not in user_histories:
        user_histories[user_id] = ChatMessageHistory()
    if user_id not in user_data:
        user_data[user_id] = {"user_name": "", "gender": "", "age": None, "height": None, "weight": None, "activity_level": "", "fitness_goals": ""}
    
    chain = prompt | chat

    runnable_with_message_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: user_histories[int(session_id)],
        input_messages_key="human_input",
        history_messages_key="history",
    )
    
    try:
        response = await runnable_with_message_history.ainvoke(
            {"human_input": user_message, **user_data[user_id]},
            config={"configurable": {"session_id": str(user_id)}},
        )
        ai_message = response.content
        logger.info(f"אורך התשובה מ-Claude: {len(ai_message)} תווים")
        
        # חילוץ מידע המשתמש מהתשובה
        new_user_info, cleaned_response = extract_user_info(ai_message)

        # עדכון user_data אם התקבל מידע חדש
        if new_user_info:
            for key, value in new_user_info.items():
                if value is not None and value != "":
                    user_data[user_id][key] = value
        
        # שליחת התשובה בחלקים
        for i in range(0, len(cleaned_response), 4000):
            chunk = cleaned_response[i:i+4000]
            await update.message.reply_text(chunk)
            logger.info(f"נשלח חלק באורך {len(chunk)} תווים")
        
        # עדכון היסטוריית השיחה
        user_histories[user_id].add_user_message(user_message)
        user_histories[user_id].add_ai_message(cleaned_response)
        
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