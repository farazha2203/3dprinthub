(function () {
    "use strict";

    const MODE_DIMENSIONS = {
        list: ["profile"],
        size: ["size"],
        weight: ["weight"],
        build: ["build"],
        size_build: ["size", "build"],
        build_size: ["build", "size"],
        size_weight: ["size", "weight"],
        weight_size: ["weight", "size"],
        size_weight_build: ["size", "weight", "build"],
        size_build_weight: ["size", "build", "weight"],
    };

    const LABELS = {
        profile: "پروفایل محصول",
        size: "سایز / ابعاد",
        weight: "وزن",
        build: "مدل ساخت",
        brand: "برند فیلامنت",
        material: "فیلامنت / متریال",
        color: "رنگ فیلامنت",
        quality: "کیفیت چاپ",
    };

    const formatNumber = (value) => Number(value || 0).toLocaleString("fa-IR");
    const formatToman = (value) => `${formatNumber(value)} تومان`;
    const clean = (value) => String(value == null ? "" : value).trim();
    const escapeHtml = (value) => clean(value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    }[char]));


    function readNativeOption(option, metadata) {
        const meta = metadata || {};
        const finalWeight = Number(meta.final_weight_grams || option.dataset.partWeight || 0);
        const materialWeight = Number(meta.material_weight_grams || option.dataset.chargeableWeight || 0);
        const shippingWeight = Number(meta.effective_shipping_weight_grams || option.dataset.shippingWeight || finalWeight || materialWeight || 0);
        const profileLabel = clean(meta.profile_label || meta.profile_name || meta.selection_value || "");
        return {
            id: String(option.value),
            option,
            profileKey: clean(meta.profile_key || option.value),
            profileLabel: profileLabel || clean(option.textContent),
            profileDescription: clean(meta.profile_description || ""),
            isDefault: Boolean(meta.profile_is_default),
            size: clean(meta.size_label || option.dataset.sizeLabel),
            build: clean(meta.build_profile || option.dataset.buildProfile),
            buildLabel: clean(meta.build_profile_label || option.dataset.buildProfileLabel),
            material: clean(meta.material || option.dataset.material),
            color: clean(meta.color || option.dataset.color),
            filamentBrand: clean(meta.filament_brand_name || option.dataset.filamentBrand || ""),
            colorHex: clean(meta.color_hex || ""),
            colorSecondaryHex: clean(meta.color_secondary_hex || ""),
            colorTertiaryHex: clean(meta.color_tertiary_hex || ""),
            colorType: clean(meta.color_type || "solid"),
            colorTypeLabel: clean(meta.color_type_label || ""),
            colorFinish: clean(meta.color_finish || "matte"),
            colorFinishLabel: clean(meta.color_finish_label || ""),
            colorPalette: Array.isArray(meta.color_palette_hexes)
                ? meta.color_palette_hexes.map(clean).filter((value) => /^#[0-9a-f]{6}$/i.test(value)).slice(0, 7)
                : [],
            filamentImage: clean(meta.filament_image_url || ""),
            filamentRollWeight: Number(meta.filament_roll_weight_grams || 0),
            filamentSalePricePerRoll: Number(meta.filament_sale_price_per_roll || 0),
            filamentSalePricePerGram: Number(meta.filament_sale_price_per_gram || 0),
            currentStockGrams: Number(meta.current_stock_grams || 0),
            orderable: meta.orderable !== false,
            preheatHours: Number(meta.preheat_hours || 0),
            preheatTemperature: Number(meta.preheat_temperature_c || 0),
            quality: clean(meta.quality || option.dataset.quality),
            finalWeight,
            supportWeight: Number(meta.support_weight_grams || option.dataset.supportWeight || 0),
            materialWeight,
            shippingWeight,
            packagingWeight: Number(meta.packaging_weight_grams || 0),
            printMinutes: Number(meta.print_time_minutes || option.dataset.printTime || 0),
            price: Number(meta.unit_price || option.dataset.total || 0),
            partLength: Number(meta.part_length_cm || 0),
            partWidth: Number(meta.part_width_cm || 0),
            partHeight: Number(meta.part_height_cm || 0),
            partDimensionsLabel: clean(meta.part_dimensions_label || ""),
            packageLength: Number(meta.package_length_cm || 0),
            packageWidth: Number(meta.package_width_cm || 0),
            packageHeight: Number(meta.package_height_cm || 0),
        };
    }

    function valueFor(variant, dim) {
        if (dim === "profile") return variant.profileKey || variant.id;
        if (dim === "size") return variant.size;
        if (dim === "weight") return String(variant.finalWeight || variant.materialWeight || 0);
        if (dim === "build") return variant.build;
        if (dim === "brand") return variant.filamentBrand || "بدون برند";
        if (dim === "material") return variant.material;
        if (dim === "color") return variant.color;
        if (dim === "quality") return variant.quality;
        return "";
    }

    function labelFor(variant, dim) {
        if (dim === "profile") return variant.profileLabel;
        if (dim === "size") return variant.size || "بدون سایز";
        if (dim === "weight") {
            const value = variant.finalWeight || variant.materialWeight || 0;
            return value ? `${formatNumber(value)} گرم` : "وزن ثبت‌نشده";
        }
        if (dim === "build") return variant.buildLabel || variant.build || "استاندارد";
        if (dim === "brand") return variant.filamentBrand || "بدون برند";
        if (dim === "material") return variant.material || "بدون متریال";
        if (dim === "color") {
            const finish = variant.colorFinishLabel || variant.colorFinish || "";
            return `${variant.color || "بدون رنگ"}${finish ? ` — ${finish}` : ""}`;
        }
        if (dim === "quality") return variant.quality || "استاندارد";
        return "";
    }

    function uniqueOptions(variants, dim) {
        const map = new Map();
        variants.forEach((variant) => {
            const value = valueFor(variant, dim);
            if (!value && dim !== "weight") return;
            if (!map.has(value)) map.set(value, { label: labelFor(variant, dim), variant });
        });
        return Array.from(map.entries()).map(([value, meta]) => ({
            value,
            label: meta.label,
            variant: meta.variant,
        }));
    }

    function buildDimensions(mode, variants) {
        const dimensions = [...(MODE_DIMENSIONS[mode] || MODE_DIMENSIONS.size_build)];
        ["weight", "brand", "material", "color", "quality"].forEach((dim) => {
            if (dimensions.includes(dim)) return;
            if (uniqueOptions(variants, dim).length > 1) dimensions.push(dim);
        });
        return dimensions.filter((dim) => uniqueOptions(variants, dim).length > 0);
    }

    function matching(variants, state, exceptDim) {
        return variants.filter((variant) => {
            return Object.entries(state).every(([dim, value]) => {
                if (!value || dim === exceptDim) return true;
                return valueFor(variant, dim) === value;
            });
        });
    }

    function upstreamState(state, dimensions, endExclusive) {
        const scoped = {};
        dimensions.slice(0, endExclusive).forEach((dim) => {
            if (state[dim]) scoped[dim] = state[dim];
        });
        return scoped;
    }

    function variantsForDimension(variants, state, dimensions, dimIndex) {
        return matching(variants, upstreamState(state, dimensions, dimIndex));
    }

    function clearDownstreamState(state, dimensions, dimIndex) {
        dimensions.slice(dimIndex + 1).forEach((dim) => {
            delete state[dim];
        });
    }

    const TEST_API = {
        MODE_DIMENSIONS,
        buildDimensions,
        matching,
        upstreamState,
        variantsForDimension,
        clearDownstreamState,
        valueFor,
        uniqueOptions,
    };

    if (typeof module !== "undefined" && module.exports) {
        module.exports = TEST_API;
    }
    if (typeof document === "undefined") return;

    function installSelector(select, payload) {
        if (!select || select.dataset.phase50ProfileReady === "1") return;
        const optionNodes = Array.from(select.options).filter((option) => option.value && !option.disabled);
        if (!optionNodes.length) return;

        const variantsMap = payload && payload.variants ? payload.variants : {};
        const variants = optionNodes.map((option) => readNativeOption(option, variantsMap[String(option.value)]));
        if (!variants.length) return;

        const firstProductId = clean((variantsMap[variants[0].id] || {}).product_id);
        const productMeta = (payload && payload.products && payload.products[firstProductId]) || {};
        const mode = clean(productMeta.selection_mode || "size_build");
        const selectorLabel = clean(productMeta.selector_label || "") || "انتخاب مشخصات محصول";
        const dimensions = buildDimensions(mode, variants);
        if (!dimensions.length) return;

        const label = document.querySelector('label[for="variant-select"]');
        if (label) label.classList.add("store-profile-original-label");

        const shell = document.createElement("section");
        shell.className = "store-profile-selector";
        shell.setAttribute("aria-label", selectorLabel);
        shell.innerHTML = `
            <div class="store-profile-selector__head">
                <div>
                    <h3>${escapeHtml(selectorLabel)}</h3>
                    <p>پروفایل/سایز را انتخاب کنید؛ سپس برند، فیلامنت و رنگ/Finish موجود را مشخص کنید. قیمت فقط پس از کامل‌شدن مسیر انتخاب نمایش داده می‌شود.</p>
                </div>
                <span class="store-profile-selector__badge">پروفایل فروش</span>
            </div>
            <div class="store-profile-controls" data-profile-controls></div>
            <div class="store-profile-summary" data-profile-summary></div>
        `;
        if (label && label.parentNode) {
            label.parentNode.insertBefore(shell, label);
        } else if (select.parentNode) {
            select.parentNode.insertBefore(shell, select);
        }

        const fallback = document.createElement("details");
        fallback.className = "store-profile-native-fallback";
        fallback.innerHTML = `<summary>فهرست کامل پروفایل‌ها</summary><div class="store-profile-native-fallback__body"></div>`;
        const fallbackBody = fallback.querySelector(".store-profile-native-fallback__body");
        select.parentNode.insertBefore(fallback, select);
        fallbackBody.appendChild(select);

        const controls = shell.querySelector("[data-profile-controls]");
        const summary = shell.querySelector("[data-profile-summary]");
        const state = {};

        function syncStateToVariant(variant) {
            dimensions.forEach((dim) => {
                state[dim] = valueFor(variant, dim);
            });
        }

        function chooseVariant(variant) {
            if (!variant) return;
            syncStateToVariant(variant);
            select.value = variant.id;
            select.dispatchEvent(new Event("change", { bubbles: true }));
            render();
        }

        function selectionComplete() {
            return dimensions.every((dim) => state[dim] !== undefined && state[dim] !== "");
        }

        function selectedVariant() {
            if (!selectionComplete()) return null;
            const exact = matching(variants, state).filter((variant) => variant.orderable !== false);
            if (exact.length === 1) return exact[0];
            const current = variants.find((variant) => variant.id === select.value);
            if (current && exact.includes(current)) return current;
            return exact.find((variant) => variant.isDefault) || exact[0] || null;
        }

        function autoFillSingletons() {
            dimensions.forEach((dim, index) => {
                if (state[dim]) return;
                const possible = variantsForDimension(variants, state, dimensions, index);
                const options = uniqueOptions(possible.length ? possible : variants, dim);
                const orderable = options.filter((item) => {
                    const optionVariants = (possible.length ? possible : variants)
                        .filter((variant) => valueFor(variant, dim) === item.value);
                    return optionVariants.some((variant) => variant.orderable !== false);
                });
                if (orderable.length === 1) state[dim] = orderable[0].value;
            });
        }

        function renderSummary(variant) {
            if (!variant) {
                summary.innerHTML = `<div class="text-sm text-slate-500">برای مشاهده قیمت و مشخصات، یک پروفایل را انتخاب کنید.</div>`;
                return;
            }
            const partText = variant.partDimensionsLabel || (
                [variant.partLength, variant.partWidth, variant.partHeight].some(Boolean)
                    ? `${formatNumber(variant.partLength)} × ${formatNumber(variant.partWidth)} × ${formatNumber(variant.partHeight)} سانتی‌متر`
                    : "طبق پروفایل"
            );
            const packageText = [variant.packageLength, variant.packageWidth, variant.packageHeight].some(Boolean)
                ? `${formatNumber(variant.packageLength)} × ${formatNumber(variant.packageWidth)} × ${formatNumber(variant.packageHeight)} سانتی‌متر`
                : "طبق تنظیمات سفارش";
            const facts = [
                ["پروفایل", variant.profileLabel],
                ["سایز", variant.size || "—"],
                ["مدل ساخت", variant.buildLabel || variant.build || "استاندارد"],
                ["متریال", variant.material || "—"],
                ...(variant.filamentBrand ? [["برند فیلامنت", variant.filamentBrand]] : []),
                ["رنگ", variant.color || "—"],
                ...(variant.colorTypeLabel ? [["رفتار رنگ", variant.colorTypeLabel]] : []),
                ...(variant.colorFinishLabel ? [["Finish", variant.colorFinishLabel]] : []),
                ...(variant.filamentRollWeight ? [["وزن رول", `${formatNumber(variant.filamentRollWeight)} گرم`]] : []),
                ...(variant.filamentSalePricePerRoll ? [["قیمت فروش رول", formatToman(variant.filamentSalePricePerRoll)]] : []),
                ...(variant.filamentSalePricePerGram ? [["قیمت خودکار هر گرم", `${formatToman(variant.filamentSalePricePerGram)}/گرم`]] : []),
                ["موجودی فیلامنت", variant.currentStockGrams ? `${formatNumber(variant.currentStockGrams)} گرم` : "ناموجود"],
                ...(variant.preheatHours ? [["پیش‌گرم", `${formatNumber(variant.preheatHours)} ساعت${variant.preheatTemperature ? ` در ${formatNumber(variant.preheatTemperature)}°C` : ""}`]] : []),
                ["کیفیت چاپ", variant.quality || "—"],
                ["وزن قطعه", variant.finalWeight ? `${formatNumber(variant.finalWeight)} گرم` : "—"],
                ...(variant.supportWeight ? [["وزن ساپورت", `${formatNumber(variant.supportWeight)} گرم`]] : []),
                ["ابعاد قطعه", partText],
                ["وزن ارسال", variant.shippingWeight ? `${formatNumber(variant.shippingWeight)} گرم` : "—"],
                ["زمان چاپ", variant.printMinutes ? `${formatNumber(variant.printMinutes)} دقیقه` : "—"],
                ["ابعاد بسته", packageText],
            ];
            summary.innerHTML = `
                <div class="store-profile-summary__price"><span>قیمت پروفایل انتخابی</span><strong>${formatToman(variant.price)}</strong></div>
                ${variant.profileDescription ? `<p class="store-profile-summary__description">${escapeHtml(variant.profileDescription)}</p>` : ""}
                <div class="store-profile-summary__facts">
                    ${facts.map(([key, value]) => `<div class="store-profile-fact"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`).join("")}
                </div>
            `;
        }

        function render() {
            controls.innerHTML = "";
            dimensions.forEach((dim, dimIndex) => {
                const possibleVariants = variantsForDimension(variants, state, dimensions, dimIndex);
                const options = uniqueOptions(possibleVariants.length ? possibleVariants : variants, dim);
                if (!options.length) return;
                const group = document.createElement("div");
                group.className = "store-profile-control";
                group.innerHTML = `<div class="store-profile-control__label">${LABELS[dim] || dim}</div><div class="store-profile-options" role="group" aria-label="${LABELS[dim] || dim}"></div>`;
                const optionHost = group.querySelector(".store-profile-options");
                options.forEach((item) => {
                    const button = document.createElement("button");
                    button.type = "button";
                    button.className = "store-profile-option";
                    const optionVariants = (possibleVariants.length ? possibleVariants : variants)
                        .filter((variant) => valueFor(variant, dim) === item.value);
                    if (dim === "color") {
                        const visual = item.variant || optionVariants[0] || {};
                        if (visual.filamentImage) {
                            const image = document.createElement("img");
                            image.className = "store-profile-color-image";
                            image.src = visual.filamentImage;
                            image.alt = "";
                            button.appendChild(image);
                        } else {
                            const palette = (
                                visual.colorPalette && visual.colorPalette.length
                                    ? visual.colorPalette
                                    : [visual.colorHex, visual.colorSecondaryHex, visual.colorTertiaryHex]
                                        .filter((value) => /^#[0-9a-f]{6}$/i.test(value))
                            );
                            if (palette.length) {
                                const swatch = document.createElement("span");
                                swatch.className = "store-profile-color-swatch";
                                if (palette.length === 1) {
                                    swatch.style.background = palette[0];
                                } else {
                                    const step = 100 / palette.length;
                                    const pieces = palette.map((color, index) => {
                                        const start = Math.round(index * step);
                                        const end = index === palette.length - 1
                                            ? 100
                                            : Math.round((index + 1) * step);
                                        return `${color} ${start}% ${end}%`;
                                    });
                                    swatch.style.background = `linear-gradient(135deg, ${pieces.join(", ")})`;
                                }
                                button.appendChild(swatch);
                            }
                        }
                    }
                    const text = document.createElement("span");
                    text.textContent = item.label;
                    button.appendChild(text);
                    button.disabled = !optionVariants.some((variant) => variant.orderable !== false);
                    if (dim === "weight" || dim === "profile") {
                        const matchingPrices = optionVariants.map((variant) => variant.price).filter((value) => value > 0);
                        if (matchingPrices.length) {
                            const minPrice = Math.min(...matchingPrices);
                            const price = document.createElement("small");
                            price.className = "store-profile-option__price";
                            price.textContent = formatToman(minPrice);
                            button.appendChild(price);
                        }
                    }
                    button.dataset.dimension = dim;
                    button.dataset.value = item.value;
                    button.setAttribute("aria-pressed", state[dim] === item.value ? "true" : "false");
                    button.addEventListener("click", () => {
                        state[dim] = item.value;
                        clearDownstreamState(state, dimensions, dimIndex);
                        autoFillSingletons();
                        const prefix = upstreamState(state, dimensions, dimensions.length);
                        const candidates = matching(variants, prefix)
                            .filter((variant) => variant.orderable !== false);
                        if (selectionComplete()) {
                            const current = variants.find((variant) => variant.id === select.value);
                            const preferred = (
                                current && candidates.includes(current) ? current : null
                            ) || candidates.find((variant) => variant.isDefault) || candidates[0];
                            if (preferred) chooseVariant(preferred);
                            else render();
                        } else {
                            render();
                        }
                    });
                    optionHost.appendChild(button);
                });
                controls.appendChild(group);
            });
            renderSummary(selectedVariant());
        }

        const initial = variants.find((variant) => variant.isDefault && variant.orderable !== false)
            || variants.find((variant) => variant.id === select.value && variant.orderable !== false)
            || variants.find((variant) => variant.orderable !== false)
            || variants[0];
        syncStateToVariant(initial);
        // Preserve profile/size defaults but require explicit downstream choice
        // whenever there is more than one real brand/material/color.
        ["brand", "material", "color"].forEach((dim) => {
            if (dimensions.includes(dim) && uniqueOptions(variants, dim).length > 1) delete state[dim];
        });
        autoFillSingletons();
        if (selectionComplete()) {
            select.value = initial.id;
            select.dispatchEvent(new Event("change", { bubbles: true }));
        }
        render();
        shell.classList.add("is-ready");
        select.dataset.phase50ProfileReady = "1";
    }

    async function boot() {
        const select = document.getElementById("variant-select");
        if (!select) return;
        const ids = Array.from(select.options).filter((option) => option.value).map((option) => option.value);
        if (!ids.length) return;
        try {
            const response = await fetch(`/store/api/variant-commerce-options/?ids=${encodeURIComponent(ids.join(","))}`, {
                credentials: "same-origin",
                headers: { Accept: "application/json" },
            });
            if (!response.ok) return;
            installSelector(select, await response.json());
        } catch (_error) {
            /* Progressive enhancement only: the mature native select remains. */
        }
    }

    document.addEventListener("DOMContentLoaded", boot);
})();
