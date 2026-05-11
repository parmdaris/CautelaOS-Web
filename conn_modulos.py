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
                "logo_src": modulo[2],
                "cor_pri": modulo[3],
                "cor_sec": modulo[4],
                "cor_terc": modulo[5],
                "empresa": modulo[6]
            })

        return lista_modulos
    
    else:
        query = ''' SELECT * from modulos.dados where id = %s order by id ASC'''
        cursor.execute(query, id_modulo)
        modulo = cursor.fetchone()

        modulo_dados = {
                "id": modulo[0],
                "nome": modulo[1],
                "logo_src": modulo[2],
                "cor_pri": modulo[3],
                "cor_sec": modulo[4],
                "cor_terc": modulo[5],
                "empresa": modulo[6]
            }
        return modulo_dados
    