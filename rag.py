from langchain_community.llms import LlamaCpp
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.callbacks import BaseCallbackHandler

MODEL_PATH = "models/Llama-3.2-3B-Instruct-Q4_K_S.gguf"
DB_DIR = "index"


class StreamCallback(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs):
        print(token, end="", flush=True)

def main():
    print("=== LOCAL RAG (Llama-3.2-3B) ===")

    llm = LlamaCpp(
        model_path=MODEL_PATH,
        n_ctx=1536,         
        temperature=0.1,
        verbose=False,
        streaming=True,
        n_threads=4,         
        callbacks=[StreamCallback()]
    )

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embeddings
    )

    retriever = db.as_retriever(search_kwargs={"k": 1})

    template = """
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
{codigo}
</codigo>

Pergunta:
{question}

Resposta:
"""
    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

    print("Sistema pronto. Escreve a tua pergunta.")

    while True:
        q = input("\nPergunta: ")
        if q.lower() in ["sair", "exit", "quit"]:
            break

        print("\nResposta:\n")

        docs = retriever.invoke(q)

        context = "\n\n".join([d.page_content for d in docs])

        final_prompt = prompt.format(
        context=context,
        question=q,
        codigo=q  
        )


        for _ in llm.stream(final_prompt):
            pass

        print("\n")

if __name__ == "__main__":
    main()
