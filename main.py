from flask import Flask, url_for, render_template, request, redirect, session
from auth import login_requerido, acesso_requerido, gerarSenhaHash, tem_acesso
import conn_cautelas as cautelas
import conn_clientes as clientes
import conn_estoque as estoque
import conn_colaboradores as usuarios
import db_configdata as db
import datetime, json, os

data_iso = datetime.datetime.now().date().strftime("%Y-%m-%d %H:%M:%S")
data = datetime.datetime.now().date().strftime("%d/%m/%Y")
hora = datetime.datetime.now().time().strftime("%H:%M:%S")

dados_db = db.dados()




def iniciarIndex():

    app = Flask(__name__)
    app.secret_key = "cautelaos"
    app.jinja_env.globals.update(tem_acesso=tem_acesso)

    #app.secret_key = os.environ.get("SECRET_KEY", "cautelaos-secret")

################################################################################# Dashboard, login e logout

    @app.route('/')
    @login_requerido
    def dashboard():

        valor_estoque = estoque.valorEstoque(dados_db)
        qtd_itens = estoque.qtdArtigos(dados_db)
        criticos = estoque.countArtigosCriticos(dados_db)
        val_vendas = "1.500,00"
        qtd_vendas_hj = 12

        return render_template('dashboard.html', 
                               valor_estoque=valor_estoque, 
                               qtd_itens=qtd_itens, 
                               criticos=criticos, 
                               val_vendas=val_vendas,
                               qtd_vendas_hj=qtd_vendas_hj
                               )
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            usuario = request.form["usuario"]
            senha = request.form["senha"]

            user = usuarios.autenticar_usuario(dados_db, usuario, senha)

            if user:
                session["usuario_id"] = user["id"]
                session["usuario_nome"] = user["nome"]
                session["nivel_acesso"] = user["id_acesso"]
                session["cargo"] = user["cargo"]


                return redirect(url_for("dashboard"))

            return render_template("login.html", erro="Usuário ou senha inválidos")

        return render_template("login.html")

    @app.route("/logout", methods=["POST"])
    @login_requerido
    def logout():
        session.clear()
        return redirect(url_for("login"))


################################################################################# Cautelas


    @app.route("/cautelas/")
    @login_requerido
    def listar_cautelas():
        lista_cautelas = cautelas.listaCautelas(dados_db)
        qtd_cautelas = cautelas.qtdCautelas(dados_db)
        return render_template('cautela/visualizar_lista_cautelas.html', dados=lista_cautelas, qtd=qtd_cautelas)

    @app.route("/cautela/nova")
    @login_requerido
    def nova_cautela():
        return render_template('cautela/adicionar_cautela.html')

    @app.route('/cautelas/<id_cautela>')
    @login_requerido
    def ver_cautela(id_cautela):
        detalhe_dados = cautelas.getDadosCautela(dados_db, id_cautela)
        itens_cautela = cautelas.getItensCautela(dados_db, id_cautela, detalhe_dados["qtd_itens"])
        return render_template("cautela/visualizar_cautela.html", itens_cautela=itens_cautela, **detalhe_dados)

    @app.route("/cautelas/<id_cautela>/print")
    def imprimir_cautela(id_cautela):
        detalhe_dados = cautelas.getDadosCautela(dados_db, id_cautela)
        itens_cautela = cautelas.getItensCautela(dados_db, id_cautela, detalhe_dados["qtd_itens"])
        return render_template('cautela/template_print_cautela.html', itens_cautela=itens_cautela, **detalhe_dados)


################################################################################# Estoque


    @app.route("/estoque")
    @login_requerido
    def ver_estoque():
        tipos = estoque.getTiposItens(dados_db)
        dados_estoque = estoque.getEstoque(dados_db)
        valor_estoque = estoque.valorEstoque(dados_db)
        qtd_artigos = estoque.qtdArtigos(dados_db)
        return render_template('estoque/visualizar_lista_estoque.html', 
                               dados_estq=dados_estoque, 
                               valor_estoque=valor_estoque, 
                               qtd_artigos=qtd_artigos,
                               tipos_itens=tipos
                               )
    
    @app.route("/estoque/<codigo_item>/ver")
    @login_requerido
    def ver_item_estoque(codigo_item):
        dados_item = estoque.getDadosItem(dados_db, codigo_item)
        return render_template('estoque/ver_item_estoque.html', dados_item=dados_item)
    
    @app.route('/estoque/adicionar_item', methods=['GET', 'POST'])
    @login_requerido
    def adicionarItem():

        if request.method == 'POST':
            dados_item = request.form.to_dict()
            acao = dados_item.get('acao')

            salvar_item = estoque.adicionarItemDB(dados_db, dados_item)

            if salvar_item == "SKU_DUPLICADO":
                return redirect(url_for('adicionarItem', erro='sku_existente'))
            if salvar_item is False:
                return redirect(url_for('adicionarItem', erro='erro_geral'))
            
            if acao == 'salvar_outro':
                return redirect(url_for('adicionarItem'))
            
            return redirect(url_for('ver_estoque'))
        
        tiposItens = estoque.getTiposItens(dados_db)
        return render_template('estoque/adicionar_item_estoque.html', tiposItens=tiposItens)
    
    @app.route('/estoque/editar_item/<codigo_item>', methods=['POST', 'GET'])
    def alterarItem(codigo_item):
        if request.method == 'POST':
            dados_item = request.form.to_dict()
            estoque.alterarItemDB(dados_db, dados_item, codigo_item=codigo_item)
            codigo_item = dados_item.get('novo_codigo')
            return redirect(url_for('ver_item_estoque', codigo_item=codigo_item))

        tiposItens = estoque.getTiposItens(dados_db)
        dados_item = estoque.getDadosItem(dados_db, codigo_item)
        return render_template('estoque/editar_item_estoque.html', dados_item=dados_item, tiposItens=tiposItens)
    
    @app.route('/estoque/<codigo_item>/deletar')
    def deletarItem(codigo_item):
        estoque.deletarItem(dados_db, codigo_item)
        return redirect(url_for('ver_estoque'))
    
    @app.route("/estoque/print", methods=['GET', 'POST'])
    def imprimir_estoque():
        parametros = request.form.to_dict()
        tipo = parametros.get('tipo-filtro')

        if tipo == "Todos":
            tipo = ""

        itens_estoque = estoque.getEstoque(dados_db, tipo)
        valor_estoque = estoque.valorEstoque(dados_db, tipo)
        qtd_artigos = estoque.qtdArtigos(dados_db, tipo)
        operador = session["usuario_nome"]
        id_operador = session["usuario_id"]

        
            
        return render_template('estoque/template_print_estoque.html', 
                               dados_estq=itens_estoque, 
                               valor_estoque=valor_estoque, 
                               qtd_artigos=qtd_artigos, 
                               categoria=tipo, data=data, 
                               hora=hora, operador=operador, 
                               id_operador=id_operador
                               )
    

################################################################################# Vendas


    @app.route('/vendas/nova', methods=['GET', 'POST'])
    @login_requerido
    def registrar_venda():
        if request.method == "POST":
            #descricao = request.form.get('descricao')
            return redirect(url_for('ver_estoque'))
        
        itens = estoque.getEstoque(dados_db)
        dados_clientes = clientes.getClientesVenda(dados_db)
        dados = [{"data": data, "operador": session["usuario_nome"], "id_venda": "27"}]
        return render_template('venda/registrar_venda.html', dados_itens=json.dumps(itens), dados_gerais=json.dumps(dados), dados_clientes=json.dumps(dados_clientes))
    
    @app.route('/vendas')
    @login_requerido
    def visualizar_vendas():
        return render_template('dashboard.html')


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
        qty_colabs = usuarios.getQtyColabs(dados_db)
        dados_colabs = usuarios.getListaColaboradores(dados_db)

        return render_template('colaboradores/ver_lista_colaboradores.html', dados_colabs=dados_colabs, qty_colabs=qty_colabs)


    @app.route('/colaboradores/<id_colab>', methods=['GET','POST'])
    @login_requerido
    @acesso_requerido(1)
    def detalhes_colaborador(id_colab):
        dados_colab = usuarios.getDadosColaborador(dados_db, id_colab)

        return render_template('colaboradores/detalhes_colaborador.html', dados_colab=dados_colab) 
    
    
    @app.route('/colaboradores/<id_colab>') 
    @login_requerido
    @acesso_requerido(1)
    def edit_dados_colaborador(id_colab):
        return render_template('colaboradores/ver_lista_colaboradores.html') 
    

    @app.route('/colaboradores/novo', methods = ['GET', 'POST']) 
    @login_requerido
    @acesso_requerido(1)
    def cadastrar_colab():
        id_operador = session["usuario_id"]

        if request.method == 'POST':
            dados_colab = request.form.to_dict()

            salvar_colab = usuarios.novoColaborador(dados_db, dados_colab, data=data_iso, operador=id_operador)

            if salvar_colab == "USERNAME_DUPLICADO":
                return redirect(url_for('cadastrar_colab', erro='username_existente'))
            if salvar_colab != True:
                return redirect(url_for('cadastrar_colab', erro=True, stack_erro=salvar_colab))
            
            return redirect(url_for('visualizar_colaboradores'))

        cargos = usuarios.getCargos(dados_db)

        return render_template('colaboradores/adicionar_colaborador.html', data=data, cargos=cargos)




######################################## Inicialização do app Flask
    app.run(debug=True, host="0.0.0.0")

if __name__ == "__main__":
    iniciarIndex()
