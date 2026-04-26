import streamlit as st
import json
import os
import base64
from ai_utils import analyze_with_llm, create_pdf_report

st.set_page_config(page_title="AI SecOps Platform", layout="wide", page_icon="🛡️")

# Custom CSS for better aesthetics
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    .chat-message {
        padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex;
    }
    .chat-message.user {
        background-color: #e9ecef;
    }
    .chat-message.bot {
        background-color: #ffffff; border: 1px solid #dee2e6;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ AI DevSecOps Platform")
st.markdown("### Advanced Security Intelligence with RAG & ChromaDB")

# Tabs
tab1, tab2, tab3 = st.tabs(["SAST Analyzer", "DAST Analyzer", "Pentest Assistant (Chatbot)"])

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

with tab1:
    st.header("🔍 SAST Analysis")
    st.write("Upload SonarQube JSON for AI-driven remediation paths.")
    sast_file = st.file_uploader("Upload SAST Report", type="json", key="sast")
    if sast_file:
        st.success("Report uploaded.")
        if st.button("Generate AI Security PDF"):
            st.info("Triggering AI analysis with RAG context...")
            # In a real app, we'd run the full analysis here
            st.warning("Note: Use `python ai_sast.py` for the full automated pipeline analysis.")

with tab2:
    st.header("⚡ DAST Analysis")
    st.write("Upload OWASP ZAP JSON for automated exploit simulations.")
    dast_file = st.file_uploader("Upload DAST Report", type="json", key="dast")
    if dast_file:
        st.success("Report uploaded.")
        if st.button("Generate AI Pentest PDF"):
            st.info("Triggering AI analysis with RAG context...")
            st.warning("Note: Use `python ai_dast.py` for the full automated pipeline analysis.")

with tab3:
    st.header("🤖 Pentest Assistant")
    st.info("I am powered by **Groq LLaMA 3.3** and a **Security RAG** system indexing OWASP and NIST standards.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat history display
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Sidebar controls
    with st.sidebar:
        st.header("Controls")
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        if st.session_state.messages:
            if st.button("Export Chat to PDF"):
                # Prepare data for PDF
                chat_data = []
                for m in st.session_state.messages:
                    role = "USER" if m["role"] == "user" else "AI ASSISTANT"
                    chat_data.append(f"[{role}]:\n{m['content']}\n")
                
                pdf_path = "chatbot_conversation.pdf"
                create_pdf_report("AI Pentest Assistant Conversation", chat_data, pdf_path)
                st.success("PDF Generated!")
                st.markdown(get_binary_file_downloader_html(pdf_path, 'Chat History PDF'), unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("How do I fix a Blind SQL Injection in Node.js?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing with RAG knowledge..."):
                # system_prompt for chatbot
                sys_prompt = "You are an expert penetration tester and secure coding assistant. Use the provided context to give the best security advice."
                response = analyze_with_llm(sys_prompt, prompt, use_rag=True)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
