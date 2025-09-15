from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document

embeddings = OpenAIEmbeddings()
VECTOR_DIR = "vector_memory"
vectorstore = Chroma(persist_directory=VECTOR_DIR, embedding_function=embeddings)

def add_to_memory(file_path, code):
    doc = Document(page_content=code, metadata={"file_path": file_path})
    vectorstore.add_documents([doc])
    vectorstore.persist()

def retrieve_memory(query, k=3):
    results = vectorstore.similarity_search(query, k=k)
    return "\n\n".join([f"# From {doc.metadata['file_path']}:\n{doc.page_content}" for doc in results])
