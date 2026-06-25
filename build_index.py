import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma


DOCS_DIR = "docs"
DB_DIR = "index"

def main():
    print("=== BUILDING LOCAL RAG INDEX ===")

    docs = []
    for fname in os.listdir(DOCS_DIR):
        if fname.lower().endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DOCS_DIR, fname))
            docs.extend(loader.load())

    print(f"[OK] {len(docs)} páginas carregadas")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)
    print(f"[OK] {len(chunks)} chunks gerados")

    embeddings = HuggingFaceEmbeddings(
        model_name="./models/bge-small-en-v1.5"
    )

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )

    print("[DONE] Index criado com sucesso.")

if __name__ == "__main__":
    main()
