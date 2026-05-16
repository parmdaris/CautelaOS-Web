from ativ_sistema import conectarBanco
from psycopg2 import errors as pg_err

def listaCautelas(): #########################################################################################
    connection = conectarBanco()

    connection.autocommit = True
    cursor = connection.cursor() 
    
    query = '''select a.id_cautela, 
                    b.nome_cliente, 
                    a.data_cautela, 
                    a.qtd_itens, 
                    a.volumes 
                from cautela.dados as a 
                INNER JOIN cliente.dados as b
                    ON a.id_cliente = b.id_cliente 
                order by id_cautela desc;'''
    
    cursor.execute(query) 
    stream = cursor.fetchall()

    dados = [
    {
        "id_cautela": row[0],
        "nome_cliente": row[1],
        "data_cautela": row[2].strftime("%d/%m/%Y"),  # formata a data
        "qtd_itens": row[3],
        "volumes": row[4]
    }
    for row in stream
    ]

    connection.close() 
    return dados
    


def getDadosCautela(id_cautela): #########################################################################################
    connection = conectarBanco()

    connection.autocommit = True
    cursor = connection.cursor() 

    query = '''select a.id_cautela,
                    b.nome_cliente, 
                    a.data_cautela, 
                    a.qtd_itens, 
                    a.volumes, 
                    a.obs_cautela, 
                    a.receptor 
                from cautela.dados as a 
                INNER JOIN cliente.dados as b
                    ON a.id_cliente = b.id_cliente 
                where a.id_cautela = %s 
                order by id_cautela asc;'''

    cursor.execute(query, id_cautela) 
    stream = cursor.fetchone()

    if stream:
        detalhe_dados_cautela = {
            "id_cautela": stream[0],
            "nome_cliente": stream[1],
            "data_cautela": stream[2].strftime("%Y/%m/%d"),
            "qtd_itens": stream[3],
            "volumes": stream[4],
            "obs_cautela": stream[5],
            "receptor": stream[6],
            "materiais": []  # você pode preencher isso se quiser os materiais também
        }
    else:
        detalhe_dados_cautela = {}

    connection.close() 
    return detalhe_dados_cautela


def getItensCautela(id_cautela, qtd_itens): #########################################################################################
    connection = conectarBanco()

    connection.autocommit = True
    cursor = connection.cursor() 
    itens_cautela = []

    for i in range(1, qtd_itens + 1):
        query = f'''
            select
                i.cod_item_{i}, 
                d.nome_item, 
                i.qtd_item_{i}
            from cautela.itens as i 
            inner join estoque.suprimentos as d 
                on i.cod_item_{i} = d.codigo 
            where i.id_cautela = %s
        '''
        cursor.execute(query, (id_cautela,))
        row = cursor.fetchone()

        if row:
            itens_cautela.append({
                "codigo": row[0],
                "nome": row[1],
                "quantidade": row[2]
            })

    connection.close() 
    return itens_cautela

def qtdCautelas():
    connection = conectarBanco()
    connection.autocommit = True
    cursor = connection.cursor() 
    
    query = '''select COUNT(*) from cautela.dados;'''
    
    cursor.execute(query) 
    stream = cursor.fetchone()
    qtd_artigos = int(stream[0])
    return qtd_artigos