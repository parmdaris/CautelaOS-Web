function formatarMoedaBR(input) {
    let valor = input.value.replace(/\D/g, '');

    if (valor === '') valor = '0';

    valor = (valor / 100).toFixed(2);
    valor = valor.replace('.', ',');
    valor = valor.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

    input.value = 'R$ ' + valor;
}

document.addEventListener("DOMContentLoaded", function () {
    const tiposItens = JSON.parse(
        document.getElementById("tipos-itens").textContent
    );

    document.querySelectorAll('select[name="tipo_item"]').forEach(select => {
        const selecionado = select.dataset.selected;

        tiposItens.forEach(tipo => {
            const option = document.createElement('option');
            option.value = tipo;
            option.textContent = tipo;

            if (tipo === selecionado) {
                option.selected = true;
            }

            select.appendChild(option);
        });
    });

    const valor = document.getElementById("valor");
    const valorAtacado = document.getElementById("valor_atacado");

    [valor, valorAtacado].forEach(campo => {
        if (!campo) return;

        if (campo.value) {
            formatarMoedaBR(campo);
        }

        campo.addEventListener("input", () => formatarMoedaBR(campo));
    });


    document.getElementById("novo_codigo").addEventListener("input", function () {
    this.value = this.value
        .toUpperCase()
        .replace(/[^A-Z0-9-]/g, "");
    });
});
