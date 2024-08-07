from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def gerar_pdf(transacoes):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 40
    for transacao in transacoes:
        c.drawString(40, y, f"Data: {transacao['data']} - Valor: {transacao['valor']} - Método de Pagamento: {transacao['metodo_pagamento']}")
        y -= 20
        for item in transacao['itens']:
            c.drawString(60, y, f"Produto: {item['produto']} - Quantidade: {item['quantidade']} x Preço: {item['preco']} = Total: {item['total']}")
            y -= 20
        y -= 10

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
