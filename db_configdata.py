import configparser as cfgp, os, sys, logging, psycopg2 as pg
from datetime import datetime

config = cfgp.ConfigParser()
configFilePath = 'config.cfg'

logging.basicConfig(filename="c-os-w.log", level=logging.INFO, encoding='utf-8')
data_atual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def conectarBanco():
    config.read(configFilePath)
    db = config['db-config']
    try:
        connection = pg.connect(
                        database=os.environ.get("DB_NAME", db.get('database')),
                        user=os.environ.get("DB_USER", db.get('user')),
                        password=os.environ.get("DB_PASSWORD", db.get('password')),
                        host=os.environ.get("DB_HOST", db.get('host-db')),
                        port=os.environ.get("DB_PORT", db.get('port'))
                        )
    except Exception as e:
        print(e)
        print("Falha na conexão! Contate o administrador do sistema.")
        return None
    
    return connection
        
   
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

