import psycopg2 as pg
from auth import gerarSenhaHash, checarSenhaHash

def autenticar_usuario(dados_db, usuario, senha):
    conn = None
    cursor = None

    try:
        conn = pg.connect(database = dados_db['db_name'], user=dados_db['db_user'], password=dados_db['db_password'], host=dados_db['host_db'], port=dados_db['port'])
        cursor = conn.cursor()
        query = """SELECT d.id, d.nome_simples, d.senha_hash, d.nivel_acesso, c.cargo
                    FROM colaborador.dados d
                    JOIN colaborador.cargos c
                    ON d.nivel_acesso = c.id_cargo
                    WHERE d.usuario = %s
                    AND d.ativo = TRUE"""
        
        cursor.execute(query, (usuario,))

        resultado = cursor.fetchone()

        if not resultado:
            return None

        if checarSenhaHash(resultado[2], senha):
            return {
                "id": resultado[0],
                "nome": resultado[1],
                "id_acesso": resultado[3],
                "cargo": resultado[4]
            }
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()




def getListaColaboradores(dados_db):
    connection = None
    cursor = None
    listaColabs = []

    try:
        connection = pg.connect(database=dados_db['db_name'], user=dados_db['db_user'], password=dados_db['db_password'],
            host=dados_db['host_db'],port=dados_db['port'])

        cursor = connection.cursor()
        
        query = """
            SELECT id, nome_simples, usuario, nivel_acesso, ativo
            FROM colaborador.dados
            """
        
        cursor.execute(query)

        resultado = cursor.fetchall()

        if not resultado:
            return None
        
        listaColabs = [
        {
            "id": row[0],
            "nome_simples": row[1],
            "usuario": row[2],
            "nivel_acesso": row[3],
            "ativo": row[4]
        }
        for row in resultado
        ]
        
    except Exception as e:
        if connection:
            connection.rollback()
            print(f"Erro ao atualizar item: {e}")
            return False

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return listaColabs


def getQtyColabs(dados_db):
    connection = None
    cursor = None
    
    try:
        connection = pg.connect(database=dados_db['db_name'], user=dados_db['db_user'], password=dados_db['db_password'],
            host=dados_db['host_db'],port=dados_db['port'])

        cursor = connection.cursor()
        
        query_total = """SELECT COUNT(*) FROM colaborador.dados"""
        query_ativos = """SELECT COUNT(*) FROM colaborador.dados WHERE ativo = True"""
        
        cursor.execute(query_total)
        total_colabs = cursor.fetchone()[0]

        cursor.execute(query_ativos)
        ativos = cursor.fetchone()[0]

        if total_colabs is None or ativos is None:
            return None
        
        resultado = {
            "total": total_colabs,
            "ativos": ativos
        }
        
    except Exception as e:
        if connection:
            connection.rollback()
            print(f"Falha: {e}")
            return False

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return resultado


def getDadosColaborador(dados_db, id_colab):
    pass

def novoColaborador(dados_db):
    pass


def alterarSenha(dados_db, pw_atual, pw_novo):
    pass

def recuperarSenha(dados_db, cpf):
    pass