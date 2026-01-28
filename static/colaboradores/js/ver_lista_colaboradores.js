$(document).ready(function () {
    $('#tabela-colabs').DataTable({
        pageLength: 25,
        autoWidth: false,
        responsive: true,
        dom: 'lftrip',
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
