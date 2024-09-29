from dataclasses import dataclass
from langchain_community.chat_message_histories import ChatMessageHistory


user_histories = {}
user_profiles = {}


@dataclass
class UserProfile:
    name: str = None
    gender: str = None
    age: int = None
    height: float = None
    weight: float = None
    activity_level: str = None
    fitness_goals: str = None
    workouts_per_week: int = None


def initialize_user_history(user_id):
    if user_id not in user_histories:
        user_histories[user_id] = ChatMessageHistory()


def get_user_history(user_id: int):
    return user_histories.get(int(user_id))


def add_ai_and_user_messages(user_id, user_message, ai_message):
    history = get_user_history(user_id)
    history.add_user_message(user_message)
    history.add_ai_message(ai_message)
    if len(history.messages) > 20:
        history.messages = history.messages[-20:]
    user_histories[user_id] = history


def initialize_user_profile(user_id) -> UserProfile:
    if user_id not in user_profiles:
        user_profiles[user_id] = UserProfile()


def get_user_profile(user_id: int) -> UserProfile:
    return user_profiles[user_id]


def update_user_profile(user_id, data):
    if data is None:
        return
    profile = get_user_profile(user_id)
    for key, value in data.items():
        setattr(profile, key, value)
    user_profiles[user_id] = profile


def clear_user_history(user_id: int):
    history = get_user_history(user_id)
    history.clear()
    user_histories[user_id] = history


def clear_user_profile(user_id):
    profile = UserProfile()
    user_profiles[user_id] = profile


def clear_user_data(user_id):
    clear_user_history(user_id)
    clear_user_profile(user_id)
