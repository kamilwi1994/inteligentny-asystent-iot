
import streamlit as st
import silnik_rag

st.set_page_config(page_title="Inteligentny Asystent Domowy", layout="wide")

st.title("💡 Inteligentny Asystent Domowy")
st.write("Zadaj pytanie dotyczące zużycia energii, temperatury lub poproś o porady optymalizacyjne.")

@st.cache_resource
def load_rag_chain():
    chain = silnik_rag.get_rag_chain()
    if chain is None:
        st.error("Wystąpił krytyczny błąd podczas inicjalizacji systemu RAG. Sprawdź terminal.")
    return chain

rag_chain = load_rag_chain()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Jak mogę Ci pomóc?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if rag_chain:
            with st.spinner("Analizuję dane i generuję odpowiedź..."):
                try:

                    answer = rag_chain.invoke(prompt)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Wystąpił błąd: {e}")
        else:
            st.warning("System RAG nie jest dostępny. Nie mogę odpowiedzieć na pytanie.")