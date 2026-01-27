import psycopg2 as pg

def getClientes(dados_db):

    connection = pg.connect(   
        database= dados_db['db_name'], user= dados_db['db_user'], 
        password= dados_db['db_password'], host= dados_db['host_db'], port= dados_db['port']
    )
    connection.autocommit = True
    cursor = connection.cursor() 

    
    sql = '''
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



def getClientesVenda(dados_db):
      
    connection = pg.connect(   
        database= dados_db['db_name'], user= dados_db['db_user'], 
        password= dados_db['db_password'], host= dados_db['host_db'], port= dados_db['port']
    )
    connection.autocommit = True
    cursor = connection.cursor() 

    sql = '''
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
    
    cursor.execute(sql) 
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



def getClientesContrato(dados_db):
      
    connection = pg.connect(   
        database= dados_db['db_name'], user= dados_db['db_user'], 
        password= dados_db['db_password'], host= dados_db['host_db'], port= dados_db['port']
    )
    connection.autocommit = True
    cursor = connection.cursor() 

    sql = '''
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
    
    cursor.execute(sql) 
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