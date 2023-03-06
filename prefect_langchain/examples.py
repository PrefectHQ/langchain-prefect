"""Examples of how to use the prefect plugin for langchain."""

from langchain.document_loaders.directory import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import OpenAI

from prefect_langchain.plugins import RecordLLMCalls


def record_call_using_callable_llm():
    """Test LLM call wrapped when using a callable LLM."""
    with RecordLLMCalls(tags={"testing"}):
        llm = OpenAI(temperature=0.9)
        text = (
            "What would be a good company name for a company that makes colorful socks?"
        )
        llm(text)


def record_call_using_qa_with_sources_chain():
    """Test LLM call wrapped when using a QA with sources chain.

    Defaults to running local ChromaDB vectorstore for embeddings.
    """
    loader = DirectoryLoader("context")
    index = VectorstoreIndexCreator().from_loaders([loader])
    query = "What did the president say about Ketanji Brown Jackson"

    with RecordLLMCalls():
        index.query_with_sources(query)


if __name__ == "__main__":
    record_call_using_callable_llm()
    # record_call_using_qa_with_sources_chain()
