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
                order by codigo desc;'''
    
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