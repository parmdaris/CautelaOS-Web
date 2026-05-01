$(document).ready(function () {

    $('#tabela-vendas').DataTable({
        pageLength: 25,
        autoWidth: false,
        responsive: true,
        dom: 'lftip',
        order: [[0, "desc"]],
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
