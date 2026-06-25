from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import re
import os

from langchain_community.llms import LlamaCpp
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from fastapi import UploadFile, File
from typing import List
import subprocess

MODEL_PATH = "models/Llama-3.2-3B-Instruct-Q4_K_S.gguf"
DB_DIR = "index"

app = FastAPI()

llm = LlamaCpp(
    model_path=MODEL_PATH,
    n_ctx=4096,
    temperature=0.1,
    n_threads=4,
    verbose=False
)

embeddings = HuggingFaceEmbeddings(
    model_name="./models/bge-small-en-v1.5"
)

db = Chroma(
    persist_directory=DB_DIR,
    embedding_function=embeddings
)
retriever = db.as_retriever(search_kwargs={"k": 2})


class AnalyzeRequest(BaseModel):
    vulnerability: str
    code: str


def extract_code(text):
    match = re.search(r"<codigo>(.*?)</codigo>", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()



@app.post("/upload_docs")
def upload_docs(files: List[UploadFile] = File(...)):
    os.makedirs("docs", exist_ok=True)

    for f in files:
        path = os.path.join("docs", f.filename)
        with open(path, "wb") as out:
            out.write(f.file.read())

    subprocess.run(["python3", "build_index.py"])

    global db, retriever
    db = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embeddings
    )
    retriever = db.as_retriever(search_kwargs={"k": 2})

    return {"status": "index_rebuilt", "docs": len(files)}


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    code = extract_code(req.code)
    docs = retriever.invoke(req.vulnerability)
    context = "\n\n".join(d.page_content for d in docs)

    prompt = f"""
És um analista de segurança.  
Usa APENAS o conhecimento dos documentos fornecidos pelo RAG para identificar vulnerabilidades.

O utilizador vai fornecer um bloco de código.  
O teu trabalho é:

1. Identificar se o código contém a vulnerabilidade pedida.
2. Explicar onde está a vulnerabilidade (linha, função, endpoint).
3. Explicar porque é vulnerável.
4. Explicar como mitigar.

IMPORTANTE:
- O código fornecido pelo utilizador está ENTRE as tags <codigo> e </codigo>.
- Ignora qualquer texto fora dessas tags.
- Se não conseguires identificar a linha, descreve a parte do código onde está a vulnerabilidade.
- Nunca peças o código outra vez.
- Nunca peças mais contexto.
- Nunca respondas com instruções genéricas.

Contexto dos documentos:
{context}

Código fornecido pelo utilizador:
<codigo>
{code}
</codigo>

Resposta:
"""

    resposta = llm.invoke(prompt)
    return {"answer": resposta}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
