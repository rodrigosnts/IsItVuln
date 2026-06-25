<p>
  <img src="assets/logo.png" alt="IsItVuln Logo" width="220">
</p>

# IsItVuln - Sistema RAG Offline para Análise de Vulnerabilidades em Código

O **IsItVuln** é um sistema local baseado em *Retrieval-Augmented Generation (RAG)* capaz de analisar código e identificar vulnerabilidades com base em documentação técnica fornecida pelo utilizador (ex.: OWASP, CWE, RFCs, etc.).  
Todo o processamento é **100% local e offline**, incluindo embeddings e inferência do modelo LLM.

---

## 🚀 Funcionalidades Principais

-  **Análise de vulnerabilidades em código**
-  **Carregamento de PDFs** (OWASP, CWE, etc.) para alimentar o RAG
-  **Embeddings locais** com BGE-small-en-v1.5
-  **Inferência local** com LlamaCpp (modelo GGUF)
-  **Índice vetorial persistente** com ChromaDB
-  **Medição de tempo de resposta**
-  **Heurística de qualidade (recall proxy)**
-  **Histórico de análises**
-  **Possibilidade de Exportar relatórios em Markdown**
-  **Funciona totalmente offline**

---

## 🧱 Arquitetura do Sistema

```
Streamlit (Frontend)
        ↓ HTTP
FastAPI (Backend)
        ↓
RAG Pipeline
    ├── ChromaDB (vetor store)
    ├── BGE-small-en-v1.5 (embeddings)
    └── LlamaCpp (LLM local)
```

---

## 📦 Requisitos

- Python 3.10+
- pip / venv
- Modelos locais (os seguintes ou outros):
  - `Llama-3.2-3B-Instruct-Q4_K_S.gguf`
  - `bge-small-en-v1.5` (pasta completa descarregada via `hf download`)
- Dependências Python (instaladas mais abaixo)

---

## 🔧 Instalação

### 1. Criar ambiente virtual
```bash
python3 -m venv rag_env
source rag_env/bin/activate
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Colocar os modelos na pasta `models/`
Estrutura recomendada:

```
models/
    Llama-3.2-3B-Instruct-Q4_K_S.gguf
    bge-small-en-v1.5/
        config.json
        model.safetensors
        tokenizer.json
        ...
```

### 4. Criar as pastas necessárias
```bash
mkdir docs
mkdir index
```

---

## 🏗️ Construir o Índice RAG

Sempre que forem adicionados novos PDFs:

```bash
python3 build_index.py
```

Isto irá:

- carregar PDFs da pasta `docs/`
- dividir em chunks
- gerar embeddings
- guardar tudo na pasta `index/`

---

## ▶️ Executar o Backend

```bash
python3 backend.py
```

O servidor arranca em:

```
http://127.0.0.1:8000
```

---

## 🖥️ Executar o Frontend

Noutro terminal:

```bash
streamlit run app.py
```

A interface abre em:

```
http://localhost:8501
```

---

## 🧪 Como Usar

1. Carregar PDFs na sidebar (OWASP, CWE, etc.)
2. Clicar **Enviar documentos para o índice**
3. Escrever o nome da vulnerabilidade (ex.: *XSS*, *SQL Injection*, *BOLA*)
4. Inserir o código a analisar
5. Clicar em **Analisar código**
6. Consultar:
   - resposta do modelo
   - tempo de execução
   - qualidade (proxy)
   - histórico
7. Exportar o relatório em Markdown se necessário

---

## 📁 Estrutura do Projeto

```
Projeto/
│── app.py               # Interface Streamlit
│── backend.py           # API FastAPI + pipeline RAG
│── build_index.py       # Construção do índice vetorial
│── models/              # Modelos locais (LLM + embeddings)
│── docs/                # PDFs carregados pelo utilizador
│── index/               # Índice ChromaDB persistente
│── assets/              # Logo e imagens
│── requirements.txt
```

---

## 🛡️ Notas de Segurança

- Todo o processamento é **local**  
- Nenhum dado é enviado para a cloud  
- Ideal para análise de código sensível

---

