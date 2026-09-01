(() => {
  "use strict";

  function initProductInfoTabs(root) {
    const tabs = Array.from(root.querySelectorAll("[data-product-info-tab]"));
    const panels = Array.from(root.querySelectorAll("[data-product-info-panel]"));
    if (!tabs.length || tabs.length !== panels.length) return;

    root.classList.add("is-enhanced");

    function activate(index, { focus = false, updateHash = false } = {}) {
      const bounded = Math.max(0, Math.min(index, tabs.length - 1));
      tabs.forEach((tab, tabIndex) => {
        const active = tabIndex === bounded;
        tab.setAttribute("aria-selected", active ? "true" : "false");
        tab.tabIndex = active ? 0 : -1;
      });
      panels.forEach((panel, panelIndex) => {
        const active = panelIndex === bounded;
        panel.hidden = !active;
        panel.setAttribute("aria-hidden", active ? "false" : "true");
      });
      if (focus) tabs[bounded].focus();
      tabs[bounded].scrollIntoView({ inline: "nearest", block: "nearest" });
      if (updateHash) {
        const target = tabs[bounded].dataset.productInfoTab || "";
        if (target) history.replaceState(null, "", `#product-info-${target}`);
      }
    }

    tabs.forEach((tab, index) => {
      tab.addEventListener("click", () => activate(index, { updateHash: true }));
      tab.addEventListener("keydown", (event) => {
        if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
        event.preventDefault();
        if (event.key === "Home") return activate(0, { focus: true, updateHash: true });
        if (event.key === "End") return activate(tabs.length - 1, { focus: true, updateHash: true });
        const rtl = document.documentElement.dir === "rtl";
        const forward = event.key === "ArrowRight" ? !rtl : rtl;
        const next = (index + (forward ? 1 : -1) + tabs.length) % tabs.length;
        activate(next, { focus: true, updateHash: true });
      });
    });

    let initial = 0;
    if (location.hash.startsWith("#product-info-")) {
      const requested = location.hash.replace("#product-info-", "");
      const found = tabs.findIndex((tab) => tab.dataset.productInfoTab === requested);
      if (found >= 0) initial = found;
    }
    activate(initial);
  }

  function boot() {
    document.querySelectorAll("[data-product-info-tabs]").forEach(initProductInfoTabs);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
