from dataclasses import dataclass
from langchain_community.chat_message_histories import ChatMessageHistory

user_histories = {}
user_profiles = {}

@dataclass
class UserProfile:
    name: str = ""
    gender: str = ""
    age: int = None
    height: float = None
    weight: float = None
    activity_level: str = ""
    fitness_goals: str = ""

def initialize_user_history(user_id):
    if user_id not in user_histories:
        user_histories[user_id] = ChatMessageHistory()
    return user_histories[user_id]

def initialize_user_profile(user_id):
    if user_id not in user_profiles:
        user_profiles[user_id] = UserProfile()
    return user_profiles[user_id]

def get_user_profile(user_id):
    return user_profiles[user_id]

def get_user_history(user_id):
    return user_histories[user_id]

def update_user_profile(user_id, data: dict):
    profile = get_user_profile(user_id)
    for key, value in data.items():
        setattr(profile, key, value)
    user_profiles[user_id] = profile

def update_user_history(user_id, message):
    history = get_user_history(user_id)
    history.add_message(message)
    user_histories[user_id] = history

def clear_user_history(user_id):
    history = get_user_history(user_id)
    history.clear()
    user_histories[user_id] = history

def clear_user_profile(user_id):
    profile = UserProfile()
    user_profiles[user_id] = profile

def clear_user_data(user_id):
    clear_user_history(user_id)
    clear_user_profile(user_id)
