import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def get_connection():
    """
    Estabelece e retorna a conexão com o banco de dados PostgreSQL
    utilizando as credenciais seguras do arquivo .env.
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def inicializar_banco():
    """
    Cria as tabelas (chamados e usuarios) no PostgreSQL caso elas não existam.
    Ótimo para rodar na primeira vez que o projeto inicia.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Criando a tabela de chamados exatamente como pedido no enunciado
    # Nota: No Postgres, nomes de colunas em minúsculo evitam problemas de sintaxe.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chamados (
            id SERIAL PRIMARY KEY,
            cliente VARCHAR(150) NOT NULL,
            descricao TEXT NOT NULL,
            prioridade VARCHAR(20) NOT NULL, -- Baixa/Média/Alta
            status VARCHAR(30) NOT NULL DEFAULT 'Aberto', -- Aberto/Em Atendimento/Resolvido
            statusfinal BOOLEAN DEFAULT FALSE -- FALSE = Ativo na fila, TRUE = Cancelado/Arquivado
        );
    """)
    
    # Criando a tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            senha VARCHAR(255) NOT NULL
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Banco de dados inicializado com sucesso!")

# ==========================================
# OPERAÇÕES DO CRUD PARA OS CHAMADOS
# ==========================================

def criar_chamado(cliente, descricao, prioridade):
    """
    [CREATE] Insere um novo chamado no banco de dados.
    Todo chamado nasce com o status 'Aberto' e statusfinal como FALSE (Ativo).
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO chamados (cliente, descricao, prioridade, status, statusfinal)
        VALUES (%s, %s, %s, 'Aberto', FALSE);
    """
    cursor.execute(query, (cliente, descricao, prioridade))
    
    conn.commit()
    cursor.close()
    conn.close()

def listar_chamados_pendentes():
    """
    [READ] Retorna a fila de chamados que não foram desabilitados (statusfinal = FALSE).
    Usa o DictCursor para conseguirmos acessar os dados no HTML por nome (ex: chamado['cliente']).
    """
    conn = get_connection()
    # DictCursor transforma a tupla de retorno em algo parecido com um dicionário Python
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    query = "SELECT * FROM chamados WHERE statusfinal = FALSE ORDER BY id DESC;"
    cursor.execute(query)
    chamados = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return chamados

def atualizar_status_chamado(id_chamado, novo_status):
    """
    [UPDATE] Altera o status do chamado (ex: para 'Em Atendimento' ou 'Resolvido').
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "UPDATE chamados SET status = %s WHERE id = %s;"
    cursor.execute(query, (novo_status, id_chamado))
    
    conn.commit()
    cursor.close()
    conn.close()

def desabilitar_chamado(id_chamado):
    """
    [DISABLE] Altera o campo statusfinal para TRUE.
    Isso some com o chamado da fila de atendimento (READ), mas o mantém salvo no banco.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "UPDATE chamados SET statusfinal = TRUE WHERE id = %s;"
    cursor.execute(query, (id_chamado,))
    
    conn.commit()
    cursor.close()
    conn.close()


# Este bloco serve para você testar a criação das tabelas direto pelo terminal
if __name__ == "__main__":
    inicializar_banco()