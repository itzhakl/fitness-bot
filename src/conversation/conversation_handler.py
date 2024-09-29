import json
import re
from logger import logger
from conversation.user_management import add_ai_and_user_messages, get_user_profile, initialize_user_history, initialize_user_profile, update_user_profile
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


def handle_conversation(user_id: int, user_message: str):
    initialize_user_history(user_id)
    initialize_user_profile(user_id)
    user_profile = get_user_profile(user_id)
    try:
        ai_message = ai_manager.get_ai_response(user_message, user_id, user_profile)
        
        logger.info(f"got response with: {len(ai_message)} charts length")
        
        new_user_info, cleaned_response = extract_user_info(ai_message)

        update_user_profile(user_id, new_user_info)

        add_ai_and_user_messages(user_id, user_message, ai_message)

        return cleaned_response
    except Exception as e:
        logger.error(f"An error occured while recived or response: {str(e)}", exc_info=True)
        return "מצטער, נתקלתי בבעיה. אנא נסה שוב מאוחר יותר."