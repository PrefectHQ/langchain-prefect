"""Example of observing LLM calls made by a langchain agent."""

from langchain.agents import initialize_agent, load_tools
from langchain.llms import OpenAI
from prefect import flow

from prefect_langchain.plugins import RecordLLMCalls

llm = OpenAI(temperature=0)
tools = load_tools(["llm-math"])
agent = initialize_agent(tools, llm)


@flow
def my_flow():
    """Flow wrapping any LLM calls made by the agent."""
    agent.run(
        "How old is the current Dalai Lama? "
        "What is his age divided by 2 (rounded to the nearest integer)?"
    )


with RecordLLMCalls(tags={"agent"}):
    my_flow()
