import streamlit as st
import requests
import time

BACKEND_URL = "http://127.0.0.1:8000"


if "history" not in st.session_state:
    st.session_state.history = []

if "selected_history" not in st.session_state:
    st.session_state.selected_history = None


#CSS 
st.markdown("""
<style>

    /* Botões */
    div.stButton > button:first-child {
        background-color: #1adddc;
        color: black;
        border-radius: 8px;
        height: 3em;
        width: 100%;
        font-weight: bold;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #00c2cc;
        color: black;
    }

    /* Caixas */
    .box {
        padding: 15px;
        border-radius: 10px;
        background-color: #1b1f27;
        border: 1px solid #2a2f3a;
        margin-bottom: 20px;
    }

    /* Título + logo */
    .title-container {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 20px;
    }
    .title-text {
        font-size: 32px;
        font-weight: 700;
        color: #1adddc;
    }
    .subtitle-text {
        font-size: 16px;
        color: #cccccc;
    }

</style>
""", unsafe_allow_html=True)



#HEADER 
st.image("assets/logo.png", width=200)

st.markdown("""
<div class="title-container">
    <div>
        <!-- <div class="title-text">IsItVuln</div> -->
        <div class="subtitle-text">Sistema baseado em RAG para deteção de vulnerabilidades de segurança em código simples</div>
    </div>
</div>
""", unsafe_allow_html=True)



# SIDEBAR ESQUERDA

st.sidebar.header("Gestão de documentos (RAG)")

uploaded_files = st.sidebar.file_uploader(
    "Adicionar PDFs (OWASP / CWE /...)",
    type=["pdf"],
    accept_multiple_files=True
)

if st.sidebar.button("Enviar documentos para o índice") and uploaded_files:
    files = [("files", (f.name, f.getvalue(), "application/pdf")) for f in uploaded_files]
    resp = requests.post(f"{BACKEND_URL}/upload_docs", files=files)
    st.sidebar.write(resp.json())

with st.sidebar.expander("🛈 Instruções", expanded=False):
    st.markdown("""
    **Guia de utilização do IsItVuln**

    **1 - Inserir documentos**
    - Adicione PDFs relacionados com vulnerabilidades (OWASP, CWE, etc.)
    - Estes documentos servem como base de conhecimento para o RAG.

    **2️ - Enviar documentos**
    - Clique em *"Enviar documentos para o índice"*.
    - Aguarde a reconstrução do índice local.

    **3️ - Inserir dados para análise**
    - Escreva o nome da vulnerabilidade que quer analisar.
    - Insira o código na caixa de texto.

    **4 - Analisar**
    - Clique em *"Analisar código"*.
    - Aguarde a resposta do modelo.

    **Nota:** Quanto mais específicos forem os PDFs, melhor a análise.
    """)

with st.sidebar.expander("🕮 Histórico de análises", expanded=False):
    if len(st.session_state.history) == 0:
        st.write("Sem análises anteriores.")
    else:
        for idx, item in enumerate(st.session_state.history):
            label = f"{item['timestamp']} — {item['vulnerability']}"
            if st.button(label, key=f"hist_{idx}"):
                st.session_state.selected_history = item





st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#1adddc;'>Análise de código</h3>", unsafe_allow_html=True)

vuln = st.text_input("Vulnerabilidade (ex: BOLA, Broken Authentication, XSS, Buffer Overflow)")
code = st.text_area("Código a analisar", height=300)

st.markdown('</div>', unsafe_allow_html=True)



if st.button("Analisar código"):
    if not vuln or not code:
        st.warning("Preenche vulnerabilidade e código.")
    else:

        start_time = time.time()

        payload = {
            "vulnerability": vuln,
            "code": f"<codigo>\n{code}\n</codigo>"
        }
        resp = requests.post(f"{BACKEND_URL}/analyze", json=payload)
        data = resp.json()

        end_time = time.time()
        response_time = round(end_time - start_time, 2)

        answer = data.get("answer", "Sem resposta.")

        recall_score = 0
        ans_lower = answer.lower()
        vuln_lower = vuln.lower()

        if vuln_lower in ans_lower:
            recall_score += 40
        if "mitig" in ans_lower or "recomenda" in ans_lower:
            recall_score += 30
        if "risco" in ans_lower or "impacto" in ans_lower:
            recall_score += 30

        recall_score = min(recall_score, 100)


        st.session_state.history.append({
            "timestamp": time.strftime("%H:%M:%S"),
            "vulnerability": vuln,
            "code": code,
            "response": answer,
            "response_time": response_time,
            "quality": recall_score,
        })

        st.markdown(f"""
        <div class="box">
            <h3 style='color:#1adddc;'>Resultado da análise 
            <span style="color:#888; font-size:14px;">
            (Tempo: {response_time}s ; Qualidade: {recall_score}%)
            </span></h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="box">
            <pre style="white-space: pre-wrap; color: #ffffff;">{data.get("answer", "Sem resposta.")}</pre>
        </div>
        """, unsafe_allow_html=True)

         #TEMPLATE DE EXPORTAR 
        report_md = f"""
# Relatório de Análise — IsItVuln

**Vulnerabilidade analisada:** {vuln}  
**Tempo de resposta:** {response_time}s  
**Qualidade (proxy):** {recall_score}%

---

## Código analisado

---

## Resultado da análise
{answer}

---

_Gerado automaticamente pelo sistema IsItVuln._
"""

        st.download_button(
            label="Exportar Análise",
            data=report_md,
            file_name=f"relatorio_{vuln.replace(' ', '_')}.md",
            mime="text/markdown"
        )


#HISTORICO 
if st.session_state.selected_history:
    item = st.session_state.selected_history

    st.markdown("""
    <div class="box">
        <h3 style='color:#1adddc;'>Análise anterior</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="box">
        <p><b>Vulnerabilidade:</b> {item['vulnerability']}</p>
        <p><b>Tempo:</b> {item['response_time']}s &nbsp;&nbsp; <b>Qualidade:</b> {item['quality']}%</p>
        <pre style="white-space: pre-wrap; color: #ffffff;">{item['response']}</pre>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Fechar análise anterior"):
        st.session_state.selected_history = None



st.markdown("""
<hr>
<center style="color:#666;">
© 2026 - Sistema baseado no modelo Llama-3.2-3B-Instruct. As respostas podem conter erros ou imprecisões, e devem ser verificadas.
""", unsafe_allow_html=True)
