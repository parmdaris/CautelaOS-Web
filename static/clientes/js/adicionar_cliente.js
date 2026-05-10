document.addEventListener("DOMContentLoaded", () => {

    const params = new URLSearchParams(window.location.search);

    if (params.get("erro") === "username_existente") {
        alert("⚠️ Este nome de usuário já está em uso.");
    }

    if (params.get("erro") === "True") {
        alert("⚠️ Falha: " + params.get("stack_erro"));
    }


    const identidadeInput = document.querySelector('input[name="identidade"]');
    if (identidadeInput) {
        identidadeInput.addEventListener("input", () => {
            identidadeInput.value = identidadeInput.value.replace(/\D/g, "");
        });
    }


    const usuarioInput = document.querySelector('input[name="usuario"]');
    if (usuarioInput) {
        usuarioInput.addEventListener("input", () => {
            usuarioInput.value = usuarioInput.value
                .toLowerCase()
                .replace(/[^a-z.]/g, "");
        });
    }


    const selectNivel = document.querySelector('select[name="nivel_acesso"]');
    const cargosScript = document.getElementById("cargos-json");

    if (selectNivel && cargosScript) {
        const cargos = JSON.parse(cargosScript.textContent);

        cargos.forEach(cargo => {
            const option = document.createElement("option");
            option.value = cargo.id_acesso;
            option.textContent = cargo.cargo;
            selectNivel.appendChild(option);
        });
    }

});

    