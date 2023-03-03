"""Examples of how to use the prefect plugin for langchain."""

from langchain.document_loaders.directory import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import OpenAI

from prefect_langchain.plugins import record_llm_call  # noqa


def test_record_call_using_callable_llm():
    """Test LLM call wrapped when using a callable LLM."""
    llm = OpenAI(temperature=0.9)

    text = "What would be a good company name for a company that makes colorful socks?"
    llm(text)


def test_record_call_using_qa_with_sources_chain():
    """Test LLM call wrapped when using a QA with sources chain."""
    loader = DirectoryLoader("context")
    index = VectorstoreIndexCreator().from_loaders([loader])
    query = "What did the president say about Ketanji Brown Jackson"
    index.query_with_sources(query)


if __name__ == "__main__":
    test_record_call_using_callable_llm()
    # test_record_call_using_qa_with_sources_chain()
