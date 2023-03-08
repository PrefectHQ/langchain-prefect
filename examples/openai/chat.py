"""Example observing LLM calls made by `OpenAIChat` LLM."""

from langchain.llms import OpenAIChat

from langchain_prefect.plugins import RecordLLMCalls

messages = [
    {"role": "system", "content": "You should speak like a pirate."},
    {"role": "user", "content": "I don't care about frogs."},
]

chatbot = OpenAIChat(prefix_messages=messages, temperature=0.9)

with RecordLLMCalls():
    chatbot("what did I just say?")  # langchain assumes this is a user message
