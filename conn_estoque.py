from ativ_sistema import conectarBanco
from psycopg2 import errors as pg_err

def getEstoque(tipo_item = None, item_ativo = True, itens_criticos = False):
    connection = None
    cursor = None

    try:
        connection = conectarBanco()

        connection.autocommit = True
        cursor = connection.cursor()

        if tipo_item == "":
                tipo_item = None

        sql_start = '''select codigo, nome_item, tipo_suprimento, qty, valor_unitario, valor_atacado, 
                            is_ativo, limiar_alerta, qty_atacado
                        from estoque.suprimentos where is_ativo = %s'''
        sql_end = ''' order by codigo asc;''' 
        sql_tipo = ''' and tipo_suprimento = %s'''
        
        if tipo_item is None:
            sql = sql_start + sql_end
            cursor.execute(sql, (item_ativo,))

        else:
            sql = sql_start + sql_tipo + sql_end
            cursor.execute(sql, (item_ativo, tipo_item))


        row = cursor.fetchall()

        itens_estoque = [
        {
            "codigo": row[0],
            "descricao": row[1],
            "tipo": row[2],
            "qtd": row[3],
            "valor": f"{row[4]:.2f}".replace(".",","),
            "valor_atacado": f"{row[5]:.2f}".replace(".",","),
            "is_ativo": row[6],
            "limiar_alerta": row[7],
            "is_critico": False,
            "qtd_atacado": row[8]
        }
        for row in row
        ]

        for item in itens_estoque:
            if item['qtd'] <= item['limiar_alerta']:
                item['is_critico'] = True

        if itens_criticos == True:
            itens_criticos = []
            for item in itens_estoque:
                if item["is_critico"] == True:
                    itens_criticos.append(item)

            for item in itens_criticos:
                print(item['codigo'])

            return itens_criticos


    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Erro ao conectar!")
        print(e)
        return []

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return itens_estoque

def getTiposItens():
    connection = conectarBanco()
    connection.autocommit = True
    cursor = connection.cursor() 
    
    sql = '''
            select *
            from estoque.tipos_itens 
        '''
    
    cursor.execute(sql) 
    row = cursor.fetchall()

    tipo_item = [row[0] for row in row]

    connection.close() 

    return tipo_item




def getDadosItem(codigo_item):
    connection = conectarBanco()
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
                    obs,
                    limiar_alerta,
                    is_ativo

            from estoque.suprimentos 
            where codigo = %s
        '''
    
    cursor.execute(sql, (codigo_item,)) 
    row = cursor.fetchone()

    dados_item = {
        "codigo": row[0],
        "descricao": row[1],
        "qtd": row[2],
        "valor": f"{float(row[3]):.2f}".replace(".", ","), 
        "ean_13": row[4],
        "valor_atacado": f"{row[5]:.2f}".replace(".",","),
        "qty_atacado": row[6],
        "tipo_item": row[7],
        "subtipo": row[8],
        "subdescricao": row[9],
        "obs": row[10],
        "limiar_alerta": row[11],
        "is_ativo": row[12]
        
    }

    connection.close() 
    return dados_item



def decrementarItem(codigo_item, quantidade):
    try:
        connection = conectarBanco()

        query_decremento = """
            UPDATE estoque.suprimentos
            SET qty = qty - %s
            WHERE codigo = %s
        """
        cursor = connection.cursor()
        
        cursor.execute(query_decremento, (
            quantidade,
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

def incrementarItem(codigo_item, quantidade):
    try:
        connection = conectarBanco()

        query_incremento = """
            UPDATE estoque.suprimentos
            SET qty = qty + %s
            WHERE codigo = %s
        """
        cursor = connection.cursor()
        
        cursor.execute(query_incremento, (
            quantidade,
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


def valorEstoque(tipo_item = None):
    connection = conectarBanco()

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
                    from estoque.suprimentos where tipo_suprimento = %s and is_ativo = True;'''
        cursor.execute(sql, (tipo_item,))

    row = cursor.fetchall()

    valor = 0.0
    for item in row:
        valor += item[0] * float(item[1])
    
    valor_total = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return valor_total




def qtdArtigos(tipo_item = None, criticos=False, ativos = True):
    connection = conectarBanco()

    connection.autocommit = True
    cursor = connection.cursor() 

    if tipo_item == "":
            tipo_item = None
    
    if tipo_item is None:
        sql = '''select COUNT(*)  
                from estoque.suprimentos where is_ativo = %s;'''
        cursor.execute(sql, (ativos,))
    else:
        sql = '''select COUNT(*)  
                    from estoque.suprimentos item where item.tipo_suprimento = %s and item.is_ativo = %s;'''
        cursor.execute(sql, (tipo_item, ativos))
    
    row = cursor.fetchall()
    qtd_artigos = int(row[0][0])
    return qtd_artigos


def countArtigosCriticos():
    connection = conectarBanco()

    connection.autocommit = True
    cursor = connection.cursor() 

    sql = '''select COUNT(*)  
                from estoque.suprimentos item where item.qty < item.limiar_alerta
                and item.is_ativo = True
                '''
    cursor.execute(sql)
    
    criticos = cursor.fetchone()[0]
    return criticos



def alterarItemDB(dados_item, codigo_item, id_operador):
    try:
        connection = conectarBanco()
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
                obs = %s,
                limiar_alerta = %s,
                data_modificacao = NOW(),
                operador_modificacao = %s
            WHERE codigo = %s
        """

        cursor = connection.cursor()

        if dados_item.get('subtipo') is None:
            subtipo = ""
        else:
            subtipo = dados_item.get('subtipo')

        if dados_item.get('subdescricao') is None:
            subdescricao = ""
        else:
            subdescricao = dados_item.get('subdescricao')
        if dados_item.get('obs') is None:
            obs = ""
        else:
            obs = dados_item.get('obs')
        
        cursor.execute(query_edit, (
            dados_item.get('novo_codigo'), 
            dados_item.get('descricao'), 
            valor_float, 
            dados_item.get('tipo_item'),
            dados_item.get('quantidade'), 
            dados_item.get('ean_13'), 
            valor_float_atac, 
            dados_item.get('qty_atacado'), 
            subtipo, 
            subdescricao, 
            obs,
            dados_item.get('limiar_alerta'),
            id_operador,
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



def adicionarItemDB(dados_item, id_operador):
    connection = None
    cursor = None

    try:
        connection = conectarBanco()
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
                obs,
                limiar_alerta,
                operador_cadastro
                ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            dados_item.get('obs'),
            dados_item.get('limiar_alerta'),
            id_operador
            )
        )

        connection.commit()

    except pg_err.UniqueViolation:
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


def definirAtivo(operador, codigo_item, ativar = bool):
    try:
        connection = conectarBanco()
        cursor = connection.cursor()

        cursor.execute("""
            update estoque.suprimentos 
                       set is_ativo = %s
                       where codigo = %s
        """, (ativar, codigo_item))
        connection.commit()
        cursor.close()
        connection.close()

        traceModificacao(operador, codigo_item)
    except Exception as e:
        print(f"Erro ao atualizar item: {e}")
        return 1
    return 0




def deletarItem(codigo_item):
    try:
        connection = conectarBanco()
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



def traceModificacao(u_id, codigo_item):
    try:
        with conectarBanco() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE estoque.suprimentos SET data_modificacao = NOW(), operador_modificacao = %s WHERE codigo = %s",
                    (u_id, codigo_item)
                )
    except Exception as e:
        print(f"Erro ao atualizar traceback de modificações: {e}")


