import configparser as cfgp
import os
import sys
import logging
from datetime import datetime

config = cfgp.ConfigParser()
configFilePath = 'config.cfg'
logging.basicConfig(filename="c-os-w.log", level=logging.INFO, encoding='utf-8')
data_atual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def dados():
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





def gravarLog(tipo, texto_log): #########################################################################################
    if tipo == "e":
        logging.error(data_atual + ": " + texto_log)
    if tipo == "i":
        logging.info(data_atual + ": " + texto_log)
    if tipo == "w":
        logging.warning(data_atual + ": " + texto_log)

