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
        size: "سایز قطعه",
        weight: "وزن",
        build: "مدل ساخت",
        brand: "برند فیلامنت",
        material: "متریال",
        color: "رنگ",
        quality: "کیفیت چاپ",
        variant: "گزینه نهایی",
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
        const finalWeight = Number(meta.final_weight_grams ?? option.dataset.partWeight ?? 0);
        const materialWeight = Number(meta.material_weight_grams ?? option.dataset.chargeableWeight ?? 0);
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
            materialId: clean(meta.material_id || meta.material || option.dataset.material),
            qualityId: clean(meta.quality_id || meta.quality || option.dataset.quality),
            color: clean(meta.color_name ?? option.dataset.color),
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
            stockStatus: clean(meta.stock_status),
            preheatHours: Number(meta.preheat_hours || 0),
            preheatTemperature: Number(meta.preheat_temperature_c || 0),
            quality: clean(meta.quality || option.dataset.quality),
            finalWeight,
            supportWeight: Number(meta.support_weight_grams || option.dataset.supportWeight || 0),
            materialWeight,
            shippingWeight,
            packagingWeight: Number(meta.packaging_weight_grams || 0),
            printMinutes: Number(meta.print_time_minutes ?? option.dataset.printTime ?? 0),
            price: Number(meta.unit_price ?? option.dataset.total ?? 0),
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
        if (dim === "size") return variant.size || "__unspecified__";
        if (dim === "weight") return String(variant.finalWeight || variant.materialWeight || 0);
        if (dim === "build") return variant.build;
        if (dim === "brand") return variant.filamentBrand || "بدون برند";
        if (dim === "material") return variant.materialId || variant.material || "__unspecified__";
        // A visual color can span materials/brands; never use MaterialColorOption.__str__ here.
        if (dim === "color") return JSON.stringify([
            variant.color || "", variant.colorType || "solid", variant.colorFinish || "matte",
            (variant.colorPalette?.length ? variant.colorPalette : [variant.colorHex || ""]).map((hex) => hex.toLowerCase()),
        ]);
        if (dim === "quality") return variant.qualityId || variant.quality || "__unspecified__";
        if (dim === "variant") return variant.id;
        return "";
    }

    function labelFor(variant, dim) {
        if (dim === "variant") return [variant.profileLabel, variant.filamentBrand,
            variant.buildLabel, variant.finalWeight ? `${formatNumber(variant.finalWeight)} گرم` : "",
            variant.printMinutes ? `${formatNumber(variant.printMinutes)} دقیقه` : ""].filter(Boolean).join(" — ");
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

    const GUIDED_DIMENSIONS = ["size", "color", "material", "quality"];

    function guidedCandidates(variants, state) {
        if (!GUIDED_DIMENSIONS.every((dim) => state[dim])) return [];
        return matching(variants, upstreamState(state, GUIDED_DIMENSIONS, 4));
    }

    function resolveGuidedVariant(variants, state) {
        const candidates = guidedCandidates(variants, state).filter((variant) => variant.orderable);
        if (candidates.length === 1) return candidates[0];
        return candidates.find((variant) => variant.id === state.variant) || null;
    }

    function fillGuidedSingletons(variants, state) {
        for (let index = 0; index < GUIDED_DIMENSIONS.length; index += 1) {
            const dim = GUIDED_DIMENSIONS[index];
            const pool = variantsForDimension(variants, state, GUIDED_DIMENSIONS, index);
            const options = uniqueOptions(pool.filter((variant) => variant.orderable), dim);
            if (!options.some((item) => item.value === state[dim])) delete state[dim];
            if (!state[dim] && options.length === 1) state[dim] = options[0].value;
            if (!state[dim]) break;
        }
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
        GUIDED_DIMENSIONS,
        guidedCandidates,
        resolveGuidedVariant,
        fillGuidedSingletons,
        readNativeOption,
    };

    if (typeof module !== "undefined" && module.exports) {
        module.exports = TEST_API;
    }
    if (typeof document === "undefined") return;

    function installSelector(select, payload) {
        if (!select || select.dataset.phase50ProfileReady === "1") return;
        const optionNodes = Array.from(select.options).filter((option) => option.value);
        if (!optionNodes.length) return;

        const variantsMap = payload && payload.variants ? payload.variants : {};
        // Incomplete API metadata must leave the native fallback intact.
        if (optionNodes.some((option) => !variantsMap[String(option.value)])) return;
        const variants = optionNodes.map((option) => readNativeOption(option, variantsMap[String(option.value)]));
        if (!variants.length) return;

        const selectorLabel = "انتخاب مشخصات سفارش";
        const dimensions = [...GUIDED_DIMENSIONS];
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
                    <p>فقط چهار انتخاب ساده: سایز، رنگ، متریال و کیفیت. وزن، زمان چاپ و قیمت نهایی را سیستم محاسبه می‌کند.</p>
                </div>
                <span class="store-profile-selector__badge">۴ مرحله ساده</span>
            </div>
            <div class="store-profile-controls" data-profile-controls></div>
            <div class="store-profile-summary" data-profile-summary role="status" aria-live="polite" aria-atomic="true"></div>
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

        let syncing = false;
        function syncStateToVariant(variant) {
            dimensions.forEach((dim) => { state[dim] = valueFor(variant, dim); });
            state.variant = variant.id;
        }

        function selectedVariant() {
            return resolveGuidedVariant(variants, state);
        }

        function syncCart() {
            const variant = selectedVariant();
            syncing = true;
            select.value = variant ? variant.id : "";
            // The mature price/cart listener remains the only cart handoff.
            select.dispatchEvent(new Event("change", { bubbles: true }));
            syncing = false;
        }

        function renderSummary(variant) {
            if (!variant) {
                summary.textContent = variants.some((item) => item.orderable)
                    ? "برای مشاهده خلاصه و فعال‌شدن افزودن به سبد، انتخاب‌های مشخص‌شده را کامل کنید."
                    : "در حال حاضر هیچ گزینه قابل سفارشی برای این محصول موجود نیست.";
                return;
            }
            const facts = [
                ["سایز", variant.size || "سایز استاندارد"],
                ["رنگ", labelFor(variant, "color")],
                ["متریال", variant.material || "استاندارد"],
                ["کیفیت چاپ", variant.quality || "استاندارد"],
                ["وزن قطعه", variant.finalWeight ? `${formatNumber(variant.finalWeight)} گرم` : "ثبت نشده"],
                ["زمان چاپ", variant.printMinutes ? `${formatNumber(variant.printMinutes)} دقیقه` : "ثبت نشده"],
                ["وضعیت سفارش", variant.stockStatus === "preorder" ? "پیش‌سفارش" : "قابل سفارش"],
                ...(variant.filamentBrand ? [["برند فیلامنت", variant.filamentBrand]] : []),
                ...(variant.partDimensionsLabel ? [["ابعاد قطعه", variant.partDimensionsLabel]] : []),
            ];
            summary.innerHTML = `
                <div class="store-profile-summary__price"><span>قیمت نهایی هر عدد</span><strong>${formatToman(variant.price)}</strong></div>
                <p class="store-profile-summary__note">مالیات و هزینه ارسال در تسویه‌حساب محاسبه می‌شوند.</p>
                ${variant.profileDescription ? `<p class="store-profile-summary__description">${escapeHtml(variant.profileDescription)}</p>` : ""}
                <div class="store-profile-summary__facts">
                    ${facts.map(([key, value]) => `<div class="store-profile-fact"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`).join("")}
                </div>
            `;
        }

        function render() {
            controls.innerHTML = "";
            const candidates = guidedCandidates(variants, state);
            const visibleDimensions = candidates.filter((variant) => variant.orderable).length > 1
                ? [...dimensions, "variant"] : dimensions;
            const activeIndex = visibleDimensions.findIndex((dim) => !state[dim]);
            visibleDimensions.forEach((dim, dimIndex) => {
                const unlocked = dimensions.slice(0, dimIndex).every((key) => state[key]);
                const possibleVariants = variantsForDimension(variants, state, dimensions, dimIndex);
                const options = unlocked ? uniqueOptions(possibleVariants, dim) : [];
                const group = document.createElement("div");
                group.className = "store-profile-control";
                group.dataset.step = dim;
                group.classList.toggle("is-pending", !unlocked);
                group.classList.toggle("is-active", unlocked && dimIndex === activeIndex);
                group.classList.toggle("is-complete", Boolean(state[dim]));
                const title = LABELS[dim] || "گزینه نهایی";
                group.innerHTML = `<div class="store-profile-control__label"><span class="store-profile-step-number">${formatNumber(dimIndex + 1)}</span>${title}${state[dim] ? '<span class="store-profile-step-done">انتخاب شد</span>' : ''}</div><div class="store-profile-options" role="group" aria-label="${title}"></div>`;
                if (!unlocked) {
                    const hint = document.createElement("p");
                    hint.className = "store-profile-hint";
                    hint.textContent = "ابتدا مرحله قبل را انتخاب کنید.";
                    group.appendChild(hint);
                }
                const optionHost = group.querySelector(".store-profile-options");
                options.forEach((item) => {
                    const button = document.createElement("button");
                    button.type = "button";
                    button.className = "store-profile-option";
                    const optionVariants = possibleVariants
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
                    if (button.disabled) {
                        const unavailable = document.createElement("small");
                        unavailable.textContent = "ناموجود";
                        button.appendChild(unavailable);
                    }
                    button.dataset.dimension = dim;
                    button.dataset.value = item.value;
                    button.setAttribute("aria-pressed", state[dim] === item.value ? "true" : "false");
                    button.addEventListener("click", () => {
                        state[dim] = item.value;
                        clearDownstreamState(state, visibleDimensions, dimIndex);
                        if (dim !== "variant") delete state.variant;
                        fillGuidedSingletons(variants, state);
                        syncCart();
                        render();
                        const replacement = Array.from(controls.querySelectorAll("button")).find(
                            (node) => node.dataset.dimension === dim && node.dataset.value === item.value);
                        replacement?.focus({ preventScroll: true });
                    });
                    optionHost.appendChild(button);
                });
                controls.appendChild(group);
            });
            renderSummary(selectedVariant());
        }

        // Native fallback changes and browser restoration must update the guided state too.
        select.addEventListener("change", () => {
            if (syncing) return;
            Object.keys(state).forEach((key) => delete state[key]);
            const variant = variants.find((item) => item.id === select.value && item.orderable);
            if (variant) syncStateToVariant(variant);
            syncCart();
            render();
        });
        variants.forEach((variant) => {
            variant.option.disabled = !variant.orderable;
            variant.option.dataset.unavailable = variant.orderable ? "0" : "1";
            variant.option.dataset.total = String(variant.price);
        });
        const initial = variants.find((variant) => variant.id === select.value && variant.orderable);
        if (initial) syncStateToVariant(initial);
        else fillGuidedSingletons(variants, state);
        syncCart();
        render();
        const breakdown = document.getElementById("price-breakdown");
        if (breakdown) breakdown.hidden = true;
        shell.classList.add("is-ready");
        select.dataset.phase50ProfileReady = "1";
    }

    async function boot() {
        const select = document.getElementById("variant-select");
        if (!select) return;
        const ids = Array.from(select.options).filter((option) => option.value).map((option) => option.value);
        if (!ids.length) return;
        try {
            const payload = { products: {}, variants: {} };
            // The existing endpoint bounds each request to 100 IDs.
            for (let offset = 0; offset < ids.length; offset += 100) {
                const response = await fetch(`/store/api/variant-commerce-options/?ids=${encodeURIComponent(ids.slice(offset, offset + 100).join(","))}`, {
                    credentials: "same-origin",
                    headers: { Accept: "application/json" },
                });
                if (!response.ok) return;
                const batch = await response.json();
                Object.assign(payload.products, batch.products);
                Object.assign(payload.variants, batch.variants);
            }
            installSelector(select, payload);
        } catch (_error) {
            /* Progressive enhancement only: the mature native select remains. */
        }
    }

    document.addEventListener("DOMContentLoaded", boot);
})();
