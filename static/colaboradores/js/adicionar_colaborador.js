document.addEventListener("DOMContentLoaded", () => {

    const params = new URLSearchParams(window.location.search);

    if (params.get("erro") === "username_existente") {
        alert("⚠️ Este nome de usuário já está em uso.");
    }

    if (params.get("erro") === "True") {
        alert("⚠️ Falha: " + params.get("stack_erro"));
    }

    /* ===============================
       1. Apenas números – Identidade
       =============================== */
    const identidadeInput = document.querySelector('input[name="identidade"]');
    if (identidadeInput) {
        identidadeInput.addEventListener("input", () => {
            identidadeInput.value = identidadeInput.value.replace(/\D/g, "");
        });
    }

    /* ==========================================
       2. Usuário: apenas letras e ".", minúsculo
       ========================================== */
    const usuarioInput = document.querySelector('input[name="usuario"]');
    if (usuarioInput) {
        usuarioInput.addEventListener("input", () => {
            usuarioInput.value = usuarioInput.value
                .toLowerCase()
                .replace(/[^a-z.]/g, "");
        });
    }

    /* ==================================
       3. Carregar cargos (JSON embutido)
       ================================== */
    const selectNivel = document.querySelector('select[name="nivel_acesso"]');
    const cargosScript = document.getElementById("cargos-json");

    if (selectNivel && cargosScript) {
        const cargos = JSON.parse(cargosScript.textContent);

        cargos.forEach(cargo => {
            const option = document.createElement("option");
            option.value = cargo.id_cargo;
            option.textContent = cargo.cargo;
            selectNivel.appendChild(option);
        });
    }

    /* ==================================
       Validação REAL da confirmação de senha
       ================================== */
    const senha = document.getElementById("senha");
    const confirma = document.getElementById("confirma_senha");

    function validarSenha() {
        if (!senha || !confirma) return;

        if (senha.value !== confirma.value) {
            confirma.setCustomValidity("As senhas não conferem");
        } else {
            confirma.setCustomValidity("");
        }
    }

    if (senha && confirma) {
        senha.addEventListener("input", validarSenha);
        confirma.addEventListener("input", validarSenha);
    }

});

    