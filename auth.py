from functools import wraps
from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def gerarSenhaHash(senha):
    senha_hash = generate_password_hash(senha)
    #print("Hash: ", senha_hash)

    return senha_hash