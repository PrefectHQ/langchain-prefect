"""Example observing LLM calls made by `ConversationChain`."""
from langchain.chains import ConversationChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory

from prefect_langchain.plugins import RecordLLMCalls

conversation = ConversationChain(llm=OpenAI(), memory=ConversationBufferMemory())

with RecordLLMCalls():
    conversation.predict(input="What is the meaning of life?")
    conversation.predict(input="What did I just ask?")
