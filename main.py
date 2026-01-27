from flask import Flask, url_for, render_template, request, redirect, session, flash
from auth import login_required, gerarSenhaHash
from functools import wraps
import conn_cautelas as cautelas
import conn_clientes as clientes
import conn_estoque as estoque
import conn_colaboradores as usuarios
import db_configdata as db
import datetime, json, os


data = datetime.datetime.now().date().strftime("%d/%m/%Y")
dados_db = db.dados()




def iniciarIndex():

    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "cautelaos-secret")




    @app.route('/') ################################################################################################### Renderização de tela - principal (Dashboard)
    @login_required
    def cautelaos():
        return render_template('dashboard.html')
    



    @app.route("/login", methods=["GET", "POST"]) ##################################################################### Renderização de tela - login
    def login():
        if request.method == "POST":
            usuario = request.form["usuario"]
            senha = request.form["senha"]

            user = usuarios.autenticar_usuario(dados_db, usuario, senha)

            if user:
                session["usuario_id"] = user["id"]
                session["usuario_nome"] = user["nome"]
                session["nivel"] = user["nivel_acesso"]
                return redirect(url_for("cautelaos"))

            return render_template("login.html", erro="Usuário ou senha inválidos")

        return render_template("login.html")




    @app.route("/logout", methods=["POST"]) ########################################################################### Função de logout
    @login_required
    def logout():
        session.clear()
        flash("Sessão encerrada com sucesso.", "info")
        return redirect(url_for("login"))




    @app.route("/cautelas/") ########################################################################################### Renderização de tela - listagem de cautelas
    @login_required
    def listar_cautelas():
        lista_cautelas = cautelas.listaCautelas(dados_db)
        qtd_cautelas = cautelas.qtdCautelas(dados_db)
        return render_template('cautela/visualizar_lista_cautelas.html', dados=lista_cautelas, qtd=qtd_cautelas)





    @app.route('/cautelas/<id_cautela>') ################################################################################ Renderização de tela - visualizar cautela específica
    @login_required
    def ver_cautela(id_cautela):
        detalhe_dados = cautelas.getDadosCautela(dados_db, id_cautela)
        itens_cautela = cautelas.getItensCautela(dados_db, id_cautela, detalhe_dados["qtd_itens"])
        return render_template("cautela/visualizar_cautela.html", itens_cautela=itens_cautela, **detalhe_dados)





    @app.route("/cautelas/<id_cautela>/print") ########################################################################### Renderização de tela - renderizar cautela para impressão
    def imprimir_cautela(id_cautela):
        detalhe_dados = cautelas.getDadosCautela(dados_db, id_cautela)
        itens_cautela = cautelas.getItensCautela(dados_db, id_cautela, detalhe_dados["qtd_itens"])
        return render_template('cautela/template_print_cautela.html', itens_cautela=itens_cautela, **detalhe_dados)
    




    @app.route("/estoque") ############################################################################################### Renderização de tela - listagem de estoque
    @login_required
    def ver_estoque():
        dados_estoque = estoque.getEstoque(dados_db)
        valor_estoque = estoque.valorEstoque(dados_db)
        qtd_artigos = estoque.qtdArtigos(dados_db)
        return render_template('estoque/visualizar_lista_estoque.html', dados_estq=dados_estoque, valor_estoque=valor_estoque, qtd_artigos=qtd_artigos)
    




    @app.route("/estoque/<codigo_item>/ver") ################################################################################ Renderização de tela - detalhe de item do estoque
    @login_required
    def ver_item_estoque(codigo_item):
        dados_item = estoque.getDadosItem(dados_db, codigo_item)
        return render_template('estoque/ver_item_estoque.html', dados_item=dados_item)





    @app.route("/estoque/<codigo_item>/editar") ################################################################################ Renderização de tela - editar item do estoque
    @login_required
    def editar_item_estoque(codigo_item):
        tiposItens = estoque.getTiposItens(dados_db)
        dados_item = estoque.getDadosItem(dados_db, codigo_item)
        return render_template('estoque/editar_item_estoque.html', dados_item=dados_item, tiposItens=tiposItens)





    @app.route("/estoque/print") ############################################################################################# Renderização de tela - renderizar listagem de estoque para impressão
    def imprimir_estoque():
        tipo = request.args.get("tipo_filtro", "")
        #data = datetime.datetime.now().date().strftime("%d/%m/%Y")
        dados_estoque = estoque.getEstoque(dados_db, tipo)
        valor_estoque = estoque.valorEstoque(dados_db, tipo)
        qtd_artigos = estoque.qtdArtigos(dados_db, tipo)

        if tipo == "":
            tipo = "Tudo"
            
        return render_template('estoque/template_print_estoque.html', dados_estq=dados_estoque, valor_estoque=valor_estoque, qtd_artigos=qtd_artigos, categoria=tipo, data=data)





    @app.route("/cautela/nova") ############################################################################################# Renderização de tela - registro de nova cautela
    @login_required
    def nova_cautela():
        return render_template('cautela/adicionar_cautela.html')
    
    



    @app.route('/estoque/editar_item/<codigo_item>', methods=['POST', 'GET']) ###################################################### Função - alterar dados de item do estoque
    def alterarItem(codigo_item):
        dados_item = request.form.to_dict()

        estoque.alterarItemDB(dados_db, dados_item, codigo_item=codigo_item)

        codigo_item = dados_item.get('novo_codigo')
        return redirect(url_for('ver_item_estoque', codigo_item=codigo_item))





    @app.route('/estoque/adicionar') ############################################################################################# Renderização de tela - adicionar novo item no estoque
    @login_required
    def incluir_item():
        tiposItens = estoque.getTiposItens(dados_db)
        return render_template('estoque/adicionar_item_estoque.html', tiposItens=tiposItens)
    




    @app.route('/estoque/adicionar_item', methods=['POST']) ###################################################################### Função - adicionar novo item no estoque
    def adicionarItem():
        dados_item = request.form.to_dict()
        acao = dados_item.get('acao')

        estoque.adicionarItemDB(dados_db, dados_item)

        if acao == 'salvar_outro':
            flash('Item salvo! Você pode cadastrar outro.', 'success')
            return redirect(url_for('incluir_item'))
        
        return redirect(url_for('ver_estoque'))
    




    @app.route('/estoque/<codigo_item>/deletar') ############################################################################################# Função - deletar item do estoque
    def deletarItem(codigo_item):
        estoque.deletarItem(dados_db, codigo_item)
        return redirect(url_for('ver_estoque'))
    




    @app.route('/vendas/nova') ############################################################################################# Renderização de tela - registro de nova venda
    @login_required
    def registrar_venda():
        itens = estoque.getEstoque(dados_db)
        dados_clientes = clientes.getClientesVenda(dados_db)

        dados = [
            {"data": data, "operador": session["usuario_nome"], "id_venda": "27"}
        ]

        return render_template('venda/registrar_venda.html', dados_itens=json.dumps(itens), dados_gerais=json.dumps(dados), dados_clientes=json.dumps(dados_clientes))





    @app.route('/vendas/salvar', methods=['POST']) ############################################################################################# Função - gravar venda
    def salvarVenda():
        #descricao = request.form.get('descricao')
        
        return redirect(url_for('ver_estoque'))
    



    @app.route('/vendas') ############################################################################################# Renderização de tela - listagem de vendas
    @login_required
    def visualizar_vendas():
        return render_template('dashboard.html')
    




    @app.route('/clientes') ############################################################################################# Renderização de tela - listagem de clientes
    @login_required
    def visualizar_clientes():
        return render_template('clientes/ver_lista_clientes.html')
    
    



    @app.route('/colaboradores') ############################################################################################# Renderização de tela - listagem de colaboradores
    @login_required
    def visualizar_colaboradores():
        return render_template('colaboradores/ver_lista_colaboradores.html')









    app.run(debug=True, host="0.0.0.0")
if __name__ == "__main__":
    iniciarIndex()
    