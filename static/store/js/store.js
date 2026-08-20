document.addEventListener("DOMContentLoaded", function () {
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
        setText(
            "variant-meta",
            [option.dataset.material + color, option.dataset.quality, weightText, timeText].filter(Boolean).join(" • ")
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

    select.addEventListener("change", updatePrice);
    updatePrice();
});
