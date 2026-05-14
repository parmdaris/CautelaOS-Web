from functools import wraps
from flask import session, redirect, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash


def login_requerido(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        usuario = session.get("usuario")

        if not usuario:
            return redirect(url_for("login"))

        if usuario.get("u_primeiro_acesso") is True:
            return redirect(url_for("acesso_inicial"))

        return f(*args, **kwargs)

    return decorated


def acesso_requerido(*niveis_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            id_acesso = session.get("nivel_acesso")

            if id_acesso is None:
                return redirect(url_for("login"))

            if id_acesso not in niveis_permitidos:
                abort(403) #forbidden

            return f(*args, **kwargs)
        return decorated_function
    return decorator





def tem_acesso(*niveis): #Verifica se o nivel_acesso do usuario está na tupla "niveis" e retorna true se sim e false se não.
    return session.get("nivel_acesso") in niveis



def checarSenhaHash(hash, senha):
    if check_password_hash(hash, senha):
        return True
    else:
        return False


def gerarSenhaHash(senha):
    senha_hash = generate_password_hash(senha)
    return senha_hash


def verificarAcessoModulo(id_usuario):
    pass
