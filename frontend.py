import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("📄 Ask My Docs")

if "doc_id" not in st.session_state:
    st.session_state.doc_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.session_state.messages:
    if st.button("Clear Chat"):
        requests.delete(f"{API_URL}/ask/history/user")  
        st.session_state.messages = []                  
        st.rerun()                                       


# Upload file
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    if st.button("Ingest PDF"):
        with st.spinner("Reading PDF..."):
            res = requests.post(
                f"{API_URL}/ingest",
                files={"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            )
            if res.status_code == 200:
                st.session_state.doc_id = res.json()["doc_id"]
                st.success("PDF ready! Now ask a question below.")
            else:
                st.error("Something went wrong.")
        
# Ask a question
if "doc_id" in st.session_state:
    question = st.chat_input("Ask a question...")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # show chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        # Get answer
        with st.chat_message("assistant"):
            answer = ""
            box = st.empty()
            with requests.post(
                f"{API_URL}/stream/",
                json={"query": question, "session_id": "user", "doc_id": st.session_state.doc_id},
                stream=True
            ) as res:
                for chunk in res.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        answer += chunk
                        box.markdown(answer + "|")
            box.markdown(answer)
        st.session_state.messages.append({"role": "assitant", "content": answer})
