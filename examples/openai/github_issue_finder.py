"""Ingesting GitHub issues and finding similar ones using OpenAI."""
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms.openai import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_prefect.loaders import GithubIssueLoader
from langchain_prefect.plugins import RecordLLMCalls

loader = GithubIssueLoader("prefecthq/prefect", n_issues=20)

chain = load_qa_with_sources_chain(OpenAI(temperature=0))

splitter = CharacterTextSplitter(separator=" ", chunk_size=1024, chunk_overlap=0)

source_chunks = [
    Document(
        page_content=chunk,
        metadata=source.metadata,
    )
    for source in loader.load()
    for chunk in splitter.split_text(source.page_content)
]

index = Chroma.from_documents(
    documents=source_chunks,
    embedding=OpenAIEmbeddings(),
)


def answer(question: str, k: int = 5):
    """Answer a question using the index."""
    return chain(
        {
            "input_documents": index.similarity_search(question, k=k),
            "question": question,
        },
        return_only_outputs=True,
    )["output_text"]


with RecordLLMCalls(tags={index.__class__.__name__}):
    print(answer("Are there open issues related to large mapped tasks?"))
