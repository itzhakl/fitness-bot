from langchain_anthropic import ChatAnthropic
from langchain_core.runnables import RunnableWithMessageHistory
from config import ANTHROPIC_API_KEY
from conversation.prompts import create_prompt
from conversation.user_management import user_histories
from dataclasses import dataclass, asdict

class AIManager:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            temperature=0,
            max_tokens=4096,
            timeout=None,
            max_retries=2,
            api_key=ANTHROPIC_API_KEY,
        )
        self.prompt = create_prompt()
        self.chain = self.prompt | self.llm

    def get_ai_response(self, user_input, user_id, user_profile):
        runnable_with_message_history = RunnableWithMessageHistory(
            self.chain,
            lambda session_id: user_histories[int(session_id)],
            input_messages_key="human_input",
            history_messages_key="history",
        )

        response = runnable_with_message_history.invoke(
            {"human_input": user_input, **asdict(user_profile)},
            config={"configurable": {"session_id": str(user_id)}},
        )

        return response.content

ai_manager = AIManager()