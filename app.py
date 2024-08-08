from datetime import datetime
from datetime import datetime, date, timedelta
import io
from flask import Flask, jsonify, render_template, request, redirect, send_file, url_for, session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from models import FechamentoCaixa, Transacao, db, Usuario, Categoria, Produto, ItemTransacao

from utils import gerar_pdf
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartcaixa.db'
app.config['SECRET_KEY'] = 'Ayce'
app.config['UPLOAD_FOLDER'] = 'static/imagens'
db.init_app(app)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
def index():
    if 'usuario' in session:
        return redirect(url_for('pdv'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario']
    senha = request.form['senha']
    user = Usuario.query.filter_by(usuario=usuario).first()
    if user and check_password_hash(user.senha, senha):
        login_user(user)
        session['usuario'] = usuario
        return redirect(url_for('pdv'))
    return 'Usuário ou senha inválidos', 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('usuario', None)
    return redirect(url_for('index'))

@app.route('/pdv')
@login_required
def pdv():
    return render_template('pdv.html')

@app.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    
    dados = request.get_json()
    carrinho = dados.get('carrinho', [])
    pagamento = dados.get('pagamento')
    valor_recebido = dados.get('valor_recebido')
    imprimir_nota = dados.get('imprimir_nota', False)
    
    if not carrinho:
        return jsonify({'status': 'error', 'message': 'Carrinho vazio!'}), 400
    
    total = sum(item['preco'] * item['quantidade'] for item in carrinho)
    troco = valor_recebido - total

    if pagamento == 'dinheiro' and troco < 0:
        return jsonify({'status': 'error', 'message': 'Valor recebido insuficiente!'}), 400

    for item in carrinho:
        produto = Produto.query.get(item['id'])
        if produto:
            produto.estoque -= item['quantidade']
            if produto.estoque < 0:
                return jsonify({'status': 'error', 'message': f'Estoque insuficiente para {produto.nome}!'}), 400
            db.session.add(produto)
    
    nova_transacao = Transacao(
        data=datetime.now(),
        valor=total,
        metodo_pagamento=pagamento
    )
    db.session.add(nova_transacao)
    db.session.commit()
    
    for item in carrinho:
        item_transacao = ItemTransacao(
            produto_id=item['id'],
            quantidade=item['quantidade'],
            preco=item['preco'],
            transacao=nova_transacao
        )
        db.session.add(item_transacao)
    
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Compra finalizada com sucesso!'}), 200
    
    

@app.route('/categorias')
def categorias():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    categorias = Categoria.query.all()
    return render_template('categorias.html', categorias=categorias)

@app.route('/add_categoria', methods=['POST'])
def add_categoria():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    nome_categoria = request.form['nome_categoria']
    nova_categoria = Categoria(nome=nome_categoria)
    db.session.add(nova_categoria)
    db.session.commit()
    return redirect(url_for('categorias'))

@app.route('/produtos')
def produtos():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    produtos = Produto.query.all()
    categorias = Categoria.query.all()
    return render_template('produtos.html', produtos=produtos, categorias=categorias)

@app.route('/add_produto', methods=['POST'])
def add_produto():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    nome_produto = request.form['nome_produto']
    descricao_produto = request.form['descricao_produto']
    codigo_barras = request.form['codigo_barras']
    preco_produto = request.form['preco_produto']
    estoque_produto = request.form['estoque_produto']
    categoria_id = request.form['categoria_id']
    
    imagem_produto = request.files['imagem_produto']
    imagem_path = None
    if imagem_produto:
        imagem_filename = secure_filename(imagem_produto.filename)
        imagem_path = os.path.join(app.config['UPLOAD_FOLDER'], imagem_filename)
        imagem_produto.save(imagem_path)
    
    novo_produto = Produto(
        nome=nome_produto,
        descricao=descricao_produto,
        codigo_barras=codigo_barras,
        preco=preco_produto,
        estoque=estoque_produto,
        imagem=imagem_path,
        categoria_id=categoria_id
    )
    db.session.add(novo_produto)
    db.session.commit()
    return redirect(url_for('produtos'))

@app.route('/edit_produto/<int:produto_id>', methods=['POST'])
def edit_produto(produto_id):
    if 'usuario' not in session:
        return redirect(url_for('index'))
    
    produto = Produto.query.get_or_404(produto_id)
    
    # Obtendo valores do formulário e garantindo que não sejam None
    nome_produto = request.form.get('nome_produto')
    descricao_produto = request.form.get('descricao_produto')
    codigo_barras = request.form.get('codigo_barras')
    preco_produto = request.form.get('preco_produto')
    estoque_produto = request.form.get('estoque_produto')
    categoria_id = request.form.get('categoria_id')
    
    # Verificando se os valores não são vazios
    if nome_produto:
        produto.nome = nome_produto
    if descricao_produto:
        produto.descricao = descricao_produto
    if codigo_barras:
        produto.codigo_barras = codigo_barras
    if preco_produto:
        produto.preco = preco_produto
    if estoque_produto:
        produto.estoque = estoque_produto
    if categoria_id:
        produto.categoria_id = categoria_id
    
    imagem_produto = request.files.get('imagem_produto')
    if imagem_produto and imagem_produto.filename:
        imagem_filename = secure_filename(imagem_produto.filename)
        imagem_produto.save(os.path.join(app.config['UPLOAD_FOLDER'], imagem_filename))
        produto.imagem = imagem_filename

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Adicione um log ou um tratamento de erro aqui se necessário
        print(f"Erro ao atualizar o produto: {e}")
        return redirect(url_for('produtos', error="Erro ao atualizar o produto"))
    
    return redirect(url_for('produtos'))



@app.route('/transacoes')
def transacoes():
    filtro = request.args.get('filtro', 'hoje')
    pagina = int(request.args.get('page', 1))
    limite = 200  # Número de transações por página

    # Filtra transações com base no filtro (hoje, semana, mês)
    if filtro == 'hoje':
        transacoes_query = Transacao.query.filter(Transacao.data >= date.today())
    elif filtro == 'semana':
        start_date = date.today() - timedelta(days=date.today().weekday())
        transacoes_query = Transacao.query.filter(Transacao.data >= start_date)
    elif filtro == 'mes':
        start_date = date.today().replace(day=1)
        transacoes_query = Transacao.query.filter(Transacao.data >= start_date)
    else:
        transacoes_query = Transacao.query

    # Contar total de transações para paginação
    total_transacoes = transacoes_query.count()
    
    # Paginando os resultados
    transacoes_detalhadas = transacoes_query.paginate(page=pagina, per_page=limite)

    # Calculando o total dos valores
    total = sum(t.valor for t in transacoes_detalhadas.items)

    return render_template('transacoes.html', 
                           transacoes_detalhadas=transacoes_detalhadas.items, 
                           filtro=filtro,
                           pagina=pagina,
                           total_transacoes=total_transacoes,
                           limite=limite,
                           total=total)
@app.route('/fechamento', methods=['GET', 'POST'])
def fechamento():
    if 'usuario' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Início do fechamento
        abertura = request.form.get('abertura')
        fechamento = datetime.now()
        usuario_id = Usuario.query.filter_by(usuario=session['usuario']).first().id

        # Ajuste o formato da data de abertura
        try:
            abertura_datetime = datetime.strptime(abertura, '%Y-%m-%dT%H:%M')
        except ValueError:
            return "Formato de data e hora inválido. Use o formato 'YYYY-MM-DDTHH:MM'.", 400

        # Criação do fechamento
        fechamento_caixa = FechamentoCaixa(
            abertura=abertura_datetime,
            fechamento=fechamento,
            usuario_id=usuario_id
        )
        db.session.add(fechamento_caixa)
        db.session.commit()

        # Calcular totais
        total_pix = db.session.query(db.func.sum(Transacao.valor)).filter(
            Transacao.metodo_pagamento == 'pix',
            Transacao.data >= abertura_datetime,
            Transacao.data <= fechamento
        ).scalar() or 0

        total_debito = db.session.query(db.func.sum(Transacao.valor)).filter(
            Transacao.metodo_pagamento == 'debito',
            Transacao.data >= abertura_datetime,
            Transacao.data <= fechamento
        ).scalar() or 0

        total_credito = db.session.query(db.func.sum(Transacao.valor)).filter(
            Transacao.metodo_pagamento == 'credito',
            Transacao.data >= abertura_datetime,
            Transacao.data <= fechamento
        ).scalar() or 0

        total_dinheiro = db.session.query(db.func.sum(Transacao.valor)).filter(
            Transacao.metodo_pagamento == 'dinheiro',
            Transacao.data >= abertura_datetime,
            Transacao.data <= fechamento
        ).scalar() or 0

        fechamento_caixa.total_pix = total_pix
        fechamento_caixa.total_debito = total_debito
        fechamento_caixa.total_credito = total_credito
        fechamento_caixa.total_dinheiro = total_dinheiro

        db.session.commit()

        return render_template('fechamento.html', fechamento=fechamento_caixa)

    return render_template('fechamento.html')

@app.route('/configuracoes')
def configuracoes():
    if current_user.is_admin:
        usuarios = Usuario.query.all()
        return render_template('configuracoes.html', usuarios=usuarios)
    return redirect(url_for('pdv'))

@app.route('/add_usuario', methods=['POST'])
def add_usuario():
    usuario = request.form['usuario']
    senha = request.form['senha']
    nivel_acesso = request.form['nivel_acesso']
    
    senha_hash = generate_password_hash(senha)
    novo_usuario = Usuario(usuario=usuario, senha=senha_hash, nivel_acesso=nivel_acesso)
    db.session.add(novo_usuario)
    db.session.commit()
    
    return redirect(url_for('configuracoes'))

# Adicione uma rota para deletar um usuário
@app.route('/delete_usuario', methods=['POST'])
def delete_usuario():
    usuario_id = request.form['usuario_id']
    usuario = Usuario.query.get(usuario_id)
    
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
    
    return redirect(url_for('configuracoes'))

@app.route('/gerar_relatorio', methods=['POST'])
def gerar_relatorio():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    transacoes = Transacao.query.all()
    resumo = [f"{t.data} - {t.valor} - {t.metodo_pagamento}" for t in transacoes]
    gerar_pdf(resumo)
    return redirect(url_for('fechamento'))

@app.route('/search_produto', methods=['GET'])
def search_produto():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    query = request.args.get('query', '')
    produtos = Produto.query.filter(
        Produto.nome.ilike(f'%{query}%') | Produto.codigo_barras.ilike(f'%{query}%')
    ).all()
    produtos_list = [{'id': p.id, 'nome': p.nome, 'descricao': p.descricao, 'codigo_barras': p.codigo_barras, 'preco': p.preco, 'estoque': p.estoque} for p in produtos]
    return jsonify(produtos_list)

def gerar_pdf(resumo):
    # Função fictícia para gerar PDF
    pass

from app import app  

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=13400, debug=True)

