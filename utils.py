import io
from fpdf import FPDF

def gerar_pdf(itens):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for item in itens:
        pdf.cell(200, 10, txt=item, ln=True)
    
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    
    return pdf_output.getvalue()
