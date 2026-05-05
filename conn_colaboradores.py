from db_configdata import conectarBanco
from conn_auth import gerarSenhaHash, checarSenhaHash
from psycopg2 import errors as pg_err
from datetime import datetime

def autenticar_usuario(usuario, senha):
    connection = None
    cursor = None

    try:
        connection = conectarBanco()
        cursor = connection.cursor()
        query = """SELECT d.id, d.apelido, d.senha_hash, d.nivel_acesso, c.cargo, d.primeiro_acesso
                    FROM colaborador.dados d
                    JOIN colaborador.cargos c
                    ON d.nivel_acesso = c.id_acesso
                    WHERE d.usuario = %s
                    AND d.is_ativo = TRUE"""
        
        cursor.execute(query, (usuario,))

        dadosColab = cursor.fetchone()

        if not dadosColab:
            return None

        if checarSenhaHash(dadosColab[2], senha):
            return {
                "u_id": dadosColab[0],
                "u_apelido": dadosColab[1],
                "nivel_acesso": dadosColab[3],
                "cargo": dadosColab[4],
                "u_primeiro_acesso": dadosColab[5]
            }
        return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def getAcessos(id):
    connection = None
    cursor = None

    try:
        connection = conectarBanco()
        cursor = connection.cursor()
        query = """SELECT *
                    FROM colaborador.acessos
                    WHERE id_usuario = %s"""
    
        cursor.execute(query, (id,))
        dadosAcessos = cursor.fetchone()
        return {
                    "ver_estoque": dadosAcessos[1],
                    "editar_item_estoque": dadosAcessos[2],
                    "ver_vendas": dadosAcessos[3],
                    "registrar_vendas": dadosAcessos[4],
                    "editar_vendas": dadosAcessos[5],
                    "ver_os": dadosAcessos[6],
                    "registrar_os": dadosAcessos[7],
                    "editar_os": dadosAcessos[8],
                    "ver_cautela": dadosAcessos[9],
                    "registrar_cautela": dadosAcessos[10],
                    "editar_cautela": dadosAcessos[11],
                    "ver_relatorios": dadosAcessos[12],
                    "apagar_dados": dadosAcessos[13]
                }

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def contaIniciada(usuario, senha_nova_hash):
    try:
        with conectarBanco() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE colaborador.dados SET senha_hash = %s, primeiro_acesso = false where id = %s",
                    (senha_nova_hash, usuario)
                )
    except Exception as e:
        print(f"Erro ao atualizar último login: {e}")
        return False

def compararSenhaHash(usuario, senha_inserida):
    try:
        with conectarBanco() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT senha_hash from colaborador.dados where id = %s",
                    (usuario,)
                )
                row = cursor.fetchone()
                if not row:
                    return False
                senha_db_hash = row[0]
                return checarSenhaHash(senha_db_hash, senha_inserida)

    except Exception as e:
        print(f"Erro ao atualizar último login: {e}")
        return False


def ultimoLogin(u_id):
    try:
        with conectarBanco() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE colaborador.dados SET data_ult_login = NOW() WHERE id = %s",
                    (u_id,)
                )
    except Exception as e:
        print(f"Erro ao atualizar último login: {e}")


def getListaColaboradores(so_ativos=False):
    connection = None
    cursor = None
    listaColabs = []

    try:
        connection = conectarBanco()

        cursor = connection.cursor()
        
        query = """
            SELECT d.id, d.apelido, d.usuario, d.nivel_acesso, d.is_ativo, c.cargo
            FROM colaborador.dados d
            JOIN colaborador.cargos c
            ON d.nivel_acesso = c.id_acesso
            """
        
        if so_ativos == True:
            query = query + " where is_ativo = true"
        
        cursor.execute(query)

        resultado = cursor.fetchall()

        if not resultado:
            return None
        
        listaColabs = [
        {
            "id": row[0],
            "apelido": row[1],
            "usuario": row[2],
            "nivel_acesso": row[3],
            "is_ativo": row[4],
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


def getCargos():
    connection = None
    cursor = None
    
    try:
        connection = conectarBanco()

        cursor = connection.cursor()
        
        query = """SELECT id_acesso, cargo 
        FROM colaborador.cargos WHERE id_acesso <> 1 ORDER BY id_acesso ASC"""
        
        cursor.execute(query)
        cargos = cursor.fetchall()

        if not cargos:
            return []
        
        lista_cargos = []

        for id_cargo, cargo in cargos:
            lista_cargos.append({
                "id_acesso": id_cargo,
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


def getQtyColabs():
    connection = None
    cursor = None
    
    try:
        connection = conectarBanco()

        cursor = connection.cursor()
        
        query_total = """SELECT COUNT(*) FROM colaborador.dados"""
        query_ativos = """SELECT COUNT(*) FROM colaborador.dados WHERE is_ativo = True"""
        
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

def setNovoColaborador(dados_colab, operador):
    connection = None
    cursor = None
    
    try:
        connection = conectarBanco()

        cursor = connection.cursor()

        nome_completo = dados_colab["nome_completo"]
        usuario = dados_colab["usuario"]
        senha_hash = gerarSenhaHash("1234")
        nivel_acesso = dados_colab["nivel_acesso"]
        apelido = dados_colab["apelido"]
        operador_inclusao = operador
        identidade_hash = gerarSenhaHash(dados_colab["identidade"])
        
        query = """INSERT INTO colaborador.dados (
            nome_completo, 
            usuario, 
            senha_hash,
            nivel_acesso, 
            apelido, 
            data_inclusao, 
            operador_inclusao, 
            identidade_hash) VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s)"""
        
        cursor.execute((query), (nome_completo, usuario, senha_hash, nivel_acesso, apelido, operador_inclusao, identidade_hash))
        connection.commit()

    except pg_err.UniqueViolation:
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



def getDadosColaborador(id_colab):
    connection = None
    cursor = None
    
    try:
        connection = conectarBanco()

        cursor = connection.cursor()
        
        query = """SELECT
                        d.id,
                        d.apelido,
                        d.nome_completo,
                        d.usuario,
                        d.is_ativo,
                        d.nivel_acesso,
                        c.cargo,
                        d.data_inclusao,

                        inc.apelido AS operador_inclusao,
                        d.data_modificacao,
                        mod.apelido AS operador_modificacao,
                        d.data_ult_login
                    FROM colaborador.dados d
                    JOIN colaborador.cargos c
                        ON c.id_acesso = d.nivel_acesso
                    LEFT JOIN colaborador.dados inc
                        ON inc.id = d.operador_inclusao
                    LEFT JOIN colaborador.dados mod
                        ON mod.id = d.operador_modificacao
                    WHERE d.id = %s;
                    """
        
        cursor.execute((query), (id_colab,))
        
        resultado = cursor.fetchone()

        if not resultado:
            return None

        colaborador = {
                "id": resultado[0],
                "apelido": resultado[1],
                "nome_completo": resultado[2],
                "nome_usuario": resultado[3],
                "is_ativo": resultado[4],
                "nivel_acesso": resultado[5],
                "cargo": resultado[6],
                "data_inclusao": resultado[7].strftime("%d/%m/%Y - %H:%M:%S")
                    if resultado[7] else None,
                "operador_inclusao": resultado[8],
                "data_modificacao": resultado[9].strftime("%d/%m/%Y - %H:%M:%S")
                    if resultado[9] else None,
                "operador_modificacao": resultado[10],
                "data_ult_login": resultado[11].strftime("%d/%m/%Y - %H:%M:%S"),
                "delta_dias": (datetime.now().date() - resultado[11].date()).days if resultado[11] else None
            }

        return colaborador
    
    except Exception as e:
        if connection:
            connection.rollback()
            print(f"Falha ao consultar dados do colaborador: {e}")
            return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    
    return True


def setDadosColaborador(id, novos_dados_colab, operador):
    connection = None
    cursor = None
    
    try:
        connection = conectarBanco()
        cursor = connection.cursor()

        nome_completo = novos_dados_colab["nome_completo"]
        usuario = novos_dados_colab["usuario"]
        is_ativo = novos_dados_colab["is_ativo"]
        nivel_acesso = novos_dados_colab["nivel_acesso"]
        apelido = novos_dados_colab["apelido"]
        operador_modificacao = operador

        
        
        query = """UPDATE colaborador.dados SET
            nome_completo = %s, 
            usuario = %s,
            is_ativo = %s,
            nivel_acesso = %s, 
            apelido = %s,
            data_modificacao = NOW(), 
            operador_modificacao = %s
            WHERE id = %s"""
        
        cursor.execute((query), (nome_completo, usuario, is_ativo, nivel_acesso, apelido, operador_modificacao, id))
        connection.commit()

    except pg_err.UniqueViolation:
        if connection:
            connection.rollback()
        return "USERNAME_DUPLICADO"
    
    except Exception as e:
        if connection:
            connection.rollback()
            
            print(f"Falha ao gravar alteração: {e}")
            return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    
    return True

def alterarSenha(id, novo_pw):
    try:
        with conectarBanco() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE colaborador.dados SET senha_hash = %s where id = %s",
                    (gerarSenhaHash(novo_pw), id)
                )
    except Exception as e:
        print(f"Erro ao alterar senha: {e}")
        return False

def recuperarSenha(cpf):
    pass








