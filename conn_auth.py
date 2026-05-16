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




def permissao_requerida(*permissoes_requeridas):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            usuario = session.get("usuario")

            if not usuario:
                return redirect(url_for("login"))

            permissoes_usuario = set(usuario.get("funcoes_habilitadas") or [])

            if not permissoes_usuario.intersection(permissoes_requeridas):
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator



def macrofuncao_requerida(*macrofuncoes_requeridas):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            modulo = session.get("modulo")
            usuario = session.get("usuario")

            if not modulo:
                return redirect(url_for("selecionar_modulo"))

            macrofuncoes_modulo = set(modulo.get("macrofuncoes") or [])
            macrofuncoes_usuario = set(usuario.get("macrofuncoes_habilitadas"))

            if not macrofuncoes_modulo.intersection(macrofuncoes_requeridas):
                abort(403)

            if not macrofuncoes_usuario.intersection(macrofuncoes_requeridas):
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator




def tem_acesso(*permissoes): #Verifica se o nivel_acesso do usuario está na tupla "permissoes" e retorna true se sim e false se não.
    return session.get("nivel_acesso") in permissoes



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
