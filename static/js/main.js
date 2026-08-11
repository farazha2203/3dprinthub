document.addEventListener("DOMContentLoaded", function () {
    function scrollToSection(sectionId) {
        const target = document.getElementById(sectionId);

        if (!target) {
            console.warn("Section not found:", sectionId);
            return false;
        }

        const headerOffset = 105;
        const elementPosition = target.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
            top: offsetPosition,
            behavior: "smooth"
        });

        history.replaceState(null, "", "#" + sectionId);

        return true;
    }

    /*
    |--------------------------------------------------------------------------
    | Header / internal links
    |--------------------------------------------------------------------------
    */
    const scrollLinks = document.querySelectorAll("[data-scroll-to]");

    scrollLinks.forEach(function (link) {
        link.addEventListener("click", function (event) {
            const sectionId = link.getAttribute("data-scroll-to");

            if (!sectionId) {
                return;
            }

            const isHomePage = window.location.pathname === "/" || window.location.pathname === "";

            if (isHomePage) {
                event.preventDefault();
                scrollToSection(sectionId);
            }
        });
    });

    /*
    |--------------------------------------------------------------------------
    | If page opened with hash
    |--------------------------------------------------------------------------
    */
    if (window.location.hash) {
        const sectionId = window.location.hash.replace("#", "");

        setTimeout(function () {
            scrollToSection(sectionId);
        }, 250);
    }

    /*
    |--------------------------------------------------------------------------
    | Mobile menu
    |--------------------------------------------------------------------------
    */
    const mobileMenuButton = document.getElementById("mobile-menu-button");
    const mobileMenu = document.getElementById("mobile-menu");
    const mobileMenuLinks = document.querySelectorAll(".mobile-menu-link");

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener("click", function () {
            mobileMenu.classList.toggle("is-open");
        });

        mobileMenuLinks.forEach(function (link) {
            link.addEventListener("click", function () {
                mobileMenu.classList.remove("is-open");
            });
        });
    }

    /*
    |--------------------------------------------------------------------------
    | Material price preview
    |--------------------------------------------------------------------------
    */
    const materialSelect = document.getElementById("id_material");
    const previewBox = document.getElementById("material-price-preview");
    const previewName = document.getElementById("material-preview-name");
    const previewKg = document.getElementById("material-preview-kg");
    const previewGram = document.getElementById("material-preview-gram");

    function formatNumber(value) {
        if (!value || Number(value) === 0) {
            return "استعلامی";
        }

        return Number(value).toLocaleString("fa-IR") + " تومان";
    }

    function updateMaterialPreview() {
        if (!materialSelect || !previewBox) {
            return;
        }

        const selectedOption = materialSelect.options[materialSelect.selectedIndex];

        if (!selectedOption || !selectedOption.value) {
            previewBox.classList.add("hidden");
            return;
        }

        const name = selectedOption.dataset.name || selectedOption.textContent.trim();
        const priceKg = selectedOption.dataset.priceKg || "0";
        const priceGram = selectedOption.dataset.priceGram || "0";

        if (previewName) previewName.textContent = name;
        if (previewKg) previewKg.textContent = formatNumber(priceKg);
        if (previewGram) previewGram.textContent = formatNumber(priceGram);

        previewBox.classList.remove("hidden");
    }

    if (materialSelect) {
        materialSelect.addEventListener("change", updateMaterialPreview);
        updateMaterialPreview();
    }
});