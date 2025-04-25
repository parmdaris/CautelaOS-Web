from flask import Flask, url_for, render_template

app = Flask(__name__)

@app.route('/')
def olaMundo():
    titulo = "Projetito do flaques"
    usuarios = [
        {"nome":"Atonio", "membro-ativo":True},
        {"nome":"Juao", "membro-ativo":False}
    ]
    return render_template('index.html', titulo=titulo, usuarios=usuarios)

@app.route('/sobre')
def sobre():
    return "so eu, o tiririca"

@app.route('/weather')
def climaTempo():
    dados = {
        "cidade": "São Paulo",
        "pais": "Brasil",
        "temperatura": 27,
        "descricao": "Céu limpo",
        "umidade": 58,
        "vento": 12,
        "atualizado_em": "24/04/2025 15:40"
    }
    return render_template('weather.html', **dados)

@app.route('/cautela/<id_cautela>')
def cautela(id_cautela):
    dados = {
        "destino": "Departamento de TI - Sala 203",
        "data": "24/04/2025",
        "materiais": [
            {"quantidade": 2, "nome": "Notebook Lenovo ThinkPad"},
            {"quantidade": 3, "nome": "Mouse sem fio Logitech"},
            {"quantidade": 1, "nome": "Projetor Epson X200"}
        ],
        "observacoes": "id: " + id_cautela
    }

    return render_template("cautela.html", **dados)

@app.route("/estoque")
def ver_estoque():
    return "<h2>Página de Estoque</h2>"

@app.route("/cautelas")
def ver_cautelas():
    return "<h2>Lista de Cautelas</h2>"

@app.route("/cautela/nova")
def nova_cautela():
    return "<h2>Nova Cautela</h2>"

@app.route('/main')
def mainmenu():
    return render_template("mainmenu.html")



app.run(debug=True)