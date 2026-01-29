function formatarMoedaBR(input) {
    let valor = input.value.replace(/\D/g, '');

    valor = (valor / 100).toFixed(2);
    valor = valor.replace('.', ',');
    valor = valor.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

    input.value = 'R$ ' + valor;
}

document.getElementById("codigo").addEventListener("input", function () {
    this.value = this.value
        .toUpperCase()
        .replace(/[^A-Z0-9-]/g, "");
});

document.addEventListener("DOMContentLoaded", function () {

    const params = new URLSearchParams(window.location.search);

    if (params.get("erro") === "sku_existente") {
        alert("⚠️ Este SKU já está cadastrado no sistema.");
    }

    if (params.get("erro") === false) {
        alert("⚠️ Falha na adição do item. Entre em contato com o administrador.");
    }

    
    const header = document.querySelector("header p");
    if (header && typeof nomeOperador !== "undefined") {
        header.textContent = `Operador: ${nomeOperador}`;
    }


    const camposMoeda = [
        document.getElementById("valor"),
        document.getElementById("valor_atacado")
    ];

    camposMoeda.forEach(campo => {
        if (!campo) return;

        campo.value = '0';
        formatarMoedaBR(campo);

        campo.addEventListener("input", () => {
            formatarMoedaBR(campo);
        });
    });


    const tiposItens = JSON.parse(
        document.getElementById("tipos-itens").textContent
    );

    document.querySelectorAll('select[name="tipo"]').forEach(select => {

        const selecionado = select.dataset.selected || null;

        tiposItens.forEach(tipo => {
            const option = document.createElement("option");
            option.value = tipo;
            option.textContent = tipo;

            if (tipo === selecionado) {
                option.selected = true;
            }

            select.appendChild(option);
        });

    });

});
