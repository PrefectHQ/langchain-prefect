"""Example observing LLM calls made by `OpenAIChat` LLM."""

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from langchain_prefect.plugins import RecordLLMCalls

messages = [
    SystemMessage(content="You should speak like a pirate."),
    HumanMessage(content="I don't care about frogs."),
    HumanMessage(content="What did I just say?"),
]

chatbot = ChatOpenAI()

with RecordLLMCalls():
    print(chatbot(messages))
