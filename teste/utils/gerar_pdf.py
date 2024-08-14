from fpdf import FPDF

def gerar_relatorio_pdf(dados, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for dado in dados:
        pdf.cell(200, 10, txt=dado, ln=True)

    pdf.output(filename)


