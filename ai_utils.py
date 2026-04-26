import os
import json
from fpdf import FPDF
from groq import Groq
from ai_rag import rag_system

# Using the provided key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
MODEL_NAME = "llama-3.3-70b-versatile"

client = Groq(api_key=GROQ_API_KEY)

def analyze_with_llm(system_prompt, user_prompt, use_rag=True):
    """
    Sends a structured prompt to the Groq LLM model, optionally using RAG for context.
    """
    context = ""
    if use_rag:
        # Retrieve context from RAG based on the user prompt
        context = rag_system.query(user_prompt)
    
    if context:
        augmented_prompt = f"""You are a specialized security assistant. Use the following retrieved security knowledge to enhance your response:

--- RETRIEVED CONTEXT ---
{context}
--- END CONTEXT ---

User Query: {user_prompt}

Please provide a highly detailed and accurate analysis based on the context above and your general expertise. Include risk levels, exploit examples, and secure code fixes."""
    else:
        augmented_prompt = user_prompt

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": augmented_prompt}
            ],
            model=MODEL_NAME,
            temperature=0.2,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error communicating with LLM: {e}")
        return f"Error: {e}"

def create_pdf_report(title, data, output_filename):
    """
    Generates a professional human-readable PDF report.
    Supports both structured vulnerability data and chatbot history.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Header with a subtle background color for the title area
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 20)
    pdf.cell(0, 20, title, ln=True, align='C', fill=True)
    pdf.ln(10)
    
    pdf.set_font("helvetica", size=11)
    
    # Process data and inject into PDF
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                # Handle structured vulnerability items
                for k, v in item.items():
                    if "id" in k.lower() or "url" in k.lower() or "location" in k.lower():
                        pdf.set_font("helvetica", "B", 12)
                        pdf.set_text_color(0, 51, 102) # Dark blue for targets
                        pdf.cell(0, 8, f"{k.replace('_', ' ').title()}: {v}", ln=True)
                        pdf.set_text_color(0, 0, 0) # Reset to black
                        pdf.set_font("helvetica", size=11)
                    elif "llm_analysis" in k.lower() or "analysis" in k.lower():
                        pdf.set_font("helvetica", "B", 11)
                        pdf.cell(0, 6, "AI Expert Analysis:", ln=True)
                        pdf.set_font("helvetica", size=10)
                        # Clean markdown and special chars for PDF compatibility
                        content = str(v).replace("**", "").replace("#", "").encode('latin-1', 'replace').decode('latin-1')
                        pdf.multi_cell(0, 5, content)
                        pdf.ln(2)
                    else:
                        pdf.set_font("helvetica", "B", 11)
                        pdf.cell(0, 6, f"{k.replace('_', ' ').title()}:", ln=True)
                        pdf.set_font("helvetica", size=10)
                        content = str(v).encode('latin-1', 'replace').decode('latin-1')
                        pdf.multi_cell(0, 5, content)
                        pdf.ln(2)
                
                pdf.ln(5)
                pdf.set_draw_color(200, 200, 200)
                pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
                pdf.ln(5)
            elif isinstance(item, str):
                # Handle plain text lines (e.g. chat messages)
                content = item.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 6, content)
                pdf.ln(2)
    
    pdf.output(output_filename)
