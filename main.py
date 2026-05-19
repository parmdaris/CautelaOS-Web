from flask import Flask, url_for, render_template, request, redirect, session, current_app
from conn_auth import login_requerido, gerarSenhaHash, tem_acesso, permissao_requerida, macrofuncao_requerida
from ativ_sistema import inicializarCfg, getVersao, getListaFuncoes
from conn_estoque import moeda_para_float
import conn_cautelas as cautelas, conn_clientes as clientes, conn_estoque as estoque, conn_vendas as vendas
import conn_modulos as modulos, conn_colaboradores as usuarios
import datetime, json, traceback

data_iso = datetime.datetime.now().date().strftime("%Y-%m-%d %H:%M:%S")
data = datetime.datetime.now().date().strftime("%d/%m/%Y")
hora = datetime.datetime.now().time().strftime("%H:%M:%S")

app = Flask(__name__)

def iniciarIndex():

    app.secret_key = "cautelaos"
    app.jinja_env.globals.update(tem_acesso=tem_acesso)
    

    #app.secret_key = os.environ.get("SECRET_KEY", "cautelaos-secret")

################################################################################# Dashboard, login e logout

    @app.route('/')
    @login_requerido
    def dashboard():

        if not session.get("modulo_id"):
            return redirect(url_for("selecionar_modulo"))
    
        session["modulo"] = modulos.getModulos(int(session["modulo_id"]))

        print(session.get("usuario", ""))
        
        valor_estoque = estoque.valorEstoque()
        qtd_itens = estoque.qtdArtigos()
        criticos = estoque.countArtigosCriticos()
        valor_total_hoje = vendas.getValorVendas(0)
        qtd_vendas_hoje = vendas.getQtyVendas(0)

        return render_template('dashboard.html', 
                               valor_estoque=valor_estoque, 
                               qtd_itens=qtd_itens, 
                               criticos=criticos, 
                               valor_total_hoje=valor_total_hoje,
                               qtd_vendas_hoje=qtd_vendas_hoje,
                               )
    
    
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        session["versao_sistema"] = getVersao()
        if request.method == "POST":
            usuario = request.form["usuario"]
            senha = request.form["senha"]

            user = usuarios.autenticar_usuario(usuario, senha)
            
            if user:
                session["usuario"] = user

                usuarios.ultimoLogin(user['id'])
                
                if user["primeiro_acesso"]:
                    return redirect(url_for("acesso_inicial"))
                else:
                    return redirect(url_for("selecionar_modulo"))

            return render_template("login.html", erro="Usuário ou senha inválidos")

        return render_template("login.html")

    @app.route("/logout", methods=["POST"])
    def logout():
        if session:
            session.clear()
        return redirect(url_for("login"))
    

    @app.route("/start", methods=["POST", "GET"])
    @login_requerido
    def acesso_inicial():
        if request.method == "POST":
            senha_inserida = request.form["senha"]

            if usuarios.compararSenhaHash(session["usuario"]["id"], senha_inserida):
                return render_template("start.html", erro="A senha deve ser diferente da atual")
            
            usuarios.contaIniciada(session["usuario"]["id"], gerarSenhaHash(senha_inserida))
            return redirect(url_for("dashboard"))
        
        return render_template("start.html", usuario = session["usuario"]["u_apelido"])
    
    @app.errorhandler(Exception)
    def tratar_erro(e):
        tipo = type(e).__name__

        if current_app.debug:
            return render_template(
                "error.html",
                erro=str(e),
                tipo=tipo,
                traceback=traceback.format_exc()
            ), 500

        return render_template(
            "error.html",
            tipo=tipo
        ), getattr(e, 'code', 500)

################################################################################# Modulos de trabalho
    
    @app.route("/modulos")
    @login_requerido
    def selecionar_modulo():
        sys_versao = getVersao()
        sys_modulos = modulos.getModulos()
        usr_modulos = modulos.verificarAcesso(session["usuario"]["id"])

        if len(usr_modulos) == 1:
            session["modulo_id"] = usr_modulos[0]
            session["u_qtd_modulos"] = 1
            return redirect(url_for("dashboard"))
        else:
            session["u_qtd_modulos"] = len(usr_modulos)
            return render_template("selecao_modulo.html", sys_versao=sys_versao, modulos=sys_modulos, usr_modulos=usr_modulos)
    
    
    @app.route('/<int:id_modulo>')
    @login_requerido
    def definir_modulo(id_modulo):
        session["modulo_id"] = id_modulo
        return redirect(url_for("dashboard"))

################################################################################# Cautelas


    @app.route("/cautelas/")
    @login_requerido
    @macrofuncao_requerida('cautela')
    def listar_cautelas():
        lista_cautelas = cautelas.listaCautelas()
        qtd_cautelas = cautelas.qtdCautelas()
        return render_template('cautela/visualizar_lista_cautelas.html', dados=lista_cautelas, qtd=qtd_cautelas)

    @app.route("/cautela/nova")
    @login_requerido
    @permissao_requerida('cautela_registrar')
    @macrofuncao_requerida('cautela')
    def nova_cautela():
        return render_template('cautela/adicionar_cautela.html')

    @app.route('/cautelas/<id_cautela>')
    @login_requerido
    @macrofuncao_requerida('cautela')
    def ver_cautela(id_cautela):
        detalhe_dados = cautelas.getDadosCautela(id_cautela)
        itens_cautela = cautelas.getItensCautela(id_cautela, detalhe_dados["qtd_itens"])
        return render_template("cautela/visualizar_cautela.html", itens_cautela=itens_cautela, **detalhe_dados)

    @app.route("/cautelas/<id_cautela>/print")
    @login_requerido
    @macrofuncao_requerida('cautela')
    def imprimir_cautela(id_cautela):
        detalhe_dados = cautelas.getDadosCautela(id_cautela)
        itens_cautela = cautelas.getItensCautela(id_cautela, detalhe_dados["qtd_itens"])
        return render_template('cautela/template_print_cautela.html', itens_cautela=itens_cautela, **detalhe_dados)


################################################################################# Estoque


    @app.route("/estoque")
    @login_requerido
    @macrofuncao_requerida('estoque')
    def ver_estoque():
        tipos = estoque.getTiposItens()
        dados_estoque = estoque.getEstoque(id_modulo = session.get("modulo").get("id"))
        valor_estoque = estoque.valorEstoque(id_modulo = session.get("modulo").get("id"))
        qtd_artigos = estoque.qtdArtigos()
        return render_template('estoque/visualizar_lista_estoque.html', 
                               dados_estq=dados_estoque, 
                               valor_estoque=valor_estoque, 
                               qtd_artigos=qtd_artigos,
                               tipos_itens=tipos
                               )
    


    @app.route("/estoque/inativos")
    @login_requerido
    @macrofuncao_requerida('estoque')
    def ver_itens_inativos():
        tipos = estoque.getTiposItens()
        dados_estoque = estoque.getEstoque(None, False)
        qtd_artigos_inativos = estoque.qtdArtigos(None, False)
        return render_template('estoque/visualizar_lista_inativos.html', 
                               dados_estq=dados_estoque, 
                               qtd_artigos=qtd_artigos_inativos,
                               tipos_itens=tipos
                               )
    

    
    @app.route("/estoque/editar_item/lote")
    @login_requerido
    @permissao_requerida('estoque_editar')
    @macrofuncao_requerida('estoque')
    def editar_lote():
        if request.method == 'POST': ####################################################################################
            return None

        tipos = estoque.getTiposItens()
        dados_estoque = estoque.getEstoque(None, False)
        qtd_artigos_inativos = estoque.qtdArtigos(None, False)
        return render_template('estoque/editar_lote.html', 
                               dados_estq=dados_estoque, 
                               qtd_artigos=qtd_artigos_inativos,
                               tipos_itens=tipos
                               )

    
    @app.route("/estoque/<codigo_item>/ver")
    @login_requerido
    @macrofuncao_requerida('estoque')
    def ver_item_estoque(codigo_item):
        dados_item = estoque.getDadosItem(codigo_item)
        return render_template('estoque/ver_item_estoque.html', dados_item=dados_item)
    
    @app.route('/estoque/adicionar_item', methods=['GET', 'POST'])
    @login_requerido
    @permissao_requerida('estoque_cadastrar')
    @macrofuncao_requerida('estoque')
    def adicionarItem():

        if request.method == 'POST':
            dados_item = request.form.to_dict()
            acao = dados_item.get('acao')

            salvar_item = estoque.adicionarItemDB(dados_item, session["usuario"]["id"])

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
    @permissao_requerida('estoque_editar')
    @macrofuncao_requerida('estoque')
    def alterarItem(codigo_item):
        if request.method == 'POST':
            dados_item = request.form.to_dict()
            estoque.alterarItemDB(dados_item, codigo_item=codigo_item, id_operador=session["usuario"]["id"])
            codigo_item = dados_item.get('novo_codigo')
            return redirect(url_for('ver_item_estoque', codigo_item=codigo_item))
        
        tiposItens = estoque.getTiposItens()
        dados_item = estoque.getDadosItem(codigo_item)
        return render_template('estoque/editar_item_estoque.html', dados_item=dados_item, tiposItens=tiposItens, nivel_acesso=session["nivel_acesso"])
    
    @app.route('/estoque/<codigo_item>/deletar')
    @login_requerido
    @permissao_requerida('estoque_editar')
    @macrofuncao_requerida('estoque')
    def deletarItem(codigo_item):
        estoque.deletarItem(codigo_item)
        return redirect(url_for('ver_estoque'))
    
    @app.route('/estoque/<codigo_item>/<ativar>')
    @login_requerido
    @permissao_requerida('estoque_editar')
    @macrofuncao_requerida('estoque')
    def definirAtivo(codigo_item, ativar=bool):
        estoque.definirAtivo(session["usuario"]["id"], codigo_item, ativar)
        return redirect(url_for('ver_item_estoque', codigo_item=codigo_item))
    
    @app.route("/estoque/print", methods=['GET', 'POST'])
    @login_requerido
    @macrofuncao_requerida('estoque')
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
        id_operador = session["usuario"]["id"]
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
    @permissao_requerida('venda_registrar')
    @macrofuncao_requerida('venda')
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
                "obs": request.form.get("observacoes"),
                "vendedor": request.form.get("vendedor")
            }

            if not itens_venda:
                return redirect(url_for('registrar_venda'), erro="venda vazia")
            
            id_venda = vendas.registrarDadosVenda(dados_venda, session["usuario"]["id"])

            if id_venda:
                vendas.registrarItensVenda(id_venda, itens_venda)
                return redirect(url_for('visualizar_vendas'))
            
        ####################################################################### Fim if POST
        itens = estoque.getEstoque()
        dados_clientes = clientes.getClientesVenda()
        id_atual = vendas.getQtyVendas(0, True) + 1
        dados = [{"data": data, "operador": session["u_apelido"], "id_venda": id_atual}]
        lista_colaboradores = usuarios.getListaColaboradores(True)
        return render_template('venda/registrar_venda.html', dados_itens=json.dumps(itens), dados_gerais=json.dumps(dados), dados_clientes=json.dumps(dados_clientes), lista_colaboradores=json.dumps(lista_colaboradores))
    
    @app.route('/vendas')
    @login_requerido
    @macrofuncao_requerida('venda')
    def visualizar_vendas():
        if request.method == "POST":
            pass

        valor_vendas = vendas.getValorVendas(-1)
        valor_vendas_hoje = vendas.getValorVendas(0)

        qtd_vendas = vendas.getQtyVendas(-1)
        qtd_vendas_hoje = vendas.getQtyVendas(0)

        dados_vendas = vendas.getListaVendas()

        for item in dados_vendas:
            item["data_venda"] = item["data_venda"].strftime("%d/%m/%Y")

        return render_template('venda/visualizar_lista_vendas.html', dados_vendas=dados_vendas, qtd_vendas=qtd_vendas, valor_vendas=valor_vendas, valor_vendas_hoje=valor_vendas_hoje, qtd_vendas_hoje=qtd_vendas_hoje)


    @app.route("/vendas/<id_venda>/ver")
    @login_requerido
    @macrofuncao_requerida('venda')
    def ver_venda(id_venda):
        dados_venda = vendas.getDadosVenda(id_venda)
        return render_template('venda/ver_venda.html', dados_venda=dados_venda)

################################################################################# Clientes


    @app.route('/clientes')
    @login_requerido
    @macrofuncao_requerida('cliente')
    def visualizar_clientes():
        lista_clientes = clientes.getClientes()
        qtd_clientes = {
            "total": int(clientes.getQtyClientes(0)),
            "ativos": int(clientes.getQtyClientes()),
            "inativos": int(clientes.getQtyClientes(-1))
        }

        return render_template('clientes/ver_lista_clientes.html', lista_clientes = lista_clientes, qtd_clientes = qtd_clientes, ativos = True)
    
    @app.route('/clientes/inativos')
    @login_requerido
    @macrofuncao_requerida('cliente')
    def visualizar_clientes_inativos():
        lista_clientes = clientes.getClientes(-1)
        qtd_clientes = {
            "total": int(clientes.getQtyClientes(0)),
            "ativos": int(clientes.getQtyClientes()),
            "inativos": int(clientes.getQtyClientes(-1))
        }

        return render_template('clientes/ver_lista_clientes.html', lista_clientes = lista_clientes, qtd_clientes = qtd_clientes, ativos = False)

    @app.route('/clientes/<id_cliente>')
    @login_requerido
    @macrofuncao_requerida('cliente')
    def detalhes_cliente(id_cliente):
        dados_cliente = clientes.getDadosCliente(id_cliente)
        return render_template('clientes/detalhes_cliente.html', cliente=dados_cliente)
    

    @app.route('/clientes/editar/<id_cliente>')
    @login_requerido
    @permissao_requerida('cliente_editar')
    @macrofuncao_requerida('cliente')
    def editar_cliente(id_cliente):
        modulos = [
            {"nome": "Vortex Filamentos", "apelido": "vortex"},
            {"nome": "Mimiso Arena Card Games", "apelido": "mimiso"}, ##################################################################################################!!!!!! EDITAR
            {"nome": "Niitech Outsourcing", "apelido": "niitech"}
        ]
        dados_cliente = clientes.getDadosCliente(id_cliente)
        return render_template('clientes/editar_dados_cliente.html', cliente=dados_cliente, modulos=modulos)
    
################################################################################# Colaboradores


    @app.route('/colaboradores') 
    @login_requerido
    @macrofuncao_requerida('colaborador')
    def visualizar_colaboradores():
        qty_colabs = usuarios.getQtyColabs()
        dados_colabs = usuarios.getListaColaboradores()

        return render_template('colaboradores/ver_lista_colaboradores.html', dados_colabs=dados_colabs, qty_colabs=qty_colabs)


    @app.route('/colaboradores/<int:id_colab>', methods=['GET','POST'])
    @login_requerido
    @macrofuncao_requerida('colaborador')
    def detalhes_colaborador(id_colab):
        dados_colab = usuarios.getDadosColaborador(id_colab)
        lista_funcoes = getListaFuncoes()
        lista_modulos = modulos.getModulos()
        return render_template('colaboradores/detalhes_colaborador.html', dados_colab=dados_colab, lista_funcoes=lista_funcoes, lista_modulos=lista_modulos) 
    

    @app.route('/perfil', methods=['GET','POST'])
    @login_requerido
    @macrofuncao_requerida('colaborador')
    def perfil_colaborador():
        id_colab = session["usuario"]["id"]
        dados_colab = usuarios.getDadosColaborador(id_colab)
        return render_template('colaboradores/perfil_colaborador.html', dados_colab=dados_colab) 
    
    
    @app.route('/colaboradores/<id_colab>/editar', methods=['GET', 'POST'])
    @login_requerido
    @permissao_requerida('colaborador_editar')
    @macrofuncao_requerida('colaborador')
    def edit_dados_colaborador(id_colab):
        cargos = usuarios.getCargos()
        
        if request.method == 'POST':
            novos_dados_colab = request.form.to_dict()
            usuarios.setDadosColaborador(id_colab, novos_dados_colab, session["usuario"]["id"])

            return redirect(url_for('detalhes_colaborador', id_colab=id_colab, cargos=cargos, dados_colab=novos_dados_colab))
        
        pendente = usuarios.checkContaIniciada(id_colab)
        dados_colab = usuarios.getDadosColaborador(id_colab)

        return render_template('colaboradores/editar_dados_colaborador.html', id_colab=id_colab, dados_colab=dados_colab, cargos=cargos, pendente = pendente)
    

    @app.route('/colaboradores/novo', methods = ['GET', 'POST'])
    @login_requerido
    @permissao_requerida('colaborador_cadastrar')
    @macrofuncao_requerida('colaborador')
    def cadastrar_colab():
        id_operador = session["usuario"]["id"]

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


    @app.route('/perfil/alterar/senha', methods = ['GET', 'POST'])
    @login_requerido
    @permissao_requerida('colaborador_editar')
    @macrofuncao_requerida('colaborador')
    def alterar_senha_colab():
        if request.method == 'POST':
            pw_atual = request.form.get("senha_atual")
            novo_pw = request.form.get("nova_senha")
            
            if usuarios.compararSenhaHash(session["usuario"]["id"], pw_atual):
                usuarios.alterarSenha(session["usuario"]["id"], novo_pw, session["usuario"]["id"])
                usuarios.registrar_modificacao(session["usuario"]["id"], session["usuario"]["id"])
                session.clear()
                return redirect(url_for("login"))
                #return redirect(url_for('perfil_colaborador'))
            
            else:
                pass #######################Lidar com senha incorreta

        return render_template('colaboradores/colab_alterar_senha.html', id=session["usuario"]["id"])


    @app.route('/colaboradores/<id_colab>/editar/redefinirsenha', methods = ['GET', 'POST'])
    @login_requerido
    @permissao_requerida('colaborador_editar')
    @macrofuncao_requerida('colaborador')
    def redefinir_senha_colab(id_colab):
        if request.method == 'POST':
            cpf_informado = request.form.get("cpf_colaborador")
            red = usuarios.recuperarSenha(id_colab, cpf_informado, session["usuario"]["id"])
            return redirect(url_for("detalhes_colaborador", id_colab = id_colab))
        
        dados_colab = usuarios.getDadosColaborador(id_colab)
        login_colab = dados_colab['nome_usuario']
        return render_template('colaboradores/colab_redefinir.html', id_colab=id_colab, login_colab=login_colab)


######################################## Inicialização do app Flask


inicializarCfg()
iniciarIndex() 

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

