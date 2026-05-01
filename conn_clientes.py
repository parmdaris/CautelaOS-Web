from db_configdata import conectarBanco
from psycopg2 import errors as pg_err

def getClientes():

    connection = conectarBanco()
    connection.autocommit = True
    cursor = connection.cursor() 

    
    query = '''
        select id_cliente, 
        nome_cliente,
        nome_fantasia, 
        cnpj, 
        telefone_contato,
        is_ativo,
        is_contrato,
        is_venda
        from cliente.dados
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
            "telefone": row[4],
            "isAtivo": row[5],
            "isContrato": row[6],
            "isVenda": row[7]
        })

    connection.close() 
    return dados_clientes



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