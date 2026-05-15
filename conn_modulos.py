from db_configdata import conectarBanco
from psycopg2 import errors as pg_err
from flask import session

def getModulos(id_modulo = None):
    connection = None
    cursor = None

    connection = conectarBanco()
    connection.autocommit = True
    cursor = connection.cursor()

    if id_modulo == None:

        query = ''' SELECT * from modulos.dados order by id ASC'''

        cursor.execute(query)
        modulos = cursor.fetchall()

        lista_modulos = []

        for modulo in modulos:
            lista_modulos.append({
                "id": modulo[0],
                "nome": modulo[1],
                "splash_src": "modulos/splash/" + str(modulo[0]) + ".png",
                "logo_src": "modulos/logo/" + str(modulo[0]) + ".png",
                "cor_pri": modulo[3],
                "cor_sec": modulo[4],
                "cor_terc": modulo[5],
                "empresa": modulo[6]
            })
        return lista_modulos
    
    else:
        query = ''' SELECT * from modulos.dados where id = %s order by id ASC'''
        cursor.execute(query, (id_modulo,))
        dados = cursor.fetchone()

        modulo = {
                "id": dados[0],
                "nome": dados[1],
                "empresa": dados[6],

                "img_src": {
                    "splash_src": "modulos/splash/" + str(dados[0]) + ".png",
                    "logo_src": "modulos/logo/" + str(dados[0]) + ".png",
                },

                "cores": {
                    "primaria": dados[3],
                    "secundaria": dados[4],
                    "terciaria": dados[5],
                    "texto_barra": cor_texto(dados[3])
                },

                "macrofuncoes": getMacrofuncoes(cursor, dados[0])
            }
        
        print(modulo["macrofuncoes"])

        return modulo
    

    
def cor_texto(hexcolor):
    hexcolor = hexcolor.replace("#", "")

    r = int(hexcolor[0:2], 16)
    g = int(hexcolor[2:4], 16)
    b = int(hexcolor[4:6], 16)

    luminancia = (0.299*r + 0.587*g + 0.114*b)

    return "#000000" if luminancia > 180 else "#cfd8dc"



def getMacrofuncoes(cursor, id_modulo):
    query = '''select mf.nome as funcao from modulos.macrofuncoes_modulo mfunc
                    join modulos.dados mod on mod.id = mfunc.id_modulo 
                    join sistema.macrofuncoes mf on mf.id = mfunc.id_macrofuncao where mod.id = %s
                    order by mf.nome ASC'''
    cursor.execute(query, (id_modulo,))
    return [p[0] for p in cursor.fetchall()]



def verificarAcesso(id_usuario):

    connection = conectarBanco()
    cursor = connection.cursor()

    query = '''
        SELECT acesso_modulo
        FROM modulos.permissao_modulos
        WHERE id_usuario = %s
    '''

    cursor.execute(query, (id_usuario,))

    modulos_usuario = [m[0] for m in cursor.fetchall()]

    connection.close()

    return modulos_usuario
