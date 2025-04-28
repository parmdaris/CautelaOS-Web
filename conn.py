import psycopg2 as pg
import configparser as cfgp
import os
import sys
import logging
import traceback
from datetime import datetime

config = cfgp.ConfigParser()
configFilePath = 'config.cfg'
logging.basicConfig(filename="c-os-w.log", level=logging.INFO, encoding='utf-8')
data_atual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

def gravarLog(tipo, texto_log): #########################################################################################
    if tipo == "e":
        logging.error(data_atual + ": " + texto_log)
    if tipo == "i":
        logging.info(data_atual + ": " + texto_log)
    if tipo == "w":
        logging.warning(data_atual + ": " + texto_log)

def criarConfig(): #########################################################################################

    config['db-config'] = {
        'database': 'DATABASE_NAME',
        'user': 'USER',
        'password': 'PASSWORD',
        'host-db': 'HOSTNAME',
        'port': 'PORT'
    }

    with open(configFilePath, 'w') as configfile: #Gerar um novo config.ini.
        config.write(configfile) #Gravar arquivo
        gravarLog("w", "config.cfg criado com valores padrão. É necessário realizar a configuração das informações sobre o banco de dados no arquivo.")
    
    sys.exit(1)

def dadosDB():
    if not os.path.exists(configFilePath):
        gravarLog("w", "Arquivo config.cfg não encontrado. Gerando novo arquivo...")
        criarConfig()

    config.read(configFilePath)

    return {
        'db_name': config['db-config']['database'],
        'db_user': config['db-config']['user'],
        'db_password': config['db-config']['password'],
        'host_db': config['db-config']['host-db'],
        'port': config['db-config']['port']
    }




def listaCautelas(): #########################################################################################
    infoDB = dadosDB()
    connection = pg.connect(   
        database= infoDB['db_name'], user= infoDB['db_user'], 
        password= infoDB['db_password'], host= infoDB['host_db'], port= infoDB['port']
    )

    connection.autocommit = True
    cursor = connection.cursor() 
    
    sql = '''select a.id_cautela, 
                    b.nome_cliente, 
                    a.data_cautela, 
                    a.qtd_itens, 
                    a.volumes 
                from cautela.dados as a 
                INNER JOIN cliente.dados as b
                    ON a.id_cliente = b.id_cliente 
                order by id_cautela desc;'''
    
    cursor.execute(sql) 
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
    infoDB = dadosDB()
    connection = pg.connect(   
        database= infoDB['db_name'], user= infoDB['db_user'], 
        password= infoDB['db_password'], host= infoDB['host_db'], port= infoDB['port']
    )

    connection.autocommit = True
    cursor = connection.cursor() 

    sql = '''select a.id_cautela,
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

    cursor.execute(sql, id_cautela) 
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
    infoDB = dadosDB()
    connection = pg.connect(   
        database= infoDB['db_name'], user= infoDB['db_user'], 
        password= infoDB['db_password'], host= infoDB['host_db'], port= infoDB['port']
    )

    connection.autocommit = True
    cursor = connection.cursor() 
    itens_cautela = []

    for i in range(1, qtd_itens + 1):
        sql = f'''
            select
                i.cod_item_{i}, 
                d.nome_item, 
                i.qtd_item_{i}
            from cautela.itens as i 
            inner join estoque.suprimentos as d 
                on i.cod_item_{i} = d.codigo 
            where i.id_cautela = %s
        '''
        cursor.execute(sql, (id_cautela,))
        row = cursor.fetchone()

        if row:
            itens_cautela.append({
                "codigo": row[0],
                "nome": row[1],
                "quantidade": row[2]
            })

    connection.close() 
    return itens_cautela

def getEstoque():
    infoDB = dadosDB()
    connection = pg.connect(   
        database= infoDB['db_name'], user= infoDB['db_user'], 
        password= infoDB['db_password'], host= infoDB['host_db'], port= infoDB['port']
    )

    connection.autocommit = True
    cursor = connection.cursor() 
    
    sql = '''select codigo, 
                    nome_item, 
                    qty, 
                    valor_unitario
                from estoque.suprimentos 
                order by codigo asc;'''
    
    cursor.execute(sql) 
    stream = cursor.fetchall()

    dados_estoque = [
    {
        "codigo_item": row[0],
        "descricao_item": row[1],
        "qtd_item": row[2],
        "valor_item": f"{row[3]:.2f}".replace(".",",") #Armazenar row[3] (valor) como uma string literal, com precisão de 2 décimos e trocando ponto por vírgula
    }
    for row in stream
    ]

    connection.close() 
    return dados_estoque

def getDadosItem(codigo_item):
    infoDB = dadosDB()
    connection = pg.connect(   
        database= infoDB['db_name'], user= infoDB['db_user'], 
        password= infoDB['db_password'], host= infoDB['host_db'], port= infoDB['port']
    )
    connection.autocommit = True
    cursor = connection.cursor() 
    
    sql = '''
            select codigo, 
                    nome_item, 
                    qty, 
                    valor_unitario,
                    ean_13
            from estoque.suprimentos 
            where codigo = %s
        '''
    
    cursor.execute(sql, (codigo_item,)) 
    stream = cursor.fetchone()

    dados_item = {
        "codigo_item": stream[0],
        "descricao_item": stream[1],
        "qtd_item": stream[2],
        "valor_item": f"{float(stream[3]):.2f}".replace(".", ","), 
        "ean_13": stream[4]
    }

    connection.close() 
    return dados_item

def valorEstoque():
    infoDB = dadosDB()
    connection = pg.connect(   
        database= infoDB['db_name'], user= infoDB['db_user'], 
        password= infoDB['db_password'], host= infoDB['host_db'], port= infoDB['port']
    )

    connection.autocommit = True
    cursor = connection.cursor() 
    
    sql = '''select qty, valor_unitario  
                from estoque.suprimentos;'''
    
    cursor.execute(sql) 
    stream = cursor.fetchall()

    valor = 0.0
    for item in stream:
        valor += item[0] * float(item[1])
    
    valor_total = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return valor_total


def qtdArtigos():
    infoDB = dadosDB()
    connection = pg.connect(   
        database= infoDB['db_name'], user= infoDB['db_user'], 
        password= infoDB['db_password'], host= infoDB['host_db'], port= infoDB['port']
    )

    connection.autocommit = True
    cursor = connection.cursor() 
    
    sql = '''select COUNT(*)  
                from estoque.suprimentos;'''
    
    cursor.execute(sql) 
    stream = cursor.fetchall()
    qtd_artigos = int(stream[0][0])
    return qtd_artigos

def alterarItemDB(codigo_item, descricao, valor, quantidade):
    try:
        infoDB = dadosDB()
        connection = pg.connect(   
        database= infoDB['db_name'], user= infoDB['db_user'], 
        password= infoDB['db_password'], host= infoDB['host_db'], port= infoDB['port']
    )
        valor_float = float(valor.replace(",", "."))
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE estoque.suprimentos
            SET nome_item = %s,
                valor_unitario = %s,
                qty = %s
            WHERE codigo = %s
        """, (descricao, valor_float, quantidade, codigo_item))
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Erro ao atualizar item: {e}")
        return 1
    return 0

def adicionarItemDB(codigo, descricao, valor, quantidade, ean):
    try:
        infoDB = dadosDB()
        connection = pg.connect(   
        database= infoDB['db_name'], user= infoDB['db_user'], 
        password= infoDB['db_password'], host= infoDB['host_db'], port= infoDB['port']
    )
        valor_float = float(valor.replace(",", "."))
        cursor = connection.cursor()
        cursor.execute("""
            insert into estoque.suprimentos 
                       (codigo, nome_item, qty, valor_unitario, ean_13) 
                       values (%s, %s, %s, %s, %s)
        """, (codigo, descricao, quantidade, valor_float, ean))
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Erro ao atualizar item: {e}")
        return 1
    return 0

def deletarItem(codigo_item):
    try:
        infoDB = dadosDB()
        connection = pg.connect(   
        database= infoDB['db_name'], user= infoDB['db_user'], 
        password= infoDB['db_password'], host= infoDB['host_db'], port= infoDB['port']
    )
        cursor = connection.cursor()
        cursor.execute("""
            delete from estoque.suprimentos 
                       where codigo = %s
        """, (codigo_item,))
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Erro ao atualizar item: {e}")
        return 1
    return 0