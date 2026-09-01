(() => {
  "use strict";

  function topLevelPanels(form) {
    const fieldsets = Array.from(form.querySelectorAll("fieldset.module"))
      .filter((item) => !item.closest(".inline-group"));
    const inlines = Array.from(form.querySelectorAll(".inline-group"))
      .filter((item) => !item.parentElement?.closest(".inline-group"));
    return [...fieldsets, ...inlines].filter((item) => {
      return !item.classList.contains("collapse") || item.querySelector("h2, h3");
    });
  }

  function panelTitle(panel, index) {
    const heading = panel.querySelector(":scope > h2, :scope > h3");
    const text = (heading?.textContent || "").replace(/\s+/g, " ").trim();
    return text || `بخش ${index + 1}`;
  }

  function initTabbedAdmin() {
    const form = document.querySelector("#content-main form");
    if (!form || form.dataset.phase49TabsInitialized === "1") return;

    const panels = topLevelPanels(form);
    if (panels.length < 2) return;

    form.dataset.phase49TabsInitialized = "1";
    form.classList.add("phase49-admin-tabs-ready");

    const nav = document.createElement("div");
    nav.className = "phase49-admin-tabs";
    nav.setAttribute("role", "tablist");
    nav.setAttribute("aria-label", "بخش‌های فرم مدیریت");

    const storageKey = `phase49-admin-tab:${location.pathname}`;
    const saved = Number.parseInt(sessionStorage.getItem(storageKey) || "0", 10);
    let current = Number.isFinite(saved) && saved >= 0 && saved < panels.length ? saved : 0;
    const tabs = [];

    function activate(index, { focus = false } = {}) {
      current = Math.max(0, Math.min(index, panels.length - 1));
      panels.forEach((panel, panelIndex) => {
        const active = panelIndex === current;
        panel.hidden = !active;
        panel.setAttribute("aria-hidden", active ? "false" : "true");
      });
      tabs.forEach((tab, tabIndex) => {
        const active = tabIndex === current;
        tab.setAttribute("aria-selected", active ? "true" : "false");
        tab.tabIndex = active ? 0 : -1;
      });
      sessionStorage.setItem(storageKey, String(current));
      const tab = tabs[current];
      tab?.scrollIntoView({ inline: "nearest", block: "nearest" });
      if (focus) tab?.focus();
    }

    panels.forEach((panel, index) => {
      const panelId = panel.id || `phase49-admin-panel-${index + 1}`;
      const tabId = `phase49-admin-tab-${index + 1}`;
      panel.id = panelId;
      panel.classList.add("phase49-admin-tab-panel");
      panel.setAttribute("role", "tabpanel");
      panel.setAttribute("aria-labelledby", tabId);

      const tab = document.createElement("button");
      tab.type = "button";
      tab.id = tabId;
      tab.className = "phase49-admin-tabs__tab";
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-controls", panelId);
      tab.textContent = panelTitle(panel, index);
      tab.addEventListener("click", () => activate(index));
      tab.addEventListener("keydown", (event) => {
        if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
        event.preventDefault();
        if (event.key === "Home") return activate(0, { focus: true });
        if (event.key === "End") return activate(tabs.length - 1, { focus: true });
        const rtl = document.documentElement.dir === "rtl" || document.body.dir === "rtl";
        const forward = event.key === "ArrowRight" ? !rtl : rtl;
        const next = (current + (forward ? 1 : -1) + tabs.length) % tabs.length;
        activate(next, { focus: true });
      });
      tabs.push(tab);
      nav.appendChild(tab);
    });

    const anchor = panels[0];
    anchor.parentNode?.insertBefore(nav, anchor);
    activate(current);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTabbedAdmin, { once: true });
  } else {
    initTabbedAdmin();
  }
})();
