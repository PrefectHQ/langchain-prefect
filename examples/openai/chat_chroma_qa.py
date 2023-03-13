from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ChatVectorDBChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain_prefect.loaders import GitHubLoader
from langchain_prefect.plugins import RecordLLMCalls

documents = GitHubLoader("PrefectHQ/prefect", glob="**/*.md").load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents, embeddings)

system_template = """Use the following pieces of context to answer the users question. 
If you don't know the answer, just say that you don't know, don't make up an answer.
----------------
{context}"""
messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}"),
]
prompt = ChatPromptTemplate.from_messages(messages)

qa = ChatVectorDBChain.from_llm(
    ChatOpenAI(temperature=0), vectorstore, qa_prompt=prompt
)

with RecordLLMCalls(
    tags={qa.vectorstore.__class__.__name__}, max_prompt_tokens=int(1e4)
):
    chat_history = []
    query = "What infrastructures does Prefect support?"
    result = qa({"question": query, "chat_history": chat_history})

    print(result["answer"])

    chat_history = [(query, result["answer"])]
    query = "Can I use Prefect with AWS?"
    result = qa({"question": query, "chat_history": chat_history})

    print(result["answer"])
