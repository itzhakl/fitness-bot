# from langchain_community.chat_models import ChatAnthropic
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from dataclasses import dataclass, asdict
from config import ANTHROPIC_API_KEY
from logger import logger
import json

# chat = ChatAnthropic(anthropic_api_key=ANTHROPIC_API_KEY, max_tokens_to_sample=1000)
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    temperature=0,
    max_tokens=1024,
    timeout=None,
    max_retries=2,
    api_key=ANTHROPIC_API_KEY,
)

user_histories = {}
user_profiles = {}

@dataclass
class UserProfile:
    user_name: str = ""
    gender: str = ""
    age: int = None
    height: float = None
    weight: float = None
    activity_level: str = ""
    fitness_goals: str = ""

template = """
אתה מאמן כושר וירטואלי בשם אלון. תפקידך לספק ייעוץ מדויק, מועיל ומותאם אישית. הקפד על הכללים הבאים:

- ענה תמיד בעברית בתשובות קצרות, ממוקדות ויעילות.
- התייחס להיסטוריית השיחה ולמידע שסופק בעבר.
- הצע עצות מעשיות וברורות ליישום מיידי, ועודד את המשתמש.
- שאל שאלות קצרות להשלמת מידע חסר.
- הימנע מעצות רפואיות מורכבות והמלץ לפנות לרופא במידת הצורך.
- פנה למשתמש בשמו הפרטי אם ידוע.
- ודא שיש לך את כל המידע הנדרש על המשתמש לפני מתן ייעוץ. אם יש מידע חסר, שאל שאלות ממוקדות כדי להשלים אותו לפני שתמשיך.

היסטוריית השיחה:
{history}

מידע על המשתמש:
שם: {user_name}
מגדר: {gender}
גיל: {age}
גובה: {height}
משקל: {weight}
רמת פעילות: {activity_level}
מטרות כושר: {fitness_goals}

לפני שתענה למשתמש, נתח את הטקסט שלו וחלץ מידע חדש. החזר את המידע המעודכן בפורמט JSON, מוקף בתגיות <USER_INFO> </USER_INFO>. אם אין מידע חדש, החזר JSON ריק. 

השאלה הבאה: {human_input}
"""


prompt = ChatPromptTemplate.from_template(template)

def extract_user_info(response):
    import re
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

def initialize_user_history(user_id):
    if user_id not in user_histories:
        user_histories[user_id] = ChatMessageHistory()

def initialize_user_profile(user_id):
    if user_id not in user_profiles:
        user_profiles[user_id] = UserProfile()
    return user_profiles[user_id]

def handle_conversation(user_id, user_message):
    initialize_user_history(user_id)
    user_profile = initialize_user_profile(user_id)
    
    chain = prompt | llm

    runnable_with_message_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: user_histories[int(session_id)],
        input_messages_key="human_input",
        history_messages_key="history",
    )
    
    try:
        response = runnable_with_message_history.invoke(
            {"human_input": user_message, **asdict(user_profile)},
            config={"configurable": {"session_id": str(user_id)}},
        )
        ai_message = response.content
        print("response: ", response)
        logger.info(f"אורך התשובה מ-Claude: {len(ai_message)} תווים")
        
        # חילוץ מידע המשתמש מהתשובה
        new_user_info, cleaned_response = extract_user_info(ai_message)

        # עדכון user_profile אם התקבל מידע חדש
        if new_user_info:
            for key, value in new_user_info.items():
                if value is not None and value != "":
                    setattr(user_profile, key, value)
        
        # עדכון היסטוריית השיחה
        user_histories[user_id].add_user_message(user_message)
        user_histories[user_id].add_ai_message(cleaned_response)
        
        return cleaned_response
    except Exception as e:
        logger.error(f"שגיאה בקבלת או שליחת תשובה: {str(e)}", exc_info=True)
        return "מצטער, נתקלתי בבעיה. אנא נסה שוב מאוחר יותר."