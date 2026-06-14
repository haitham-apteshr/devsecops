import os
import time
from fpdf import FPDF
from groq import Groq

from ai_rag import get_rag_context

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
MODEL_NAME = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
MAX_TOKENS = int(os.environ.get("GROQ_MAX_TOKENS", "2500"))
TEMPERATURE = float(os.environ.get("GROQ_TEMPERATURE", "0.15"))
MAX_RETRIES = int(os.environ.get("GROQ_MAX_RETRIES", "3"))
RETRY_DELAY = float(os.environ.get("GROQ_RETRY_DELAY", "2.0"))

_client = None


def get_groq_client():
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to your environment or Jenkins credentials."
            )
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


def validate_api_key():
    """Quick connectivity check used by Jenkins and the UI."""
    if not GROQ_API_KEY:
        return False, "GROQ_API_KEY is missing"
    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Reply with exactly: OK"}],
            model=MODEL_NAME,
            max_tokens=10,
            temperature=0,
        )
        reply = response.choices[0].message.content.strip()
        return True, reply
    except Exception as exc:
        return False, str(exc)


def analyze_with_llm(system_prompt, user_prompt, use_rag=True, extra_context=""):
    """
    Send a structured prompt to Groq with optional RAG and retry logic.
    """
    context_parts = []
    if use_rag:
        rag_context = get_rag_context(user_prompt)
        if rag_context:
            context_parts.append(rag_context)
    if extra_context:
        context_parts.append(extra_context)

    if context_parts:
        joined_context = "\n\n".join(context_parts)
        augmented_prompt = f"""Use the following security knowledge to ground your answer:

--- CONTEXT ---
{joined_context}
--- END CONTEXT ---

{user_prompt}

Provide a structured response with these sections:
1. Risk Assessment (Critical/High/Medium/Low + CVSS estimate if applicable)
2. Root Cause Analysis
3. Exploit Scenario / PoC
4. Secure Remediation (with code or config example)
5. Defense in Depth recommendations"""
    else:
        augmented_prompt = user_prompt

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = get_groq_client()
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": augmented_prompt},
                ],
                model=MODEL_NAME,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )
            return response.choices[0].message.content
        except Exception as exc:
            last_error = exc
            print(f"[!] LLM attempt {attempt}/{MAX_RETRIES} failed: {exc}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)

    return (
        f"AI analysis unavailable after {MAX_RETRIES} attempts. "
        f"Last error: {last_error}. Verify GROQ_API_KEY and network connectivity."
    )


def generate_executive_summary(scan_type, results):
    """Generate a pipeline-level executive summary from analyzed findings."""
    if not results:
        return "No findings were analyzed."

    findings_brief = []
    for item in results[:8]:
        findings_brief.append(
            f"- {item.get('vulnerability_type', 'Unknown')} "
            f"({item.get('severity', item.get('code_location', 'N/A'))}): "
            f"{str(item.get('description', ''))[:120]}"
        )

    summary_prompt = f"""You are a CISO reporting to engineering leadership.
Write a concise executive summary for a {scan_type} scan with these top findings:

{chr(10).join(findings_brief)}

Include:
- Overall risk posture (1 paragraph)
- Top 3 prioritized actions
- Estimated remediation effort (S/M/L)"""

    system_prompt = "You are a senior application security leader writing executive briefings."
    return analyze_with_llm(system_prompt, summary_prompt, use_rag=False)


def _sanitize_pdf_text(text):
    return (
        str(text)
        .replace("**", "")
        .replace("#", "")
        .replace("\u2014", "-")
        .replace("\u2013", "-")
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def create_pdf_report(title, data, output_filename, executive_summary=None):
    """Generate a professional PDF report from structured findings or chat history."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_fill_color(33, 37, 41)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 20)
    pdf.cell(0, 18, _sanitize_pdf_text(title), ln=True, align="C", fill=True)
    pdf.ln(8)

    if executive_summary:
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("helvetica", "B", 13)
        pdf.cell(0, 8, "Executive Summary", ln=True)
        pdf.set_font("helvetica", size=10)
        pdf.multi_cell(0, 5, _sanitize_pdf_text(executive_summary))
        pdf.ln(4)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
        pdf.ln(6)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", size=11)

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for key, value in item.items():
                    label = key.replace("_", " ").title()
                    if any(token in key.lower() for token in ("id", "url", "location", "severity")):
                        pdf.set_font("helvetica", "B", 11)
                        pdf.set_text_color(0, 51, 102)
                        pdf.cell(0, 7, f"{label}: {value}", ln=True)
                        pdf.set_text_color(0, 0, 0)
                    elif "analysis" in key.lower():
                        pdf.set_font("helvetica", "B", 11)
                        pdf.cell(0, 6, "AI Expert Analysis:", ln=True)
                        pdf.set_font("helvetica", size=10)
                        pdf.multi_cell(0, 5, _sanitize_pdf_text(value))
                        pdf.ln(2)
                    else:
                        pdf.set_font("helvetica", "B", 11)
                        pdf.cell(0, 6, f"{label}:", ln=True)
                        pdf.set_font("helvetica", size=10)
                        pdf.multi_cell(0, 5, _sanitize_pdf_text(value))
                        pdf.ln(2)

                pdf.ln(4)
                pdf.set_draw_color(220, 220, 220)
                pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
                pdf.ln(5)
            elif isinstance(item, str):
                pdf.multi_cell(0, 6, _sanitize_pdf_text(item))
                pdf.ln(2)

    pdf.output(output_filename)
