$(document).ready(function () {
    $('#tabela-estoque').DataTable({
        pageLength: 25,
        autoWidth: false,
        responsive: true,
        dom: 'lftrip', // MOSTRA: length, filter, table, info, pagination
        columnDefs: [
            { targets: 2, visible: false, searchable: true }
        ],
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
});
