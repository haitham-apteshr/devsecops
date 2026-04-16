import streamlit as st
import json
import os
from ai_utils import analyze_with_llm

st.set_page_config(page_title="AI SecOps Platform", layout="wide")

st.title("🛡️ AI DevSecOps Platform")

# Tabs
tab1, tab2, tab3 = st.tabs(["SAST Analyzer", "DAST Analyzer", "Pentest Assistant (Chatbot)"])

with tab1:
    st.header("Static Application Security Testing (SAST)")
    st.write("Upload your SonarQube or SAST tool JSON report to get interactive AI analysis.")
    sast_file = st.file_uploader("Upload SAST Report (JSON)", type="json", key="sast")
    if sast_file is not None:
        try:
            data = json.load(sast_file)
            st.success("JSON loaded successfully.")
            if st.button("Run Standalone ai_sast.py Integration"):
                st.info("In a real scenario, this would trigger the standalone script `python ai_sast.py`. Try answering using the CLI for the PDF generation.")
        except Exception as e:
            st.error(f"Error parsing JSON: {e}")

with tab2:
    st.header("Dynamic Application Security Testing (DAST)")
    st.write("Upload your OWASP ZAP or DAST tool JSON report to get interactive AI analysis.")
    dast_file = st.file_uploader("Upload DAST Report (JSON)", type="json", key="dast")
    if dast_file is not None:
        try:
            data = json.load(dast_file)
            st.success("JSON loaded successfully.")
            if st.button("Run Standalone ai_dast.py Integration"):
                st.info("In a real scenario, this would trigger the standalone script `python ai_dast.py`. Try answering using the CLI for the PDF generation.")
        except Exception as e:
            st.error(f"Error parsing JSON: {e}")

with tab3:
    st.header("🤖 Pentest Assistant Chatbot")
    st.write("Ask me anything! For example:")
    st.markdown("- *How to exploit this XSS?*")
    st.markdown("- *Is this SQL injection real?*")
    st.markdown("- *How to fix this vulnerability?*")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask the Pentest Assistant..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consulting Groq LLaMA 3.3..."):
                response = analyze_with_llm(
                    "You are an expert penetration tester and secure coding assistant. Answer the user's questions clearly, concisely, and with educational exploit steps and remediation advice if asked.",
                    prompt
                )
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
