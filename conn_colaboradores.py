import psycopg2 as pg
from werkzeug.security import check_password_hash

def autenticar_usuario(dados_db, usuario, senha):
    conn = None
    cursor = None

    try:
        conn = pg.connect(
            database=dados_db['db_name'],
            user=dados_db['db_user'],
            password=dados_db['db_password'],
            host=dados_db['host_db'],
            port=dados_db['port']
        )

        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, senha_hash, nivel_acesso
            FROM colaborador.dados
            WHERE usuario = %s AND ativo = true
        """, (usuario,))

        resultado = cursor.fetchone()

        if not resultado:
            return None

        if check_password_hash(resultado[2], senha):
            return {
                "id": resultado[0],
                "nome": resultado[1],
                "nivel_acesso": resultado[3]
            }

        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
