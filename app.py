import base64
import json
import os
import tempfile

import streamlit as st

from ai_dast import analyze_dast_findings
from ai_parsers import parse_dast_report, parse_sonar_report
from ai_sast import analyze_sast_findings
from ai_utils import analyze_with_llm, create_pdf_report, validate_api_key

st.set_page_config(page_title="AI SecOps Platform", layout="wide", page_icon="🛡️")

st.markdown(
    """
    <style>
    .main { background-color: #f8f9fa; }
    .metric-card {
        background: #ffffff; border: 1px solid #dee2e6;
        border-radius: 8px; padding: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🛡️ AI DevSecOps Platform")
st.markdown("**SAST · DAST · RAG-powered Pentest Assistant** — Groq LLaMA 3.3 + ChromaDB")


def download_link(file_path, label):
    if not os.path.exists(file_path):
        return
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    st.markdown(
        f'<a href="data:application/octet-stream;base64,{data}" download="{os.path.basename(file_path)}">{label}</a>',
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.header("System Status")
    api_ok, api_msg = validate_api_key()
    if api_ok:
        st.success(f"Groq API: Connected ({api_msg[:20]})")
    else:
        st.error(f"Groq API: {api_msg}")
        st.info("Set `GROQ_API_KEY` in your environment or `.env` for docker-compose.")

    st.divider()
    max_issues = st.slider("Max findings to analyze", 1, 20, 10)
    include_summary = st.checkbox("Generate executive summary", value=True)

tab1, tab2, tab3 = st.tabs(["SAST Analyzer", "DAST Analyzer", "Pentest Assistant"])

with tab1:
    st.header("🔍 SAST Analysis")
    st.write("Upload SonarQube JSON (`sonar-report.json`) for AI-driven remediation with source context.")

    sast_file = st.file_uploader("Upload SAST Report", type="json", key="sast")
    if sast_file and st.button("Run AI SAST Analysis", key="run_sast"):
        with st.spinner("Analyzing static findings with RAG..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="wb") as tmp:
                tmp.write(sast_file.getvalue())
                tmp_path = tmp.name

            issues = parse_sonar_report(tmp_path)
            os.unlink(tmp_path)

            if not issues:
                st.warning("No issues found in the uploaded report.")
            else:
                results, summary = analyze_sast_findings(
                    issues, max_issues=max_issues, include_summary=include_summary
                )
                st.session_state["sast_results"] = results
                st.session_state["sast_summary"] = summary

                with open("ai_sast_output.json", "w", encoding="utf-8") as f:
                    json.dump({"summary": summary, "findings": results}, f, indent=4)
                create_pdf_report(
                    "AI-Enhanced SAST Security Analysis Report",
                    results,
                    "ai_sast_report.pdf",
                    executive_summary=summary,
                )
                st.success(f"Analyzed {len(results)} SAST findings.")

    if st.session_state.get("sast_results"):
        if st.session_state.get("sast_summary"):
            with st.expander("Executive Summary", expanded=True):
                st.markdown(st.session_state["sast_summary"])
        for item in st.session_state["sast_results"]:
            with st.expander(f"{item['vuln_id']} — {item['vulnerability_type']} ({item.get('severity', 'N/A')})"):
                st.markdown(f"**Location:** `{item['code_location']}` (line {item.get('line', 'N/A')})")
                st.markdown(f"**Issue:** {item['description']}")
                st.markdown(item["ai_expert_analysis"])
        col1, col2 = st.columns(2)
        with col1:
            download_link("ai_sast_report.pdf", "⬇️ Download SAST PDF")
        with col2:
            download_link("ai_sast_output.json", "⬇️ Download SAST JSON")

with tab2:
    st.header("⚡ DAST Analysis")
    st.write("Upload **Nuclei** (`nuclei-report.json`) or **OWASP ZAP** (`zap-report.json`) reports.")

    dast_file = st.file_uploader("Upload DAST Report", type="json", key="dast")
    if dast_file and st.button("Run AI DAST Analysis", key="run_dast"):
        with st.spinner("Analyzing dynamic findings with RAG..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="wb") as tmp:
                tmp.write(dast_file.getvalue())
                tmp_path = tmp.name

            findings, scanner = parse_dast_report(tmp_path)
            os.unlink(tmp_path)

            if not findings:
                st.warning("No findings detected. Ensure the file is Nuclei or ZAP JSON format.")
            else:
                results, summary = analyze_dast_findings(
                    findings,
                    max_issues=max_issues,
                    include_summary=include_summary,
                    scanner=scanner.upper(),
                )
                st.session_state["dast_results"] = results
                st.session_state["dast_summary"] = summary
                st.session_state["dast_scanner"] = scanner

                with open("ai_dast_output.json", "w", encoding="utf-8") as f:
                    json.dump(
                        {"summary": summary, "findings": results, "scanner": scanner},
                        f,
                        indent=4,
                    )
                create_pdf_report(
                    f"AI-Enhanced {scanner.upper()} Pentest Report",
                    results,
                    "ai_dast_report.pdf",
                    executive_summary=summary,
                )
                st.success(f"Analyzed {len(results)} {scanner.upper()} findings.")

    if st.session_state.get("dast_results"):
        scanner = st.session_state.get("dast_scanner", "DAST")
        st.caption(f"Scanner: {scanner.upper()}")
        if st.session_state.get("dast_summary"):
            with st.expander("Executive Summary", expanded=True):
                st.markdown(st.session_state["dast_summary"])
        for item in st.session_state["dast_results"]:
            with st.expander(
                f"{item['vuln_id']} — {item['vulnerability_type']} ({item.get('severity', 'N/A')})"
            ):
                st.markdown(f"**URL:** `{item['target_url']}`")
                if item.get("parameter"):
                    st.markdown(f"**Parameter:** `{item['parameter']}`")
                st.markdown(f"**Payload:** `{item.get('payload', 'N/A')}`")
                st.markdown(item["ai_pentest_analysis"])
        col1, col2 = st.columns(2)
        with col1:
            download_link("ai_dast_report.pdf", "⬇️ Download DAST PDF")
        with col2:
            download_link("ai_dast_output.json", "⬇️ Download DAST JSON")

with tab3:
    st.header("🤖 Pentest Assistant")
    st.info("Powered by **Groq LLaMA 3.3** + **Security RAG** (OWASP/NIST knowledge base).")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    with st.sidebar:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        if st.session_state.messages:
            if st.button("Export Chat to PDF"):
                chat_data = [
                    f"[{'USER' if m['role'] == 'user' else 'AI ASSISTANT'}]:\n{m['content']}\n"
                    for m in st.session_state.messages
                ]
                create_pdf_report("AI Pentest Assistant Conversation", chat_data, "chatbot_conversation.pdf")
                st.success("PDF generated.")
                download_link("chatbot_conversation.pdf", "⬇️ Download Chat PDF")

    if prompt := st.chat_input("How do I fix Blind SQL Injection in Node.js?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing with RAG knowledge..."):
                sys_prompt = (
                    "You are an expert penetration tester and secure coding assistant. "
                    "Give practical, step-by-step guidance with code examples. "
                    "Structure answers with: Impact, Detection, Exploitation, Fix, Prevention."
                )
                response = analyze_with_llm(sys_prompt, prompt, use_rag=True)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
