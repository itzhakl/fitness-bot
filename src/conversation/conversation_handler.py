import json
import re
from logger import logger
from conversation.user_management import initialize_user_history, initialize_user_profile, user_histories, user_profiles
from conversation.ai_manager import ai_manager

def extract_user_info(response):
    match = re.search(r'<USER_INFO>(.*?)</USER_INFO>', response, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            user_info = json.loads(json_str)
            response = re.sub(r'<USER_INFO>.*?</USER_INFO>', '', response, flags=re.DOTALL).strip()
            return user_info, response
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from AI response")
    return None, response

def handle_conversation(user_id, user_message):
    user_profile = initialize_user_profile(user_id)
    user_history = initialize_user_history(user_id)
    
    try:
        ai_message = ai_manager.get_ai_response(user_message, user_id, user_profile)
        
        logger.info(f"אורך התשובה מ-Claude: {len(ai_message)} תווים")
        
        new_user_info, cleaned_response = extract_user_info(ai_message)

        if new_user_info:
            for key, value in new_user_info.items():
                print(f"new user info: {key} = {value}")
                if value is not None and value != "":
                    setattr(user_profiles[user_id], key, value)
        
        user_histories[user_id].add_user_message(user_message)
        user_histories[user_id].add_ai_message(cleaned_response)
        
        if len(user_histories[user_id].messages) > 30:
            user_histories[user_id].messages = user_histories[user_id].messages[-30:]

        return cleaned_response
    except Exception as e:
        logger.error(f"שגיאה בקבלת או שליחת תשובה: {str(e)}", exc_info=True)
        return "מצטער, נתקלתי בבעיה. אנא נסה שוב מאוחר יותר."