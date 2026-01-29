import psycopg2 as pg

def getEstoque(dados_db, tipo_item = None):
    connection = None
    cursor = None

    try:
        connection = pg.connect(   
            database= dados_db['db_name'], user= dados_db['db_user'], 
            password= dados_db['db_password'], host= dados_db['host_db'], port= dados_db['port']
        )

        connection.autocommit = True
        cursor = connection.cursor()

        if tipo_item == "":
                tipo_item = None
        
        if tipo_item is None:
            
            sql = '''select codigo, 
                            nome_item,
                            tipo_suprimento, 
                            qty, 
                            valor_unitario,
                            valor_atacado,
                            qty_atacado,
                            subtipo,
                            subdescricao,
                            obs
                        from estoque.suprimentos 
                        order by codigo asc;'''
            
            cursor.execute(sql)
        else:
            sql = '''select codigo, 
                            nome_item,
                            tipo_suprimento, 
                            qty, 
                            valor_unitario,
                            valor_atacado,
                            qty_atacado,
                            subtipo, 
                            subdescricao,
                            obs
                        from estoque.suprimentos where tipo_suprimento = %s 
                        order by codigo asc;'''
            
            cursor.execute(sql, (tipo_item,))


        stream = cursor.fetchall()

        itens_estoque = [
        {
            "codigo": row[0],
            "descricao": row[1],
            "tipo": row[2],
            "qtd": row[3],
            "valor": f"{row[4]:.2f}".replace(".",","),
            "valor_atacado": f"{row[5]:.2f}".replace(".",","),
            "qty_atacado": row[6],
            "subtipo": row[7],
            "subdescricao": row[8],
            "observacoes": row[9]
        }
        for row in stream
        ]

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Erro ao conectar!")
        
        
        return 1

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return itens_estoque

def getTiposItens(dados_db):
    connection = pg.connect(   
        database= dados_db['db_name'], user= dados_db['db_user'], 
        password= dados_db['db_password'], host= dados_db['host_db'], port= dados_db['port']
    )
    connection.autocommit = True
    cursor = connection.cursor() 
    
    sql = '''
            select *
            from estoque.tipos_itens 
        '''
    
    cursor.execute(sql) 
    stream = cursor.fetchall()

    tipo_item = [row[0] for row in stream]

    connection.close() 

    return tipo_item




def getDadosItem(dados_db, codigo_item):
    connection = pg.connect(   
        database= dados_db['db_name'], user= dados_db['db_user'], 
        password= dados_db['db_password'], host= dados_db['host_db'], port= dados_db['port']
    )
    connection.autocommit = True
    cursor = connection.cursor() 
    
    sql = '''
            select codigo, 
                    nome_item, 
                    qty, 
                    valor_unitario,
                    ean_13,
                    valor_atacado,
                    qty_atacado,
                    tipo_suprimento,
                    subtipo,
                    subdescricao,
                    obs

            from estoque.suprimentos 
            where codigo = %s
        '''
    
    cursor.execute(sql, (codigo_item,)) 
    stream = cursor.fetchone()

    dados_item = {
        "codigo": stream[0],
        "descricao": stream[1],
        "qtd": stream[2],
        "valor": f"{float(stream[3]):.2f}".replace(".", ","), 
        "ean_13": stream[4],
        "valor_atacado": f"{stream[5]:.2f}".replace(".",","),
        "qty_atacado": stream[6],
        "tipo_item": stream[7],
        "subtipo": stream[8],
        "subdescricao": stream[9],
        "obs": stream[10]
        
    }

    connection.close() 
    return dados_item




def valorEstoque(dados_db, tipo_item = None):
    connection = pg.connect(   
        database= dados_db['db_name'], user= dados_db['db_user'], 
        password= dados_db['db_password'], host= dados_db['host_db'], port= dados_db['port']
    )

    connection.autocommit = True
    cursor = connection.cursor() 

    if tipo_item == "":
            tipo_item = None

    if tipo_item is None:
        sql = '''select qty, valor_unitario  
                    from estoque.suprimentos;'''
        cursor.execute(sql) 
    else:
        sql = '''select qty, valor_unitario  
                    from estoque.suprimentos where tipo_suprimento = %s;'''
        cursor.execute(sql, (tipo_item,))

    stream = cursor.fetchall()

    valor = 0.0
    for item in stream:
        valor += item[0] * float(item[1])
    
    valor_total = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return valor_total




def qtdArtigos(dados_db, tipo_item = None):
    connection = pg.connect(   
        database= dados_db['db_name'], user= dados_db['db_user'], 
        password= dados_db['db_password'], host= dados_db['host_db'], port= dados_db['port']
    )

    connection.autocommit = True
    cursor = connection.cursor() 

    if tipo_item == "":
            tipo_item = None
    
    if tipo_item is None:
        sql = '''select COUNT(*)  
                from estoque.suprimentos;'''
        cursor.execute(sql)
    else:
        sql = '''select COUNT(*)  
                    from estoque.suprimentos where tipo_suprimento = %s;'''
        cursor.execute(sql, (tipo_item,))
    
    stream = cursor.fetchall()
    qtd_artigos = int(stream[0][0])
    return qtd_artigos


def countArtigosCriticos(dados_db):
    connection = pg.connect(   
        database= dados_db['db_name'], user= dados_db['db_user'], 
        password= dados_db['db_password'], host= dados_db['host_db'], port= dados_db['port']
    )

    connection.autocommit = True
    cursor = connection.cursor() 

    sql = '''select COUNT(*)  
                from estoque.suprimentos where qty < 10;'''
    cursor.execute(sql)
    
    criticos = cursor.fetchone()[0]
    return criticos



def alterarItemDB(dados_db, dados_item, codigo_item):
    try:
        infoDB = dados_db
        connection = pg.connect(   
        database= infoDB['db_name'], user= infoDB['db_user'], 
        password= infoDB['db_password'], host= infoDB['host_db'], port= infoDB['port']
    )
        valor_float = moeda_para_float(dados_item.get('valor'))
        valor_float_atac = moeda_para_float(dados_item.get('valor_atacado'))

        query_edit = """
            UPDATE estoque.suprimentos
            SET codigo = %s,
                nome_item = %s,
                valor_unitario = %s,
                tipo_suprimento = %s,
                qty = %s,
                ean_13 = %s,
                valor_atacado = %s,
                qty_atacado = %s,
                subtipo = %s,
                subdescricao = %s,
                obs = %s
            WHERE codigo = %s
        """

        cursor = connection.cursor()
        
        cursor.execute(query_edit, (
            dados_item.get('novo_codigo'), 
            dados_item.get('descricao'), 
            valor_float, 
            dados_item.get('tipo_item'),
            dados_item.get('quantidade'), 
            dados_item.get('ean_13'), 
            valor_float_atac, 
            dados_item.get('qty_atacado'), 
            dados_item.get('subtipo'), 
            dados_item.get('subdescricao'), 
            dados_item.get('obs'), 
            codigo_item
            )
        )

        connection.commit()

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Erro ao atualizar item: {e}")
        return 1
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return 0



def moeda_para_float(valor):
    if not valor:
        return 0.0

    valor = valor.replace('R$', '').strip()
    valor = valor.replace('.', '').replace(',', '.')
    return float(valor)



def adicionarItemDB(dados_db, dados_item):
    connection = None
    cursor = None

    try:
        connection = pg.connect(   
        database= dados_db['db_name'], user= dados_db['db_user'], 
        password= dados_db['db_password'], host= dados_db['host_db'], port= dados_db['port']
    )
        valor_float = moeda_para_float(dados_item.get('valor'))
        valor_float_atac = moeda_para_float(dados_item.get('valor_atacado'))

        query_add = """
            insert into estoque.suprimentos (
                codigo, 
                nome_item, 
                qty, 
                tipo_suprimento, 
                valor_unitario, 
                ean_13, 
                valor_atacado, 
                qty_atacado, 
                subtipo, 
                subdescricao, 
                obs
                ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
            
        cursor = connection.cursor()

        cursor.execute(query_add, (
            dados_item.get('codigo'), 
            dados_item.get('descricao'), 
            dados_item.get('quantidade'), 
            dados_item.get('tipo'), 
            valor_float, 
            dados_item.get('ean_13'), 
            valor_float_atac, 
            dados_item.get('qtd_atacado'), 
            dados_item.get('subtipo'), 
            dados_item.get('subdescricao'), 
            dados_item.get('obs')
            )
        )

        connection.commit()

    except pg.errors.UniqueViolation:
        if connection:
            connection.rollback()
        return "SKU_DUPLICADO"

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Erro ao atualizar item: {e}")
        return False
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return True




def deletarItem(dados_db, codigo_item):
    try:
        connection = pg.connect(   
        database= dados_db['db_name'], user= dados_db['db_user'], 
        password= dados_db['db_password'], host= dados_db['host_db'], port= dados_db['port']
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






