from flask import Flask, url_for, render_template
import conn as db

def iniciarIndex():

    app = Flask(__name__)

    @app.route('/')
    def cautelaos():
        return render_template('index.html')


    @app.route("/cautelas/")
    def listar_cautelas():
        cautelas = db.listaCautelas()
        return render_template('lista_cautelas.html', dados=cautelas)


    @app.route('/cautelas/<id_cautela>')
    def ver_cautela(id_cautela):
        detalhe_dados = db.getDadosCautela(id_cautela)
        itens_cautela = db.getItensCautela(id_cautela, detalhe_dados["qtd_itens"])
        return render_template("cautela.html", itens_cautela=itens_cautela, **detalhe_dados)



    @app.route("/cautelas/<id_cautela>/print")
    def imprimir_cautela(id_cautela):
        detalhe_dados = db.getDadosCautela(id_cautela)
        itens_cautela = db.getItensCautela(id_cautela, detalhe_dados["qtd_itens"])
        return render_template('cautela_print.html', itens_cautela=itens_cautela, **detalhe_dados)
    


    



    @app.route("/estoque")
    def ver_estoque():
        dados_estoque = db.getEstoque()
        return render_template('listagem_estoque.html', dados_estq=dados_estoque)
    

    @app.route("/estoque/<codigo_item>")
    def ver_item(codigo_item):
        return codigo_item
    
    @app.route("/estoque/print")
    def imprimir_estoque():
        dados_estoque = db.getEstoque()
        return render_template('imprimir_estoque.html', dados_estq=dados_estoque)

    @app.route("/cautela/nova")
    def nova_cautela():
        return "<h2>Nova Cautela</h2>"



    app.run(debug=True, host="0.0.0.0")

if __name__ == "__main__":
    iniciarIndex()
    