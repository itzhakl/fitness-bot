from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableWithMessageHistory
from config import OPENAI_API_KEY
from conversation.prompts import create_prompt
from conversation.user_management import get_user_history
from dataclasses import asdict

class AIManager:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",  # or another appropriate OpenAI model
            temperature=1,
            max_tokens=2048,
            timeout=None,
            max_retries=2,
            api_key=OPENAI_API_KEY,
        )
        self.prompt = create_prompt()
        self.chain = self.prompt | self.llm

    def get_ai_response(self, user_input, user_id, user_profile):
        runnable_with_message_history = RunnableWithMessageHistory(
            self.chain,
            get_session_history=get_user_history,
            input_messages_key="human_input",
            history_messages_key="history",
        )

        response = runnable_with_message_history.invoke(
            {"human_input": user_input, **asdict(user_profile)},
            config={"configurable": {"session_id": str(user_id)}},
        )

        return response.content

ai_manager = AIManager()