document.addEventListener("DOMContentLoaded", function () {
    function installProductGallery() {
        const viewer = document.querySelector(".store-main-image");
        const mainImage = viewer ? viewer.querySelector("img") : null;
        if (!viewer || !mainImage) return;

        viewer.classList.add("store-gallery-viewer");
        mainImage.classList.add("store-gallery-main-image");
        mainImage.setAttribute("tabindex", "0");
        mainImage.setAttribute("role", "button");
        mainImage.setAttribute("aria-label", "مشاهده تصویر در اندازه بزرگ");

        const galleryImages = Array.from(
            viewer.parentElement.querySelectorAll(".grid.grid-cols-4 img")
        );
        const sources = [
            { src: mainImage.currentSrc || mainImage.src, alt: mainImage.alt || "تصویر محصول" },
            ...galleryImages.map((img) => ({
                src: img.currentSrc || img.src,
                alt: img.alt || mainImage.alt || "تصویر محصول",
            })),
        ];
        const uniqueSources = [];
        const seen = new Set();
        sources.forEach((item) => {
            if (!item.src || seen.has(item.src)) return;
            seen.add(item.src);
            uniqueSources.push(item);
        });
        if (!uniqueSources.length) return;

        let activeIndex = 0;
        function setActive(index) {
            const normalized = ((index % uniqueSources.length) + uniqueSources.length) % uniqueSources.length;
            activeIndex = normalized;
            const item = uniqueSources[activeIndex];
            mainImage.src = item.src;
            mainImage.alt = item.alt;
            mainImage.classList.add("is-changing");
            window.setTimeout(() => mainImage.classList.remove("is-changing"), 120);
            galleryImages.forEach((thumb) => {
                thumb.classList.toggle("store-gallery-thumb-active", (thumb.currentSrc || thumb.src) === item.src);
            });
        }

        galleryImages.forEach((thumb) => {
            thumb.classList.add("store-gallery-thumb");
            thumb.setAttribute("tabindex", "0");
            thumb.setAttribute("role", "button");
            thumb.setAttribute("aria-label", "نمایش این تصویر در قاب اصلی");
            const activate = () => {
                const src = thumb.currentSrc || thumb.src;
                const index = uniqueSources.findIndex((item) => item.src === src);
                if (index >= 0) setActive(index);
            };
            thumb.addEventListener("click", activate);
            thumb.addEventListener("keydown", (event) => {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    activate();
                }
            });
        });

        const overlay = document.createElement("div");
        overlay.className = "store-lightbox";
        overlay.setAttribute("aria-hidden", "true");
        overlay.innerHTML = `
            <button type="button" class="store-lightbox-close" aria-label="بستن">×</button>
            <button type="button" class="store-lightbox-nav store-lightbox-prev" aria-label="تصویر قبلی">‹</button>
            <figure class="store-lightbox-figure">
                <img class="store-lightbox-image" alt="">
                <figcaption class="store-lightbox-caption"></figcaption>
            </figure>
            <button type="button" class="store-lightbox-nav store-lightbox-next" aria-label="تصویر بعدی">›</button>
        `;
        document.body.appendChild(overlay);
        const lightboxImage = overlay.querySelector(".store-lightbox-image");
        const lightboxCaption = overlay.querySelector(".store-lightbox-caption");

        function renderLightbox() {
            const item = uniqueSources[activeIndex];
            lightboxImage.src = item.src;
            lightboxImage.alt = item.alt;
            lightboxCaption.textContent = item.alt;
        }
        function openLightbox() {
            renderLightbox();
            overlay.classList.add("is-open");
            overlay.setAttribute("aria-hidden", "false");
            document.documentElement.classList.add("store-lightbox-lock");
            overlay.querySelector(".store-lightbox-close").focus();
        }
        function closeLightbox() {
            overlay.classList.remove("is-open");
            overlay.setAttribute("aria-hidden", "true");
            document.documentElement.classList.remove("store-lightbox-lock");
            mainImage.focus();
        }
        function moveLightbox(step) {
            setActive(activeIndex + step);
            renderLightbox();
        }

        mainImage.addEventListener("click", openLightbox);
        mainImage.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                openLightbox();
            }
        });
        overlay.querySelector(".store-lightbox-close").addEventListener("click", closeLightbox);
        overlay.querySelector(".store-lightbox-prev").addEventListener("click", () => moveLightbox(-1));
        overlay.querySelector(".store-lightbox-next").addEventListener("click", () => moveLightbox(1));
        overlay.addEventListener("click", (event) => {
            if (event.target === overlay) closeLightbox();
        });
        document.addEventListener("keydown", (event) => {
            if (!overlay.classList.contains("is-open")) return;
            if (event.key === "Escape") closeLightbox();
            if (event.key === "ArrowLeft") moveLightbox(-1);
            if (event.key === "ArrowRight") moveLightbox(1);
        });
    }

    function installVariantPricing() {
        const select = document.getElementById("variant-select");
        const breakdown = document.getElementById("price-breakdown");
        const orderButton = document.getElementById("order-variant-button");
        const variantInput = document.getElementById("cart-variant-id");
        if (!select || !breakdown) return;

        const formatToman = (value) => Number(value || 0).toLocaleString("fa-IR") + " تومان";
        const formatNumber = (value) => Number(value || 0).toLocaleString("fa-IR");
        const setText = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        };

        function updatePrice() {
            const option = select.options[select.selectedIndex];
            if (!option || !option.value) {
                breakdown.classList.add("hidden");
                if (orderButton) orderButton.disabled = true;
                if (variantInput) variantInput.value = "";
                return;
            }

            const strategy = option.dataset.pricingStrategy || "legacy";
            const materialCost = Number(option.dataset.materialCost || 0);
            const machineCost = Number(option.dataset.machineCost || 0);
            const supervisionCost = Number(option.dataset.supervisionCost || 0);
            const extra =
                Number(option.dataset.assemblyCost || 0) +
                Number(option.dataset.accessoryCost || 0) +
                Number(option.dataset.postFee || 0) +
                Number(option.dataset.fixedFee || 0) +
                Number(option.dataset.colorAdjustment || 0);

            setText("price-material", formatToman(materialCost));
            setText("price-machine", formatToman(machineCost));
            setText("price-supervision", formatToman(supervisionCost));
            setText("price-extra", formatToman(extra));
            setText("price-total", formatToman(option.dataset.total));

            const color = option.dataset.color ? ` • رنگ ${option.dataset.color}` : "";
            const actualMinutes = Number(option.dataset.printTime || 0);
            const billableMinutes = Number(option.dataset.billableTime || actualMinutes);
            const partWeight = Number(option.dataset.partWeight || 0);
            const supportWeight = Number(option.dataset.supportWeight || 0);
            const chargeableWeight = Number(option.dataset.chargeableWeight || 0);
            const timeText = actualMinutes
                ? `زمان چاپ ${formatNumber(actualMinutes)} دقیقه${billableMinutes !== actualMinutes ? ` • زمان قابل‌محاسبه ${formatNumber(billableMinutes)} دقیقه` : ""}`
                : "";
            const weightText = chargeableWeight
                ? `وزن قابل‌محاسبه ${formatNumber(chargeableWeight)} گرم${partWeight ? ` • قطعه ${formatNumber(partWeight)} گرم` : ""}${supportWeight ? ` • ساپورت ${formatNumber(supportWeight)} گرم` : ""}`
                : "";
            const shippingText = Number(option.dataset.shippingWeight || 0)
                ? `وزن ارسال ${formatNumber(option.dataset.shippingWeight)} گرم`
                : "";
            const commerceBits = [option.dataset.sizeLabel, option.dataset.buildProfileLabel].filter(Boolean);
            setText(
                "variant-meta",
                [...commerceBits, option.dataset.material + color, option.dataset.quality, weightText, shippingText, timeText].filter(Boolean).join(" • ")
            );

            const components = document.getElementById("price-components");
            const formulaNote = document.getElementById("pricing-formula-note");
            if (strategy === "fixed") {
                if (components) components.classList.add("hidden");
                if (formulaNote) formulaNote.textContent = "این گزینه با قیمت قطعی تأییدشده اپراتور عرضه می‌شود؛ هزینه ارسال در مرحله تسویه جدا محاسبه می‌شود.";
            } else {
                if (components) components.classList.remove("hidden");
                if (formulaNote) formulaNote.textContent = "قیمت بر اساس وزن قابل محاسبه متریال، زمان چاپ، نرخ متریال، نظارت و هزینه‌های تکمیلی ثبت‌شده محاسبه می‌شود. هزینه ارسال در مرحله تسویه جدا است.";
            }

            breakdown.classList.remove("hidden");
            if (orderButton) orderButton.disabled = false;
            if (variantInput) variantInput.value = option.value;
        }

        async function hydrateCommerceMetadata() {
            const options = Array.from(select.options).filter((option) => option.value);
            const ids = options.map((option) => option.value).join(",");
            if (!ids) return;
            try {
                const response = await fetch(`/store/api/variant-commerce-options/?ids=${encodeURIComponent(ids)}`, {
                    credentials: "same-origin",
                    headers: { "Accept": "application/json" },
                });
                if (!response.ok) return;
                const payload = await response.json();
                const variants = payload.variants || {};
                options.forEach((option) => {
                    const meta = variants[String(option.value)];
                    if (!meta) return;
                    option.dataset.sizeLabel = meta.size_label || "";
                    option.dataset.buildProfile = meta.build_profile || "";
                    option.dataset.buildProfileLabel = meta.build_profile_label || "";
                    option.dataset.shippingWeight = meta.effective_shipping_weight_grams || "0";
                    const prefix = [meta.size_label, meta.build_profile_label].filter(Boolean).join(" — ");
                    if (prefix && !option.dataset.phase50LabelApplied) {
                        option.textContent = `${prefix} — ${option.textContent}`;
                        option.dataset.phase50LabelApplied = "1";
                    }
                });
                updatePrice();
            } catch (_error) {
                // Variant metadata is an enhancement. Core price/cart behavior
                // remains available if this lightweight endpoint is unavailable.
            }
        }

        select.addEventListener("change", updatePrice);
        updatePrice();
        hydrateCommerceMetadata();
    }

    installProductGallery();
    installVariantPricing();
});
