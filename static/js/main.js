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