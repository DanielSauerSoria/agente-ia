import streamlit as st

from src.loader import load_documents
from src.rag import RAGAgent

st.set_page_config(
    page_title="Santos Pegasus AI",
    page_icon="🤖",
    layout="wide"
)

if "historial" not in st.session_state:
    st.session_state.historial = []

with st.sidebar:

    st.title("🤖 Santos Pegasus AI")

    st.markdown("---")

    st.write(
        """
        Este agente responde preguntas sobre la documentación interna
        de Santos Pegasus Soluciones.
        """
    )

    st.markdown("### Documentos disponibles")

    st.write("📄 Manual de Onboarding")
    st.write("📄 Guía Backend")
    st.write("📄 Guía Frontend")
    st.write("📄 Arquitectura")
    st.write("📄 Protocolo de Incidentes")

    st.markdown("---")

    st.markdown("### Ejemplos")

    st.write("- ¿Cómo es el onboarding?")
    st.write("- ¿Qué tecnologías usa Backend?")
    st.write("- ¿Qué hacer durante un incidente?")

st.title("🤖 Santos Pegasus AI")

st.write(
    "Asistente inteligente para consultar la documentación interna "
    "de Santos Pegasus Soluciones."
)

@st.cache_resource
def cargar_agente():

    documents = load_documents()

    agent = RAGAgent()

    agent.build_vectorstore(documents)

    agent.load_llm()

    return agent

agent = cargar_agente()

question = st.text_input(
    "Escribe tu pregunta"
)

if st.button("Consultar"):

    with st.spinner("Consultando documentos..."):

        resultado = agent.ask(question)

    st.session_state.historial.append(resultado)

    st.subheader("Respuesta")

    st.success(resultado["respuesta"])

    with st.expander("📚 Ver fuentes"):

        for fuente in resultado["fuentes"]:

            st.write(
                f"{fuente['archivo']} - Página {fuente['pagina']}"
            )

        for fuente in resultado["fuentes"]:

            st.write(
                f"📄 {fuente['archivo']} "
                f"(Página {fuente['pagina']})"
            )


if st.button("🗑 Limpiar conversación"):
    st.session_state.historial = []
    st.rerun()

if st.session_state.historial:

    st.markdown("---")
    st.subheader("Historial")

    for item in reversed(st.session_state.historial):

        st.write(item["respuesta"])