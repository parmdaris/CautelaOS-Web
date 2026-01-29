document.addEventListener("DOMContentLoaded", () => {

    const badge = document.querySelector(".badge-cargo");
    if (!badge) return;

    const idAcesso = parseInt(badge.dataset.idAcesso, 10);

    switch (idAcesso) {
        case 1:
            badge.classList.add("badge-admin");
            break;

        case 2:
            badge.classList.add("badge-operador");
            break;

        case 3:
            badge.classList.add("badge-tecnico");
            break;

        case 4:
            badge.classList.add("badge-consulta");
            break;

        default:
            badge.classList.add("badge-default");
    }
});