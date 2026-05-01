document.addEventListener("DOMContentLoaded", () => {
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