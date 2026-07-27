(function () {
    "use strict";

    function qs(selector, root) {
        return (root || document).querySelector(selector);
    }

    function qsa(selector, root) {
        return Array.prototype.slice.call((root || document).querySelectorAll(selector));
    }

    function initSliders() {
        qsa("[data-p13-slider-shell]").forEach(function (shell) {
            var track = qs("[data-p13-slider]", shell);
            if (!track) return;
            var step = function () {
                var first = track.firstElementChild;
                return first ? first.getBoundingClientRect().width + 18 : 340;
            };
            var next = qs("[data-p13-next]", shell);
            var prev = qs("[data-p13-prev]", shell);
            if (next) next.addEventListener("click", function () {
                track.scrollBy({ left: -step(), behavior: "smooth" });
            });
            if (prev) prev.addEventListener("click", function () {
                track.scrollBy({ left: step(), behavior: "smooth" });
            });
        });
    }

    function initOrderWizard() {
        var form = qs("[data-p13-order-form]");
        if (!form) return;

        var panels = qsa("[data-p13-panel]", form);
        var stepButtons = qsa("[data-p13-step]", form);
        var nextButtons = qsa("[data-p13-next-step]", form);
        var prevButtons = qsa("[data-p13-prev-step]", form);
        var current = 1;

        function showStep(step) {
            current = Math.max(1, Math.min(step, panels.length));
            panels.forEach(function (panel) {
                panel.hidden = Number(panel.getAttribute("data-p13-panel")) !== current;
            });
            stepButtons.forEach(function (button) {
                button.classList.toggle(
                    "is-active",
                    Number(button.getAttribute("data-p13-step")) === current
                );
            });
            form.setAttribute("data-current-step", String(current));
            var top = form.getBoundingClientRect().top + window.scrollY - 110;
            if (window.scrollY > top + 300) {
                window.scrollTo({ top: top, behavior: "smooth" });
            }
        }

        function mode() {
            var selected = qs('input[name="request_mode"]:checked', form);
            return selected ? selected.value : "new_part";
        }

        function updateMode() {
            var value = mode();
            qsa("[data-p13-new-part-only]", form).forEach(function (element) {
                element.hidden = value !== "new_part";
            });
            qsa("[data-p13-reorder-only]", form).forEach(function (element) {
                element.hidden = value !== "reorder_model";
            });
            qsa("[data-p13-ready-only]", form).forEach(function (element) {
                element.hidden = value !== "ready_catalog";
            });
        }

        function validateCurrentStep() {
            var panel = qs('[data-p13-panel="' + current + '"]', form);
            if (!panel) return true;
            var required = qsa("input[required], select[required], textarea[required]", panel);
            for (var i = 0; i < required.length; i += 1) {
                if (!required[i].checkValidity()) {
                    required[i].reportValidity();
                    return false;
                }
            }
            if (current === 4 && mode() === "new_part") {
                var photoNames = ["photo_top", "photo_front", "photo_right", "photo_left"];
                for (var j = 0; j < photoNames.length; j += 1) {
                    var input = qs('[name="' + photoNames[j] + '"]', form);
                    if (input && (!input.files || !input.files.length)) {
                        input.setCustomValidity("این تصویر برای سفارش قطعه جدید الزامی است.");
                        input.reportValidity();
                        input.addEventListener("change", function clearMessage(event) {
                            event.target.setCustomValidity("");
                            event.target.removeEventListener("change", clearMessage);
                        });
                        return false;
                    }
                }
            }
            return true;
        }

        stepButtons.forEach(function (button) {
            button.addEventListener("click", function () {
                var requested = Number(button.getAttribute("data-p13-step"));
                if (requested <= current || validateCurrentStep()) showStep(requested);
            });
        });

        nextButtons.forEach(function (button) {
            button.addEventListener("click", function () {
                if (validateCurrentStep()) showStep(current + 1);
            });
        });

        prevButtons.forEach(function (button) {
            button.addEventListener("click", function () {
                showStep(current - 1);
            });
        });

        qsa('input[name="request_mode"]', form).forEach(function (input) {
            input.addEventListener("change", updateMode);
        });

        qsa('input[type="file"]', form).forEach(function (input) {
            input.addEventListener("change", function () {
                var field = input.closest(".p13-photo-field");
                var label = field ? qs("[data-p13-file-name]", field) : null;
                var file = input.files && input.files[0];
                if (field) field.classList.toggle("is-filled", Boolean(file));
                if (label) label.textContent = file ? file.name : "فایلی انتخاب نشده است";
            });
        });

        var material = qs("#id_material", form);
        var materialPreview = qs("[data-p13-material-preview]", form);
        function updateMaterialPreview() {
            if (!material || !materialPreview) return;
            var option = material.options[material.selectedIndex];
            var price = option ? option.getAttribute("data-price-gram") : "";
            var name = option ? option.textContent.trim() : "";
            materialPreview.textContent = price
                ? name + " — قیمت فروش هر گرم: " + Number(price).toLocaleString("fa-IR") + " تومان"
                : "قیمت نهایی پس از انتخاب متریال و بررسی فنی اعلام می‌شود.";
        }
        if (material) material.addEventListener("change", updateMaterialPreview);

        if (qs(".p13-form-error", form)) {
            var firstError = qs(".errorlist, .p13-form-error", form);
            var containingPanel = firstError && firstError.closest("[data-p13-panel]");
            if (containingPanel) current = Number(containingPanel.getAttribute("data-p13-panel"));
        }

        updateMode();
        updateMaterialPreview();
        showStep(current);
    }

    function initCatalogFilters() {
        var form = qs("[data-p13-catalog-filter]");
        if (!form) return;
        qsa("select", form).forEach(function (select) {
            select.addEventListener("change", function () { form.submit(); });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        initSliders();
        initOrderWizard();
        initCatalogFilters();
    });
})();

// Private technical documents preview
(function () {
    var input = document.getElementById("id_documents");
    var output = document.querySelector("[data-p13-document-list]");
    if (!input || !output) return;
    input.addEventListener("change", function () {
        output.innerHTML = "";
        Array.from(input.files || []).forEach(function (file) {
            var item = document.createElement("div");
            item.className = "p13-document-item";
            item.textContent = file.name + " — " + (file.size / 1024 / 1024).toFixed(2) + " MB";
            output.appendChild(item);
        });
    });
})();
