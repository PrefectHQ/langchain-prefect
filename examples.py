"""Examples of how to use the prefect plugin for langchain."""
from langchain import document_loaders
from langchain.agents import initialize_agent, load_tools
from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import OpenAI, OpenAIChat
from prefect import flow

from prefect_langchain.plugins import RecordLLMCalls

""" ---- OpenAI examples ---- """


def record_call_using_callable_llm():
    """Demonstrate LLM call wrapped when using a callable LLM."""
    with RecordLLMCalls():
        llm = OpenAI(temperature=0.9)
        llm("What would be a good name for a company that makes colorful socks?")


async def record_call_using_callable_llm_async():
    """Demonstrate LLM call wrapped when using a callable LLM."""
    with RecordLLMCalls():
        llm = OpenAI(temperature=0.9)
        await llm.agenerate(
            [
                "What would be a good name for a company that makes colorful socks?",
                "What would be a good name for a company that sells carbonated water?",
            ]
        )


def record_calls_using_agent():
    """Demonstrate LLM calls wrapped when using an agent."""
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


def record_call_using_openai_chat():
    """Demonstrate LLM call wrapped when using a chatbot."""
    with RecordLLMCalls():
        chatbot = OpenAIChat()
        chatbot("Who is Bill Gates?")


def record_call_using_qa_with_sources_chain_SOTU():
    """Demonstrate LLM call wrapped when using a QA with sources chain.

    Defaults to running local ChromaDB vectorstore for embeddings.
    """
    loader = document_loaders.DirectoryLoader("context")
    index = VectorstoreIndexCreator().from_loaders([loader])
    query = "What did the president say about Ketanji Brown Jackson?"

    with RecordLLMCalls(tags={index.vectorstore.__class__.__name__}):
        index.query_with_sources(query)


def record_call_using_qa_with_sources_chain_prefect_docs():
    """Demonstrate LLM call wrapped when using a QA with sources chain.

    Defaults to running local ChromaDB vectorstore for embeddings.
    """
    loader = document_loaders.WebBaseLoader("https://docs.prefect.io/")
    index = VectorstoreIndexCreator().from_loaders([loader])
    query = "What types of notifications are supported in Prefect 2?"

    with RecordLLMCalls(
        tags={index.vectorstore.__class__.__name__}, max_prompt_tokens=1000
    ):
        index.query_with_sources(query)


""" ---- Huggingface examples ---- """


def record_call_using_huggingfacehub():
    """Demonstrate LLM call wrapped when using callable HF LLM."""
    from langchain.llms import HuggingFaceHub

    hf = HuggingFaceHub(repo_id="gpt2")
    with RecordLLMCalls():
        hf("How are you today?")


if __name__ == "__main__":
    # import asyncio

    # asyncio.run(record_call_using_callable_llm_async())
    record_call_using_callable_llm()
    # record_calls_using_agent()
    # record_call_using_qa_with_sources_chain_SOTU()
    # record_call_using_qa_with_sources_chain_prefect_docs()
    # record_call_using_openai_chat()

    # record_call_using_huggingfacehub()
