"""Example observing LLM calls made by `OpenAI.agenerate`."""
import asyncio

from langchain.llms import OpenAI

from langchain_prefect.plugins import RecordLLMCalls

llm = OpenAI(temperature=0.9)


async def record_call_using_LLM_agenerate():
    """async func"""
    await llm.agenerate(
        [
            "What would be a good name for a company that makes colorful socks?",
            "What would be a good name for a company that sells carbonated water?",
        ]
    )


with RecordLLMCalls():
    asyncio.run(record_call_using_LLM_agenerate())
