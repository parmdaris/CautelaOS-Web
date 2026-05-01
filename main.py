from flask import Flask, url_for, render_template, request, redirect, session
from conn_auth import login_requerido, acesso_requerido, gerarSenhaHash, tem_acesso, checarSenhaHash
from db_configdata import inicializarCfg
from conn_estoque import moeda_para_float
import conn_cautelas as cautelas, conn_clientes as clientes, conn_estoque as estoque, conn_vendas as vendas
import conn_colaboradores as usuarios, datetime, json

data_iso = datetime.datetime.now().date().strftime("%Y-%m-%d %H:%M:%S")
data = datetime.datetime.now().date().strftime("%d/%m/%Y")
hora = datetime.datetime.now().time().strftime("%H:%M:%S")


def iniciarIndex():

    app = Flask(__name__)
    app.secret_key = "cautelaos"
    app.jinja_env.globals.update(tem_acesso=tem_acesso)

    #app.secret_key = os.environ.get("SECRET_KEY", "cautelaos-secret")

################################################################################# Dashboard, login e logout

    @app.route('/')
    @login_requerido
    def dashboard():

        valor_estoque = estoque.valorEstoque()
        qtd_itens = estoque.qtdArtigos()
        criticos = estoque.countArtigosCriticos()
        valor_total_hoje = vendas.getValorVendas(1)
        qtd_vendas_hoje = vendas.getQtyVendas(1)

        return render_template('dashboard.html', 
                               valor_estoque=valor_estoque, 
                               qtd_itens=qtd_itens, 
                               criticos=criticos, 
                               valor_total_hoje=valor_total_hoje,
                               qtd_vendas_hoje=qtd_vendas_hoje
                               )
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            usuario = request.form["usuario"]
            senha = request.form["senha"]

            user = usuarios.autenticar_usuario(usuario, senha)

            if user:
                session["u_id"] = user["id"]
                session["u_apelido"] = user["apelido"]
                session["nivel_acesso"] = user["id_acesso"]
                session["cargo"] = user["cargo"]
                session["u_primeiro_acesso"] = user["primeiro_acesso"]
                usuarios.ultimoLogin(user['id'])
                
                if user["primeiro_acesso"] == True:
                    return redirect(url_for("acesso_inicial"))
                else:
                    return redirect(url_for("dashboard"))

            return render_template("login.html", erro="Usuário ou senha inválidos")

        return render_template("login.html")

    @app.route("/logout", methods=["POST"])
    @login_requerido
    def logout():
        session.clear()
        return redirect(url_for("login"))
    

    @app.route("/start", methods=["POST", "GET"])
    @login_requerido
    def acesso_inicial():
        if request.method == "POST":
            senha_inserida = request.form["senha"]

            if usuarios.compararSenhaHash(session["u_id"], senha_inserida):
                return render_template("start.html", erro="A senha deve ser diferente da atual")
            
            usuarios.contaIniciada(session["u_id"], gerarSenhaHash(senha_inserida))
            return redirect(url_for("dashboard"))
        
        return render_template("start.html", usuario = session["u_apelido"])


################################################################################# Cautelas


    @app.route("/cautelas/")
    @login_requerido
    def listar_cautelas():
        lista_cautelas = cautelas.listaCautelas()
        qtd_cautelas = cautelas.qtdCautelas()
        return render_template('cautela/visualizar_lista_cautelas.html', dados=lista_cautelas, qtd=qtd_cautelas)

    @app.route("/cautela/nova")
    @login_requerido
    def nova_cautela():
        return render_template('cautela/adicionar_cautela.html')

    @app.route('/cautelas/<id_cautela>')
    @login_requerido
    def ver_cautela(id_cautela):
        detalhe_dados = cautelas.getDadosCautela(id_cautela)
        itens_cautela = cautelas.getItensCautela(id_cautela, detalhe_dados["qtd_itens"])
        return render_template("cautela/visualizar_cautela.html", itens_cautela=itens_cautela, **detalhe_dados)

    @app.route("/cautelas/<id_cautela>/print")
    @login_requerido
    def imprimir_cautela(id_cautela):
        detalhe_dados = cautelas.getDadosCautela(id_cautela)
        itens_cautela = cautelas.getItensCautela(id_cautela, detalhe_dados["qtd_itens"])
        return render_template('cautela/template_print_cautela.html', itens_cautela=itens_cautela, **detalhe_dados)


################################################################################# Estoque


    @app.route("/estoque")
    @login_requerido
    def ver_estoque():
        tipos = estoque.getTiposItens()
        dados_estoque = estoque.getEstoque()
        valor_estoque = estoque.valorEstoque()
        qtd_artigos = estoque.qtdArtigos()
        return render_template('estoque/visualizar_lista_estoque.html', 
                               dados_estq=dados_estoque, 
                               valor_estoque=valor_estoque, 
                               qtd_artigos=qtd_artigos,
                               tipos_itens=tipos
                               )
    


    @app.route("/estoque/inativos")
    @login_requerido
    def ver_itens_inativos():
        tipos = estoque.getTiposItens()
        dados_estoque = estoque.getEstoque(None, False)
        qtd_artigos_inativos = estoque.qtdArtigos(None, False)
        return render_template('estoque/visualizar_lista_inativos.html', 
                               dados_estq=dados_estoque, 
                               qtd_artigos=qtd_artigos_inativos,
                               tipos_itens=tipos
                               )

    
    @app.route("/estoque/<codigo_item>/ver")
    @login_requerido
    def ver_item_estoque(codigo_item):
        dados_item = estoque.getDadosItem(codigo_item)
        return render_template('estoque/ver_item_estoque.html', dados_item=dados_item)
    
    @app.route('/estoque/adicionar_item', methods=['GET', 'POST'])
    @login_requerido
    def adicionarItem():

        if request.method == 'POST':
            dados_item = request.form.to_dict()
            acao = dados_item.get('acao')

            salvar_item = estoque.adicionarItemDB(dados_item, session["u_id"])

            if salvar_item == "SKU_DUPLICADO":
                return redirect(url_for('adicionarItem', erro='sku_existente'))
            if salvar_item is False:
                return redirect(url_for('adicionarItem', erro='erro_geral'))
            
            if acao == 'salvar_outro':
                return redirect(url_for('adicionarItem'))
            
            return redirect(url_for('ver_estoque'))
        
        tiposItens = estoque.getTiposItens()
        return render_template('estoque/adicionar_item_estoque.html', tiposItens=tiposItens)
    
    @app.route('/estoque/editar_item/<codigo_item>', methods=['POST', 'GET'])
    @login_requerido
    def alterarItem(codigo_item):
        if request.method == 'POST':
            dados_item = request.form.to_dict()
            estoque.alterarItemDB(dados_item, codigo_item=codigo_item, id_operador=session["u_id"])
            codigo_item = dados_item.get('novo_codigo')
            return redirect(url_for('ver_item_estoque', codigo_item=codigo_item))
        
        tiposItens = estoque.getTiposItens()
        dados_item = estoque.getDadosItem(codigo_item)
        return render_template('estoque/editar_item_estoque.html', dados_item=dados_item, tiposItens=tiposItens, nivel_acesso=session["nivel_acesso"])
    
    @app.route('/estoque/<codigo_item>/deletar')
    @login_requerido
    def deletarItem(codigo_item):
        estoque.deletarItem(codigo_item)
        return redirect(url_for('ver_estoque'))
    
    @app.route('/estoque/<codigo_item>/<ativar>')
    @login_requerido
    def definirAtivo(codigo_item, ativar=bool):
        estoque.definirAtivo(session["u_id"], codigo_item, ativar)
        return redirect(url_for('ver_item_estoque', codigo_item=codigo_item))
    
    @app.route("/estoque/print", methods=['GET', 'POST'])
    @login_requerido
    def imprimir_estoque():
        parametros = request.form.to_dict()

        tipo = parametros.get('tipo-filtro')
        estado = parametros.get('estado-filtro')

        if tipo in ("", "Todos"):
            tipo = None

        if estado in ("", "Todos"):
            estado = None

        itens_criticos = True if estado == "True" else False
        if itens_criticos:
            qtd_artigos = estoque.countArtigosCriticos()
        else:
            qtd_artigos = estoque.qtdArtigos(tipo)


        itens_estoque = estoque.getEstoque(
            tipo_item=tipo,
            item_ativo=True,
            itens_criticos=itens_criticos
        )

        valor_estoque = estoque.valorEstoque(tipo)

        operador = session["u_apelido"]
        id_operador = session["u_id"]
        return render_template(
            'estoque/template_print_estoque.html',
            data=data, hora=hora,
            dados_estq=itens_estoque,
            valor_estoque=valor_estoque,
            qtd_artigos=qtd_artigos,
            categoria=tipo or "Todos",
            operador=operador,
            id_operador=id_operador,
            criticos=itens_criticos
        )


################################################################################# Vendas


    @app.route('/vendas/nova', methods=['GET', 'POST'])
    @login_requerido
    def registrar_venda():
        if request.method == "POST":
            codigos = request.form.getlist("codigo[]")
            quantidades = request.form.getlist("quantidade[]")
            valores = request.form.getlist("valor[]")

            itens_venda = []
            valor_total = 0
            qtd_total_itens = 0

            for cod, qtd, val in zip(codigos, quantidades, valores):
                valor_float = moeda_para_float(val)
                quantidade = int(qtd)
                itens_venda.append({
                    "codigo": cod,
                    "quantidade": quantidade,
                    "valor_praticado": valor_float
                })
                valor_total = valor_total + (quantidade*valor_float)
                qtd_total_itens += quantidade

            dados_venda = {
                "id_cliente": request.form.get("id_cliente[]"),
                "qtd_itens": len(itens_venda),
                "qtd_total_itens": qtd_total_itens,
                "valor_total": valor_total,
                "obs": request.form.get("observacoes")
            }

            if not itens_venda:
                return redirect(url_for('registrar_venda'), erro="venda vazia")
            
            id_venda = vendas.registrarDadosVenda(dados_venda, session["u_id"])

            if id_venda:
                vendas.registrarItensVenda(id_venda, itens_venda)
                print(itens_venda)  # debug
                print("Valor total: ", valor_total)
                return redirect(url_for('visualizar_vendas'))
        
        itens = estoque.getEstoque()
        dados_clientes = clientes.getClientesVenda()
        dados = [{"data": data, "operador": session["u_apelido"], "id_venda": "27"}]
        return render_template('venda/registrar_venda.html', dados_itens=json.dumps(itens), dados_gerais=json.dumps(dados), dados_clientes=json.dumps(dados_clientes))
    
    @app.route('/vendas')
    @login_requerido
    def visualizar_vendas():
        if request.method == "POST":
            pass

        valor_vendas = vendas.getValorVendas()
        valor_vendas_hoje = vendas.getValorVendas(1)

        qtd_vendas = vendas.getQtyVendas()
        qtd_vendas_hoje = vendas.getQtyVendas(1)

        dados_vendas = vendas.getListaVendas()

        for item in dados_vendas:
            item["data_venda"] = item["data_venda"].strftime("%d/%m/%Y")

        return render_template('venda/visualizar_lista_vendas.html', dados_vendas=dados_vendas, qtd_vendas=qtd_vendas, valor_vendas=valor_vendas, valor_vendas_hoje=valor_vendas_hoje, qtd_vendas_hoje=qtd_vendas_hoje)


################################################################################# Clientes


    @app.route('/clientes')
    @login_requerido
    @acesso_requerido(1, 2)
    def visualizar_clientes():
        return render_template('clientes/ver_lista_clientes.html')
    

    @app.route('/clientes/ver')
    @login_requerido
    @acesso_requerido(1, 2)
    def detalhes_cliente():
        return render_template('clientes/ver_lista_clientes.html')
    

    @app.route('/clientes/editar')
    @login_requerido
    @acesso_requerido(1)
    def editar_cliente():
        return render_template('clientes/ver_lista_clientes.html')
    
################################################################################# Colaboradores


    @app.route('/colaboradores') 
    @login_requerido
    @acesso_requerido(1)
    def visualizar_colaboradores():
        qty_colabs = usuarios.getQtyColabs()
        dados_colabs = usuarios.getListaColaboradores()

        return render_template('colaboradores/ver_lista_colaboradores.html', dados_colabs=dados_colabs, qty_colabs=qty_colabs)


    @app.route('/colaboradores/<int:id_colab>', methods=['GET','POST'])
    @login_requerido
    @acesso_requerido(1)
    def detalhes_colaborador(id_colab):
        dados_colab = usuarios.getDadosColaborador(id_colab)
        return render_template('colaboradores/detalhes_colaborador.html', dados_colab=dados_colab) 
    
    
    @app.route('/colaboradores/<id_colab>/editar', methods=['GET', 'POST'])
    @login_requerido
    @acesso_requerido(1)
    def edit_dados_colaborador(id_colab):
        cargos = usuarios.getCargos()
        
        if request.method == 'POST':
            novos_dados_colab = request.form.to_dict()
            usuarios.setDadosColaborador(id_colab, novos_dados_colab, session["u_id"])

            return redirect(url_for('detalhes_colaborador', id_colab=id_colab, cargos=cargos, dados_colab=novos_dados_colab))
        
        dados_colab = usuarios.getDadosColaborador(id_colab)

        return render_template('colaboradores/editar_dados_colaborador.html', id_colab=id_colab, dados_colab=dados_colab, cargos=cargos)
    

    @app.route('/colaboradores/novo', methods = ['GET', 'POST'])
    @login_requerido
    @acesso_requerido(1)
    def cadastrar_colab():
        id_operador = session["u_id"]

        if request.method == 'POST':
            dados_colab = request.form.to_dict()

            salvar_colab = usuarios.setNovoColaborador(dados_colab, operador=id_operador)

            if salvar_colab == "USERNAME_DUPLICADO":
                return redirect(url_for('cadastrar_colab', erro='username_existente'))
            if salvar_colab != True:
                return redirect(url_for('cadastrar_colab', erro=True, stack_erro=salvar_colab))
            
            return redirect(url_for('visualizar_colaboradores'))

        cargos = usuarios.getCargos()

        return render_template('colaboradores/adicionar_colaborador.html', data=data, cargos=cargos)




######################################## Inicialização do app Flask
    app.run(debug=True, host="0.0.0.0")

if __name__ == "__main__":
    
    inicializarCfg()
    iniciarIndex()
