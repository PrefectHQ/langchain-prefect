"""Example of observing LLM calls made by via callable OpenAI LLM."""

from langchain.llms import OpenAI

from langchain_prefect.plugins import RecordLLMCalls

llm = OpenAI(temperature=0.9)

with RecordLLMCalls():
    llm("What would be a good name for a company that makes colorful socks?")
