from db_configdata import conectarBanco
from conn_estoque import decrementarItem
from psycopg2 import errors as pg_err

def registrarDadosVenda(dados_venda, id_operador):
    connection = None
    cursor = None

    try:
        connection = conectarBanco()

        query_dados_venda = """
            insert into venda.dados (
                id_cliente, 
                qtd_diversos, 
                qtd_total_itens, 
                valor_total, 
                data_venda,
                obs,
                operador
                ) values (%s, %s, %s, %s, NOW(), %s, %s)
                RETURNING id_venda;
        """
            
        cursor = connection.cursor()

        cursor.execute(query_dados_venda, (
            dados_venda.get('id_cliente'), 
            dados_venda.get('qtd_itens'), 
            dados_venda.get('qtd_total_itens'), 
            dados_venda.get('valor_total'), 
            dados_venda.get('obs'),
            id_operador
            )
        )

        id_venda = cursor.fetchone()[0]

        connection.commit()

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Erro ao gravar venda: {e}")
        return False
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return id_venda




def registrarItensVenda(id_venda, itens_venda):
    connection = None
    cursor = None

    try:
        connection = conectarBanco()

        query_item_venda = """
            insert into venda.itens (
                id_venda, 
                cod_item, 
                qtd_item, 
                valor_praticado
                ) values (%s, %s, %s, %s)
        """
            
        cursor = connection.cursor()

        for item in itens_venda:
            codigo = item.get('codigo')
            quantidade = item.get('quantidade')
            valor_praticado = item.get('valor_praticado')
            cursor.execute(query_item_venda, (
                id_venda,
                codigo, 
                quantidade,
                valor_praticado
                )
            )
            decrementarItem(codigo, quantidade)

        connection.commit()

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Erro ao gravar item: {e}")
        return 1
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return 0




def getQtyVendas(dias = 0):
    connection = None
    cursor = None

    try:
        connection = conectarBanco()

        connection.autocommit = True
        cursor = connection.cursor() 

        if dias != 0:
            sql = '''select COUNT(*)  
                from venda.dados where is_valida = true and data_venda::date >= CURRENT_DATE - %s;'''
            cursor.execute(sql, (dias,))
        else: 
            sql = '''select COUNT(*)  
                    from venda.dados where is_valida = true;'''
            cursor.execute(sql)
        
        row = cursor.fetchall()
        qtd_vendas = int(row[0][0])
        return qtd_vendas
    
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Erro ao gravar item: {e}")
        return 1
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()




def getListaVendas():
    connection = None
    cursor = None

    try:
        connection = conectarBanco()

        connection.autocommit = True
        cursor = connection.cursor()

        sql = '''SELECT v.id_venda, c.nome_fantasia, v.qtd_total_itens, v.valor_total, v.data_venda
                        FROM venda.dados v INNER JOIN cliente.dados c ON v.id_cliente = c.id_cliente ORDER BY v.id_venda DESC'''
        
        cursor.execute(sql)

        row = cursor.fetchall()

        lista_vendas = [
        {
            "id_venda": row[0],
            "destino": row[1],
            "qtd_total_itens": row[2],
            "valor_total": row[3],
            "data_venda": row[4]
        }
        for row in row
        ]

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Erro ao conectar! Causa:", e)
        return []

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return lista_vendas




def getValorVendas(dias = 0):
    connection = conectarBanco()

    connection.autocommit = True
    cursor = connection.cursor()

    if dias != 0:
        sql = '''select valor_total 
                    from venda.dados where is_valida = True and data_venda::date >= CURRENT_DATE - %s;'''
        cursor.execute(sql, (dias,))
    else:
        sql = '''select valor_total 
                    from venda.dados where is_valida = True;'''
        cursor.execute(sql)

    row = cursor.fetchall()

    valor = 0.0
    for item in row:
        valor += item[0]
    
    valor_total = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return valor_total