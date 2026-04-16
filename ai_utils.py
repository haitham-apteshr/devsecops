import os
import json
from fpdf import FPDF
from groq import Groq

# Using the provided key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
MODEL_NAME = "llama-3.3-70b-versatile"

client = Groq(api_key=GROQ_API_KEY)

def analyze_with_llm(system_prompt, user_prompt):
    """
    Sends a structured prompt to the Groq LLM model.
    """
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=MODEL_NAME,
            temperature=0.2,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error communicating with LLM: {e}")
        return f"Error: {e}"

def create_pdf_report(title, data, output_filename):
    """
    Generates a human-readable PDF report using fpdf2.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("helvetica", size=11)
    
    # Process data and inject into PDF
    for item in data:
        for k, v in item.items():
            if "id" in k or "url" in k:
                pdf.set_font("helvetica", "B", 12)
                pdf.cell(0, 8, f"Target: {v}", ln=True)
                pdf.set_font("helvetica", size=11)
            else:
                pdf.set_font("helvetica", "B", 11)
                pdf.cell(0, 6, f"{k.replace('_', ' ').title()}:", ln=True)
                pdf.set_font("helvetica", size=11)
                # Handle extended characters and multiline formats
                content = str(v).encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 6, content)
                pdf.ln(2)
        pdf.ln(5)
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 0, "", "T") # Divider line
        pdf.ln(5)
        
    pdf.output(output_filename)
