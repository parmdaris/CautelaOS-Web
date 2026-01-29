$(document).ready(function () {

    const tabela = $('#tabela-estoque').DataTable({
        pageLength: 25,
        autoWidth: false,
        responsive: true,
        dom: 'lftip',
        language: {
            lengthMenu: "Mostrar _MENU_ itens",
            zeroRecords: "Nenhum resultado encontrado",
            info: "Página _PAGE_ de _PAGES_",
            infoEmpty: "Nenhum item disponível",
            infoFiltered: "(filtrado de _MAX_ itens)",
            search: "Buscar:",
            paginate: {
                next: "Próxima",
                previous: "Anterior"
            }
        }
    });

    const tipos = JSON.parse(
        document.getElementById("tipos-itens").textContent
    );

    const filtroTipo = $('<select class="tipo-select" name="tipo-select">' +
        '<option value="">Todos</option>' +
    '</select>');

    tipos.forEach(tipo => {
        filtroTipo.append(`<option value="${tipo}">${tipo}</option>`);
    });

    filtroTipo.on('change', function () {
        const valor = this.value;

    tabela.column(2).search(valor).draw();

    document.getElementById('tipo-filtro').value = valor;
    });

    const lengthLabel = $('.dataTables_length label');

    lengthLabel.append(`
        <span style="margin-left: 12px;">Tipo:</span>
    `);

    lengthLabel.append(filtroTipo);
});
