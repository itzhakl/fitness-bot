import json
from langchain.memory import ChatMessageHistory
from langchain.schema import HumanMessage, AIMessage

# פונקציה לטעינת ההיסטוריה מקובץ JSON
def load_history_from_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {}

# פונקציה לשמירת ההיסטוריה לקובץ JSON
def save_history_to_json(file_path, chat_histories):
    with open(file_path, 'w') as file:
        json.dump(chat_histories, file, indent=4)

# קריאה של ההיסטוריה מתוך JSON
def get_history_from_file(user_id, file_path='chat_history.json'):
    chat_histories = load_history_from_json(file_path)
    return chat_histories.get(user_id, [])

# שמירת ההיסטוריה עבור משתמש מסוים
def save_history_to_file(user_id, messages, file_path='chat_history.json'):
    chat_histories = load_history_from_json(file_path)
    chat_histories[user_id] = messages
    save_history_to_json(file_path, chat_histories)

# פונקציה לעדכון ההיסטוריה ושמירתה בקובץ JSON
def add_message_to_file(user_id, message, role, file_path='chat_history.json'):
    chat_histories = load_history_from_json(file_path)
    
    # אם אין היסטוריה למשתמש, צור רשימה ריקה
    if user_id not in chat_histories:
        chat_histories[user_id] = []

    # הוספת הודעה בהתאם לתפקיד (משתמש או AI)
    if role == "user":
        chat_histories[user_id].append({"role": "user", "content": message})
    elif role == "assistant":
        chat_histories[user_id].append({"role": "assistant", "content": message})

    # הגבלת מספר ההודעות ל-10
    if len(chat_histories[user_id]) > 10:
        chat_histories[user_id] = chat_histories[user_id][-10:]

    # שמור את ההיסטוריה לקובץ
    save_history_to_json(file_path, chat_histories)
