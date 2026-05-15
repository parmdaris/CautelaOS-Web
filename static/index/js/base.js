document.addEventListener("DOMContentLoaded", () => {

    /* ===== SIDEBAR ACCORDION ===== */
    const menuItems = document.querySelectorAll(".menu-item");
    const toggles = document.querySelectorAll(".menu-toggle");
    const currentPath = window.location.pathname;

    // clique manual (accordion: só um aberto)
    toggles.forEach(toggle => {
        toggle.addEventListener("click", () => {
            const currentItem = toggle.closest(".menu-item");

            menuItems.forEach(item => {
                if (item !== currentItem) {
                    item.classList.remove("open");
                }
            });

            currentItem.classList.toggle("open");
        });
    });

    // autoabrir + highlight conforme rota
    document.querySelectorAll(".submenu a, .sidebar-menu > a").forEach(link => {
        const href = link.getAttribute("href");

        if (href === currentPath) {
            link.classList.add("active");

            const parentItem = link.closest(".menu-item");
            if (parentItem) {
                parentItem.classList.add("open");
            }
        }
    });


});

