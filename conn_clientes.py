from ativ_sistema import conectarBanco
from psycopg2 import errors as pg_err

def getClientes(status = 1):

    connection = conectarBanco()
    connection.autocommit = True
    cursor = connection.cursor() 

    
    query_base = '''
        select id_cliente, 
        nome_cliente,
        nome_fantasia, 
        cnpj, 
        telefone_contato,
        is_ativo,
        is_contrato,
        is_venda
        from cliente.dados
        
        '''
    query_ativos = " where is_ativo = true"
    query_inativos = " where is_ativo = false"

    ordenacao = " order by id_cliente asc;"

    if status == -1:
        sql = query_base + query_inativos + ordenacao
    if status == 0:
        sql = query_base + ordenacao
    if status == 1:
        sql = query_base + query_ativos + ordenacao
        
    cursor.execute(sql) 
    dataset = cursor.fetchall()
    
    dados_clientes = []

    for row in dataset:
        dados_clientes.append({
            "id": row[0],
            "rsoc": row[1],
            "nome": row[2],
            "cnpj": row[3],
            "telefone": row[4],
            "isAtivo": row[5],
            "isContrato": row[6],
            "isVenda": row[7]
        })

    connection.close() 
    return dados_clientes


def getQtyClientes(status = 1):
    connection = None
    cursor = None

    connection = conectarBanco()
    connection.autocommit = True
    cursor = connection.cursor()

    query_base = '''SELECT COUNT(*) from cliente.dados'''
    query_ativo = " where is_ativo = true"
    query_inativo = " where is_ativo = false"

    if status == 1:
        sql = query_base + query_ativo
    if status == 0:
        sql = query_base
    if status == -1:
        sql = query_base + query_inativo

    cursor.execute(sql)
    resultado = cursor.fetchone()[0]
    connection.close()

    return resultado


def getClientesVenda():
      
    connection = conectarBanco()
    connection.autocommit = True
    cursor = connection.cursor() 

    query = '''
            select id_cliente, 
            nome_cliente,
            nome_fantasia, 
            cnpj, 
            telefone_contato 
            from cliente.dados
            where is_ativo = True
            and
            is_venda = True
            order by id_cliente asc;
        '''
    
    cursor.execute(query) 
    dataset = cursor.fetchall()
    
    dados_clientes = []

    for row in dataset:
        dados_clientes.append({
            "id": row[0],
            "rsoc": row[1],
            "nome": row[2],
            "cnpj": row[3],
            "telefone": row[4]
        })

    connection.close() 
    return dados_clientes



def getClientesContrato():
      
    connection = conectarBanco()
    connection.autocommit = True
    cursor = connection.cursor() 

    query = '''
            select id_cliente, 
            nome_cliente,
            nome_fantasia, 
            cnpj, 
            telefone_contato 
            from cliente.dados
            where is_ativo = True
            and
            is_contrato = True
            order by id_cliente asc;
        '''
    
    cursor.execute(query) 
    dataset = cursor.fetchall()
    
    dados_clientes = []

    for row in dataset:
        dados_clientes.append({
            "id": row[0],
            "rsoc": row[1],
            "nome": row[2],
            "cnpj": row[3],
            "telefone": row[4]
        })

    connection.close() 
    return dados_clientes


def getDadosCliente(id_cliente):
    connection = None
    cursor = None

    connection = conectarBanco()
    connection.autocommit = True
    cursor = connection.cursor()

    query = ''' SELECT 
                cli.id_cliente,
                cli.nome_cliente,
                cli.nome_fantasia,
                cli.cnpj,
                cli.telefone_contato,
                cli.is_ativo,
                cli.is_contrato,
                cli.is_venda,
                cli.data_cadastro,
                c1.apelido AS operador_cadastro,
                cli.data_modificacao,
                c2.apelido AS operador_modificacao
            FROM cliente.dados cli
            JOIN colaborador.dados c1
                ON c1.id = cli.operador_cadastro
            LEFT JOIN colaborador.dados c2
                ON c2.id = cli.operador_modificacao
            WHERE cli.id_cliente = %s'''

    cursor.execute(query, (id_cliente,))

    dados = cursor.fetchone()

    dados_cliente = {
            "id": dados[0],
            "rsoc": dados[1],
            "nome": dados[2],
            "cnpj": dados[3],
            "telefone": dados[4],
            "is_ativo": dados[5],
            "is_contrato": dados[6],
            "is_venda": dados[7],
            "data_cadastro": dados[8],
            "operador_cadastro": dados[9],
            "data_modificacao": dados[10],
            "operador_modificacao": dados[11]
    }

    connection.close()
    return dados_cliente