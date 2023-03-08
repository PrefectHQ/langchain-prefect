"""Example observing LLM calls made by `HuggingFaceHub` LLM."""
from langchain.llms import HuggingFaceHub

from langchain_prefect.plugins import RecordLLMCalls

hf = HuggingFaceHub(repo_id="gpt2")

with RecordLLMCalls():
    hf("How are you today?")
