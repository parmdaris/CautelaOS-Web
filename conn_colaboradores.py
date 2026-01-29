import psycopg2 as pg
from psycopg2.extras import RealDictCursor
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
            SELECT d.id, d.nome_simples, d.usuario, d.nivel_acesso, d.ativo, c.cargo
            FROM colaborador.dados d
            JOIN colaborador.cargos c
            ON d.nivel_acesso = c.id_cargo
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
            "ativo": row[4],
            "cargo_acesso": row[5]
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


def getCargos(dados_db):
    connection = None
    cursor = None
    
    try:
        connection = pg.connect(database=dados_db['db_name'], user=dados_db['db_user'], password=dados_db['db_password'],
            host=dados_db['host_db'],port=dados_db['port'])

        cursor = connection.cursor()
        
        query = """SELECT id_cargo, cargo 
        FROM colaborador.cargos"""
        
        cursor.execute(query)
        cargos = cursor.fetchall()

        if not cargos:
            return []
        
        lista_cargos = []

        for id_cargo, cargo in cargos:
            lista_cargos.append({
                "id_cargo": id_cargo,
                "cargo": cargo
            })

        
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

    return lista_cargos


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

def novoColaborador(dados_db, dados_colab, data, operador):
    connection = None
    cursor = None
    
    try:
        connection = pg.connect(database=dados_db['db_name'], user=dados_db['db_user'], password=dados_db['db_password'],
            host=dados_db['host_db'],port=dados_db['port'])

        cursor = connection.cursor()

        nome_completo = dados_colab["nome_completo"]
        usuario = dados_colab["usuario"]
        senha_hash = gerarSenhaHash(dados_colab["senha"])
        nivel_acesso = dados_colab["nivel_acesso"]
        nome_simples = dados_colab["nome_simples"]
        operador_inclusao = operador
        identidade_hash = gerarSenhaHash(dados_colab["identidade"])
        
        query = """INSERT INTO colaborador.dados (
            nome_completo, 
            usuario, 
            senha_hash,
            nivel_acesso, 
            nome_simples, 
            data_inclusao, 
            operador_inclusao, 
            identidade_hash) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        
        cursor.execute((query), (nome_completo, usuario, senha_hash, nivel_acesso, nome_simples, data, operador_inclusao, identidade_hash))
        connection.commit()

    except pg.errors.UniqueViolation:
        if connection:
            connection.rollback()
        return "USERNAME_DUPLICADO"
    
    except Exception as e:
        if connection:
            connection.rollback()
            print(f"Falha: {e}")
            return {e}

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    
    return True



def getDadosColaborador(dados_db, id_colab):
    connection = None
    cursor = None
    
    try:
        connection = pg.connect(database=dados_db['db_name'], user=dados_db['db_user'], password=dados_db['db_password'],
            host=dados_db['host_db'],port=dados_db['port'])

        cursor = connection.cursor()
        
        query = """SELECT d.id, 
                        d.nome_simples, 
                        d.nome_completo, 
                        d.ativo, 
                        d.nivel_acesso, 
                        d.data_inclusao, 
                        d.operador_inclusao, 
                        d.usuario,
                        d.data_modificacao,
                        d.operador_modificacao,
                        c.cargo
                    FROM colaborador.dados d
                    JOIN colaborador.cargos c
                    ON d.nivel_acesso = c.id_cargo
                    WHERE d.id = %s"""
        
        cursor.execute((query), (id_colab,))
        
        resultado = cursor.fetchone()

        if not resultado:
            return None

        dados_colab = {
            "id": resultado[0],
            "nome_simples": resultado[1],
            "nome_completo": resultado[2],
            "nome_usuario": resultado[7],
            "ativo": resultado[3],
            "nivel_acesso": resultado[4],
            "cargo": resultado[10],
            "data_inclusao": resultado[5],
            "operador_inclusao": resultado[6],
            "data_modificacao": resultado[8],
            "operador_modificacao": resultado[9],
        }

        return dados_colab

    except pg.errors.UniqueViolation:
        if connection:
            connection.rollback()
        return "USERNAME_DUPLICADO"
    
    except Exception as e:
        if connection:
            connection.rollback()
            print(f"Falha: {e}")
            return {e}

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    
    return True



def alterarSenha(dados_db, pw_atual, pw_novo):
    pass

def recuperarSenha(dados_db, cpf):
    pass