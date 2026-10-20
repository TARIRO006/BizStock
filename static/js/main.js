const menuToggle = document.getElementById("menuToggle");
const sidebar = document.getElementById("sidebar");

if (menuToggle && sidebar) {

    // Open / close sidebar using hamburger button
    menuToggle.addEventListener("click", function () {
        sidebar.classList.toggle("active");
    });

    // Close sidebar when clicking a navigation link
    const navLinks = sidebar.querySelectorAll(".nav-link");

    navLinks.forEach(function (link) {
        link.addEventListener("click", function () {
            sidebar.classList.remove("active");
        });
    });

    // Close sidebar when clicking Logout
    const logoutLink = sidebar.querySelector(".logout-link");

    if (logoutLink) {
        logoutLink.addEventListener("click", function () {
            sidebar.classList.remove("active");
        });
    }

    // Close sidebar when clicking outside it
    document.addEventListener("click", function (event) {

        const clickedInsideSidebar = sidebar.contains(event.target);
        const clickedMenuButton = menuToggle.contains(event.target);

        if (
            sidebar.classList.contains("active") &&
            !clickedInsideSidebar &&
            !clickedMenuButton
        ) {
            sidebar.classList.remove("active");
        }
    });
}



document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('sale-items');
    const addButton = document.getElementById('add-sale-item');
    const template = document.getElementById('empty-sale-item');
    const totalForms = document.getElementById('id_items-TOTAL_FORMS');

    if (!container || !addButton || !template || !totalForms) {
        return;
    }

    addButton.addEventListener('click', function () {
        const index = Number(totalForms.value);
        const html = template.innerHTML.replace(
            /__prefix__/g,
            index
        );

        container.insertAdjacentHTML('beforeend', html);
        totalForms.value = index + 1;
    });

    container.addEventListener('click', function (event) {
        const button = event.target.closest('.remove-sale-item');

        if (!button) {
            return;
        }

        const rows = container.querySelectorAll('.sale-item-row');

        if (rows.length <= 1) {
            alert('At least one product row must remain.');
            return;
        }

        button.closest('.sale-item-row').remove();
        // Do not decrement TOTAL_FORMS: Django uses the submitted
        // indexes to identify the remaining form rows.
    });
});
