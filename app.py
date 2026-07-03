from flask import Flask, render_template, request, redirect, url_for
import db  # Importa a nossa camada de persistência isolada

app = Flask(__name__)

# ==========================================
# TELA 1 - INÍCIO
# ==========================================
@app.route('/')
def index():
    """Painel de boas-vindas ao suporte."""
    return render_template('index.html')

# ==========================================
# TELA 2 - ABRIR CHAMADO (CREATE)
# ==========================================
@app.route('/novo', methods=['GET', 'POST'])
def novo_chamado():
    """
    GET: Mostra o formulário vazio.
    POST: Captura os dados do formulário e salva no banco.
    """
    if request.method == 'POST':
        cliente = request.form['cliente']
        descricao = request.form['descricao']
        prioridade = request.form['prioridade']
        
        # Chama a função isolada do banco de dados
        db.criar_chamado(cliente, descricao, prioridade)
        
        # Redireciona para a fila de suporte após criar
        return redirect(url_for('fila_suporte'))
    
    return render_template('novo_chamado.html')

# ==========================================
# TELA 3 - FILA DE SUPORTE (READ)
# ==========================================
@app.route('/fila')
def fila_suporte():
    """Lista os chamados vindos do banco de dados."""
    chamados_pendentes = db.listar_chamados_pendentes()
    return render_template('fila_suporte.html', chamados=chamados_pendentes)

# ==========================================
# AÇÕES DA FILA (UPDATE E DISABLE)
# ==========================================
@app.route('/atualizar/<int:id_chamado>', methods=['POST'])
def atualizar(id_chamado):
    """(UPDATE) Altera o status do chamado via botão."""
    novo_status = request.form.get('novo_status')
    if novo_status:
        db.atualizar_status_chamado(id_chamado, novo_status)
    return redirect(url_for('fila_suporte'))

@app.route('/desabilitar/<int:id_chamado>', methods=['POST'])
def desabilitar(id_chamado):
    """(DISABLE) Oculta o chamado da tela, mantendo no banco."""
    db.desabilitar_chamado(id_chamado)
    return redirect(url_for('fila_suporte'))


if __name__ == '__main__':
    # O debug=True ajuda muito na hora de programar, pois atualiza o servidor sozinho
    app.run(debug=True)