from flask import Flask, url_for, render_template, request, redirect
import conn as db

def iniciarIndex():

    app = Flask(__name__)

    @app.route('/')
    def cautelaos():
        return render_template('index.html')


    @app.route("/cautelas/")
    def listar_cautelas():
        cautelas = db.listaCautelas()
        qtd_cautelas = db.qtdCautelas()
        return render_template('visualizar_lista_cautelas.html', dados=cautelas, qtd=qtd_cautelas)


    @app.route('/cautelas/<id_cautela>')
    def ver_cautela(id_cautela):
        detalhe_dados = db.getDadosCautela(id_cautela)
        itens_cautela = db.getItensCautela(id_cautela, detalhe_dados["qtd_itens"])
        return render_template("visualizar_cautela.html", itens_cautela=itens_cautela, **detalhe_dados)



    @app.route("/cautelas/<id_cautela>/print")
    def imprimir_cautela(id_cautela):
        detalhe_dados = db.getDadosCautela(id_cautela)
        itens_cautela = db.getItensCautela(id_cautela, detalhe_dados["qtd_itens"])
        return render_template('template_print_cautela.html', itens_cautela=itens_cautela, **detalhe_dados)
    
    @app.route("/estoque")
    def ver_estoque():
        dados_estoque = db.getEstoque()
        valor_estoque = db.valorEstoque()
        qtd_artigos = db.qtdArtigos()
        return render_template('visualizar_lista_estoque.html', dados_estq=dados_estoque, valor_estoque=valor_estoque, qtd_artigos=qtd_artigos)
    

    @app.route("/estoque/<codigo_item>/ver")
    def ver_item_estoque(codigo_item):
        dados_item = db.getDadosItem(codigo_item)
        return render_template('ver_item_estoque.html', dados_item=dados_item)

    
    @app.route("/estoque/print")
    def imprimir_estoque():
        tipo = request.args.get("tipo_filtro", "")

        dados_estoque = db.getEstoque(tipo)
        valor_estoque = db.valorEstoque(tipo)
        qtd_artigos = db.qtdArtigos(tipo)

        if tipo == "":
            tipo = "Tudo"
            
        return render_template('template_print_estoque.html', dados_estq=dados_estoque, valor_estoque=valor_estoque, qtd_artigos=qtd_artigos, categoria=tipo)

    @app.route("/cautela/nova")
    def nova_cautela():
        return render_template('adicionar_cautela.html')
    
    
    @app.route('/estoque/editar_item/<codigo_item>', methods=['POST'])
    def alterarItem(codigo_item):
        descricao = request.form.get('descricao')
        valor = request.form.get('valor')
        quantidade = request.form.get('quantidade')
        ean_13 = request.form.get('ean_13')
        novo_codigo = request.form.get('novo_codigo')

        db.alterarItemDB(codigo_item, descricao, valor, quantidade, ean_13, novo_codigo)
        return redirect(url_for('ver_estoque'))

    @app.route('/estoque/adicionar')
    def incluir_item():
        return render_template('adicionar_item_estoque.html')

    @app.route('/estoque/adicionar_item', methods=['POST'])
    def adicionarItem():
        descricao = request.form.get('descricao')
        valor = request.form.get('valor')
        quantidade = request.form.get('quantidade')
        ean = request.form.get('ean_13')
        codigo = request.form.get('codigo')
        tipo = request.form.get('tipo_material')

        db.adicionarItemDB(codigo, descricao, valor, quantidade, ean, tipo)
        return redirect(url_for('ver_estoque'))
    
    @app.route('/estoque/<codigo_item>/deletar')
    def deletarItem(codigo_item):
        db.deletarItem(codigo_item)
        return redirect(url_for('ver_estoque'))

    app.run(debug=True, host="0.0.0.0")

if __name__ == "__main__":
    iniciarIndex()
    