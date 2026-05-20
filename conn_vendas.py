from ativ_sistema import conectarBanco
from conn_estoque import decrementarItem
from psycopg2 import errors as pg_err
from flask import session

def registrarDadosVenda(dados_venda, id_operador):
    connection = None
    cursor = None

    try:
        connection = conectarBanco()

        query_dados_venda = """
            insert into venda.dados (
                id_cliente, 
                vendedor,
                qtd_diversos, 
                qtd_total_itens, 
                valor_total, 
                data_venda,
                obs,
                operador
                ) values (%s, %s, %s, %s, %s, NOW(), %s, %s)
                RETURNING id_venda;
        """
            
        cursor = connection.cursor()

        print(dados_venda["vendedor"])

        cursor.execute(query_dados_venda, (
            dados_venda.get('id_cliente'), 
            dados_venda.get('vendedor'),
            dados_venda.get('qtd_itens'), 
            dados_venda.get('qtd_total_itens'), 
            dados_venda.get('valor_total'), 
            dados_venda.get('obs'),
            id_operador
            )
        )

        id_venda = cursor.fetchone()[0]

        registrarVendaModulo(cursor, id_venda, session.get("modulo").get("id"))

        connection.commit()

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Erro ao gravar venda: {e}")
        raise
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return id_venda


def registrarVendaModulo(cursor, id_venda, id_modulo):
    query = '''insert into venda.vendas_modulos (id_venda, id_modulo) values (%s, %s)'''
    cursor.execute(query, (id_venda, id_modulo))


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
        raise
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return 0




def getQtyVendas(intervalo_dias = 0, todas = False, id_modulo = None):
    connection = None
    cursor = None

    try:
        connection = conectarBanco()
        connection.autocommit = True
        cursor = connection.cursor() 

        if id_modulo == 1:
            query_base = "SELECT COUNT(*) from venda.dados"
            validas = " where is_valida = true"
            intervalo = " and data_venda >= CURRENT_DATE - %s"

            if intervalo_dias > -1:
                sql = query_base + validas + intervalo
                cursor.execute(sql, (intervalo_dias,))
            else: 
                if todas:
                    sql = query_base
                else:
                    sql = query_base + validas
                cursor.execute(sql)
        
        else:
            query_base = '''SELECT COUNT(*) from venda.dados v
                            JOIN venda.vendas_modulos vm on v.id_venda = vm.id_venda
                            where vm.id_modulo = %s
                            '''
            validas = " and is_valida = true"
            intervalo = " and data_venda >= CURRENT_DATE - %s"

            if intervalo_dias > -1:
                sql = query_base + validas + intervalo
                cursor.execute(sql, (id_modulo, intervalo_dias))
            else: 
                if todas:
                    sql = query_base
                else:
                    sql = query_base + validas
                cursor.execute(sql, (id_modulo,))

        
        
        row = cursor.fetchall()
        qtd_vendas = int(row[0][0])
        return qtd_vendas
    
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Erro ao gravar item: {e}")
        raise
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()




def getListaVendas(id_modulo = None):
    connection = None
    cursor = None

    try:
        connection = conectarBanco()

        connection.autocommit = True
        cursor = connection.cursor()

        if id_modulo == None:
            return []

        if id_modulo == 1:

            sql = '''SELECT v.id_venda, c.nome_fantasia, v.qtd_total_itens, v.valor_total, v.data_venda, col.apelido as vendedor
                            FROM venda.dados v INNER JOIN cliente.dados c ON v.id_cliente = c.id_cliente
                            inner join colaborador.dados col on v.vendedor = col.id
                            ORDER BY v.id_venda DESC'''
            
            cursor.execute(sql)
        else:
            sql = '''SELECT v.id_venda, c.nome_fantasia, v.qtd_total_itens, v.valor_total, v.data_venda, col.apelido as vendedor
                        FROM venda.dados v INNER JOIN cliente.dados c ON v.id_cliente = c.id_cliente
                        inner join colaborador.dados col on v.vendedor = col.id
                        left join venda.vendas_modulos vm on vm.id_venda = v.id_venda
                        where vm.id_modulo = %s
                        ORDER BY v.id_venda DESC'''
        
            cursor.execute(sql, (id_modulo,))

        row = cursor.fetchall()

        lista_vendas = [
        {
            "id_venda": row[0],
            "destino": row[1],
            "qtd_total_itens": row[2],
            "valor_total": row[3],
            "data_venda": row[4],
            "vendedor": row[5]
        }
        for row in row
        ]

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Erro ao conectar! Causa:", e)
        raise

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return lista_vendas


def getDadosVenda(id_venda):
    connection = conectarBanco()
    connection.autocommit = True
    cursor = connection.cursor()

    sql = '''select v.id_venda, v.id_cliente, c.nome_fantasia as nome_cliente, v.qtd_diversos, v.qtd_total_itens,
     v.valor_total, v.data_venda, v.receptor, v.obs, col_op.apelido as operador, col_opmod.apelido as operador_modificacao, v.data_modificacao, v.is_valida,
      ven_mpg.descricao_meio as forma_pgto, col_vend.apelido as vendedor from venda.dados v 
      inner join cliente.dados c on v.id_cliente = c.id_cliente
      inner join colaborador.dados col_vend on v.vendedor = col_vend.id
      inner join colaborador.dados col_op on v.operador = col_op.id
      inner join venda.tipos_pgto ven_mpg on v.forma_pgto = ven_mpg.id_meio
      left join colaborador.dados col_opmod on v.operador_modificacao = col_opmod.id
      where id_venda = %s
            '''
    cursor.execute(sql, (id_venda,))

    dados_venda = cursor.fetchone()

    sql = '''select v.cod_item, v.qtd_item, v.valor_praticado, e.nome_item from venda.itens v
                inner join estoque.suprimentos e on v.cod_item = e.codigo where id_venda = %s;
            '''
    cursor.execute(sql, (id_venda,))

    itens_venda = cursor.fetchall()

    if dados_venda[11]:
        data_mod = dados_venda[11].strftime("%d/%m/%Y")
    else:
        data_mod = "-"

    dados = {
        "id_venda": dados_venda[0],
        "id_cliente": dados_venda[1],
        "nome_cliente": dados_venda[2],
        "qtd_diversos": dados_venda[3],
        "qtd_total_itens": dados_venda[4],
        "valor_total": dados_venda[5],
        "data_venda": dados_venda[6].strftime("%d/%m/%Y"),
        "receptor": dados_venda[7],
        "observacoes": dados_venda[8],
        "operador": dados_venda[9],
        "operador_modificacao": dados_venda[10],
        "data_modificacao": data_mod,
        "is_valida": dados_venda[12],
        "forma_pgto": dados_venda[13],
        "vendedor": dados_venda[14]
    }

    itens = []

    for i in itens_venda:
        itens.append(
            {
                "cod_item": i[0],
                "qtd_item": i[1],
                "valor_praticado": i[2],
                "descricao": i[3]
            }
        )


    return [dados, itens]




def getValorVendas(intervalo_dias = 0, vendas_validas = True, id_modulo = None):
    connection = conectarBanco()

    connection.autocommit = True
    cursor = connection.cursor()

    if id_modulo == 1:
        query_base = '''SELECT SUM(valor_total) from venda.dados'''
        validas = " where is_valida = true"
        intervalo = " and data_venda >= CURRENT_DATE - %s"
        if intervalo_dias > -1:
            sql = query_base + validas + intervalo
            cursor.execute(sql, (intervalo_dias,))
        else: 
            if vendas_validas:
                sql = query_base + validas
            else:
                sql = query_base

            cursor.execute(sql)
    else:
        query_base = '''SELECT SUM(valor_total) from venda.dados v
                        join venda.vendas_modulos vm on v.id_venda = vm.id_venda 
                        where vm.id_modulo = %s'''
        validas = " and is_valida = true"
        intervalo = " and data_venda >= CURRENT_DATE - %s"

        if intervalo_dias > -1:
            sql = query_base + validas + intervalo
            cursor.execute(sql, (id_modulo, intervalo_dias))
        else: 
            if vendas_validas:
                sql = query_base + validas
            else:
                sql = query_base

            cursor.execute(sql, (id_modulo,))

    valor = cursor.fetchone()[0]

    if valor == None:
        valor = 0
    
    valor_total = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return valor_total