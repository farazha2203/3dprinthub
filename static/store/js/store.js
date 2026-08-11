document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("variant-select");
    const breakdown = document.getElementById("price-breakdown");
    const orderButton = document.getElementById("order-variant-button");
    const variantInput = document.getElementById("cart-variant-id");
    if (!select || !breakdown) return;
    const formatToman = (value) => Number(value || 0).toLocaleString("fa-IR") + " تومان";
    function updatePrice() {
        const option = select.options[select.selectedIndex];
        if (!option || !option.value) {
            breakdown.classList.add("hidden");
            if (orderButton) orderButton.disabled = true;
            if (variantInput) variantInput.value = "";
            return;
        }
        const extra = Number(option.dataset.postFee || 0) + Number(option.dataset.fixedFee || 0);
        const setText = (id, value) => { const el = document.getElementById(id); if (el) el.textContent = value; };
        setText("price-material", formatToman(option.dataset.materialCost));
        setText("price-machine", formatToman(option.dataset.machineCost));
        setText("price-labor", formatToman(option.dataset.laborCost));
        setText("price-extra", formatToman(extra));
        setText("price-total", formatToman(option.dataset.total));
        const color = option.dataset.color ? ` • رنگ ${option.dataset.color}` : "";
        setText("variant-meta", `وزن مصرفی ${option.dataset.weight} گرم • زمان چاپ ${option.dataset.printTime} دقیقه • ${option.dataset.material}${color} • ${option.dataset.quality}`);
        breakdown.classList.remove("hidden");
        if (orderButton) orderButton.disabled = false;
        if (variantInput) variantInput.value = option.value;
    }
    select.addEventListener("change", updatePrice);
    updatePrice();
});
