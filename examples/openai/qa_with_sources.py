"""Example observing LLM calls made by querying `VectorstoreIndexWrapper`."""
from langchain import document_loaders
from langchain.indexes import VectorstoreIndexCreator

from prefect_langchain.plugins import RecordLLMCalls

loader = document_loaders.TextLoader("context/state_of_the_union.txt")
index = VectorstoreIndexCreator().from_loaders([loader])
query = "What did the president say about Ketanji Brown Jackson?"

with RecordLLMCalls(tags={index.vectorstore.__class__.__name__}):
    # defaults to OpenAI llm if not specified
    index.query_with_sources(query)
