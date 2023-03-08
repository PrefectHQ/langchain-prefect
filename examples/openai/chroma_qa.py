"""Example observing LLM calls made by `VectorDBQA` stuff chain."""
from langchain import document_loaders
from langchain.chains import VectorDBQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

from langchain_prefect.plugins import RecordLLMCalls

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = document_loaders.WebBaseLoader("https://docs.prefect.io/").load()
texts = text_splitter.split_documents(documents)
embeddings = OpenAIEmbeddings()

db = Chroma.from_documents(texts, embeddings)
qa = VectorDBQA.from_chain_type(llm=OpenAI(), chain_type="stuff", vectorstore=db)

question = "What types of notifications are supported in Prefect 2?"

with RecordLLMCalls(tags={qa.vectorstore.__class__.__name__}, max_prompt_tokens=1e4):
    qa(question)
