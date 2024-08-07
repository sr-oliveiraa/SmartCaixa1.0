from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)
    nivel_acesso = db.Column(db.String(20))

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    produtos = db.relationship('Produto', backref='categoria', lazy=True)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200))
    codigo_barras = db.Column(db.String(100), unique=True, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, nullable=False)
    imagem = db.Column(db.String(100))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)


    def atualizar_estoque(self, quantidade_vendida):
        if quantidade_vendida > self.estoque:
            raise ValueError("Quantidade vendida excede o estoque disponível.")
        self.estoque -= quantidade_vendida
        db.session.commit()

class Transacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    metodo_pagamento = db.Column(db.String(20), nullable=False)
    itens = db.relationship('ItemTransacao', backref='transacao', lazy=True)

    def adicionar_itens(self, itens):
        for item in itens:
            item_transacao = ItemTransacao(
                produto_id=item['id'],
                quantidade=item['quantidade'],
                preco=item['preco'],
                transacao=self
            )
            db.session.add(item_transacao)
        db.session.commit()

class ItemTransacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    transacao_id = db.Column(db.Integer, db.ForeignKey('transacao.id'), nullable=False)

    produto = db.relationship('Produto', backref='itens_transacao')

class FechamentoCaixa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abertura = db.Column(db.DateTime, nullable=False)
    fechamento = db.Column(db.DateTime)
    total_pix = db.Column(db.Float, default=0.0)
    total_debito = db.Column(db.Float, default=0.0)
    total_credito = db.Column(db.Float, default=0.0)
    total_dinheiro = db.Column(db.Float, default=0.0)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref='fechamentos')

