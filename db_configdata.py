import configparser as cfgp, os, sys, logging, psycopg2 as pg
from datetime import datetime

config = cfgp.ConfigParser()
configFilePath = 'config.cfg'

logging.basicConfig(filename="c-os-w.log", level=logging.INFO, encoding='utf-8')
data_atual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def conectarBanco():
    config.read(configFilePath)
    db = config['db-config']

    return pg.connect(
                    database=db['database'], 
                    user=db['user'], 
                    password=db['password'], 
                    host=db['host-db'], 
                    port=db['port']
                    )


   
def inicializarCfg():
    if not os.path.exists(configFilePath):
        gravarLog("w", "Arquivo config.cfg não encontrado. Gerando novo arquivo...")
        criarConfig()

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

