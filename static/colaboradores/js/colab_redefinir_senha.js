const admin_pw = document.getElementById('senha-admin');
    const conf = document.getElementById('confirmar-senha');
    const erro = document.getElementById('erro-confirmacao');
    const form = document.getElementById('form-senha');

    function validar() {
        if (!conf.value) {
            erro.style.display = 'none';
            conf.classList.remove('input-erro');
            return;
        }

        if (admin_pw.value !== conf.value) {
            erro.style.display = 'block';
            conf.classList.add('input-erro');
        } else {
            erro.style.display = 'none';
            conf.classList.remove('input-erro');
        }
    }

    erro.classList.add('ativo');
    erro.classList.remove('ativo');

    admin_pw.addEventListener('input', validar);
    conf.addEventListener('input', validar);

    form.addEventListener('submit', function (e) {
        if (admin_pw.value !== conf.value) {
            e.preventDefault();
            validar();
        }
    }
    
    
    );