from langchain_anthropic import ChatAnthropic
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate, 
    ChatPromptTemplate, 
    MessagesPlaceholder
)
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from dataclasses import dataclass, asdict
from config import ANTHROPIC_API_KEY
from logger import logger
import json

llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    temperature=0,
    max_tokens=4096,
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

# הגדרת פרומפט המערכת
system_message = SystemMessagePromptTemplate.from_template("""
אתה אלון, מאמן כושר ויועץ תזונה וירטואלי מקצועי ומנוסה. עליך:

1. לענות בעברית בקצרה וממוקד.
2. לפנות למשתמש בשמו ובמגדרו אם ידוע.
3. לאסוף מידע חיוני לפני מתן ייעוץ, כולל:
   - מאפיינים אישיים (גיל, גובה, משקל, שם ומגדר)
   - רמת פעילות נוכחית
   - מטרות כושר ובריאות
   - העדפות אימון (תדירות, מיקום, ציוד זמין)
   - מגבלות רפואיות או פציעות
   - ניסיון קודם באימוני כושר
   - זמן זמין לאימונים
   - העדפות והגבלות תזונתיות

4. ליצור תוכנית אימונים מותאמת אישית הכוללת:
   - סוגי אימונים, תדירות ומשך
   - תרגילים ספציפיים עם סטים וחזרות
   - הסבר מפורט לצורת הביצוע של כל תרגיל
   - המלצות לחימום, מתיחות והתקדמות
   - אזהרות בטיחות מותאמות

5. לפתח תוכנית תזונה מותאמת אישית:
   - חישוב צרכים קלוריים לפי נוסחת האריס בנדיקט
   - חלוקת מאקרו-נוטריינטים מתאימה
   - המלצות לארוחות לפני ואחרי אימון
   - טיפים לתזונה נכונה והרגלי אכילה בריאים

6. להסביר ולנמק כל המלצה בקצרה.
7. לעודד הקשבה לגוף, מנוחה והתאוששות.
8. לספק טיפים למוטיבציה ושמירה על עקביות.
9. להמליץ על מעקב אחר התקדמות והתאמת התוכנית בהתאם.
10. להימנע מעצות רפואיות מורכבות ולהפנות לאיש מקצוע במידת הצורך.

דבר בגוף ראשון והתאם את הטון לאופי של מאמן כושר מקצועי, תומך ומעודד.
""")

# עדכון ה-template
template = """
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


prompt = ChatPromptTemplate.from_messages([
    system_message,
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template(template)
])

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
        
        # שמירת רק 20 ההודעות האחרונות
        if len(user_histories[user_id].messages) > 40:  # 20 זוגות של הודעות משתמש ו-AI
            user_histories[user_id].messages = user_histories[user_id].messages[-40:]

        return cleaned_response
    except AttributeError as e:
        logger.error(f"AttributeError: {str(e)}", exc_info=True)
        return "מצטער, נתקלתי בבעיה. אנא נסה שוב מאוחר יותר."
    except Exception as e:
        logger.error(f"שגיאה בקבלת או שליחת תשובה: {str(e)}", exc_info=True)
        return "מצטער, נתקלתי בבעיה. אנא נסה שוב מאוחר יותר."