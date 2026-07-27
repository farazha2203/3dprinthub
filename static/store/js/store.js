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
        document.getElementById("price-material").textContent = formatToman(option.dataset.materialCost);
        document.getElementById("price-machine").textContent = formatToman(option.dataset.machineCost);
        document.getElementById("price-labor").textContent = formatToman(option.dataset.laborCost);
        document.getElementById("price-extra").textContent = formatToman(extra);
        document.getElementById("price-total").textContent = formatToman(option.dataset.total);
        document.getElementById("variant-meta").textContent = `وزن مصرفی ${option.dataset.weight} گرم • زمان چاپ ${option.dataset.printTime} دقیقه • ${option.dataset.material} • ${option.dataset.quality}`;
        breakdown.classList.remove("hidden");
        if (orderButton) orderButton.disabled = false;
        if (variantInput) variantInput.value = option.value;
    }
    select.addEventListener("change", updatePrice);
    updatePrice();
});
