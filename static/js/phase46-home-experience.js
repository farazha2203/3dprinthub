(function () {
  "use strict";
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduced) document.documentElement.classList.add("p46-motion-enabled");

  function qs(selector, root) { return (root || document).querySelector(selector); }
  function qsa(selector, root) { return Array.prototype.slice.call((root || document).querySelectorAll(selector)); }
  function norm(value) { return String(value || "").trim().toUpperCase(); }

  function splitMaterials() {
    qsa("[data-p46-materials]").forEach(function (root) {
      if (root.getAttribute("data-p46-ready") === "1") return;
      var raw = root.textContent || "";
      var parts = raw.split(/(?:،|,|\/|\||;|\n)+/).map(function (item) {
        return item.replace(/\s+/g, " ").trim();
      }).filter(Boolean);
      if (!parts.length) return;
      root.textContent = "";
      parts.forEach(function (part) {
        var pill = document.createElement("span");
        pill.textContent = part;
        root.appendChild(pill);
      });
      root.setAttribute("data-p46-ready", "1");
    });
  }

  function initGuide() {
    var root = qs("[data-p46-guide]");
    if (!root) return;
    var tabs = qsa("[data-p46-tab]", root);
    var panels = qsa("[data-p46-panel]", root);
    function activate(name) {
      tabs.forEach(function (tab) {
        var active = tab.getAttribute("data-p46-tab") === name;
        tab.classList.toggle("is-active", active);
        tab.setAttribute("aria-selected", active ? "true" : "false");
        tab.tabIndex = active ? 0 : -1;
      });
      panels.forEach(function (panel) {
        var active = panel.getAttribute("data-p46-panel") === name;
        panel.hidden = !active;
      });
    }
    tabs.forEach(function (tab, index) {
      tab.addEventListener("click", function () { activate(tab.getAttribute("data-p46-tab")); });
      tab.addEventListener("keydown", function (event) {
        if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
        event.preventDefault();
        var delta = event.key === "ArrowLeft" ? 1 : -1;
        var next = (index + delta + tabs.length) % tabs.length;
        tabs[next].focus();
        activate(tabs[next].getAttribute("data-p46-tab"));
      });
    });
  }

  function initReadyPicker() {
    var root = qs("[data-p46-ready-picker]");
    var form = qs("[data-p13-order-form]");
    if (!root || !form) return;
    var hidden = qs('input[name="ready_catalog_asset_id"]', form);
    var code = qs("[data-p46-ready-code]", root);
    var filter = qs("[data-p46-ready-filter]", root);
    var items = qsa("[data-p46-ready-item]", root);
    var selected = qs("[data-p46-ready-selected]", root);
    var media = qs("[data-p46-selected-media]", root);
    var selectedCode = qs("[data-p46-selected-code]", root);
    var selectedTitle = qs("[data-p46-selected-title]", root);
    var selectedSource = qs("[data-p46-selected-source]", root);
    var clear = qs("[data-p46-clear-ready]", root);

    function sameCode(item, value) {
      var wanted = norm(value).replace(/\s+/g, "");
      var itemCode = norm(item.getAttribute("data-code")).replace(/\s+/g, "");
      var sku = norm(item.getAttribute("data-sku")).replace(/\s+/g, "");
      return wanted && (wanted === itemCode || (sku && wanted === sku));
    }

    function choose(item) {
      items.forEach(function (candidate) { candidate.classList.toggle("is-selected", candidate === item); });
      if (!item) {
        if (hidden) hidden.value = "";
        if (selected) selected.hidden = true;
        if (media) media.textContent = "";
        return;
      }
      var id = item.getAttribute("data-id") || "";
      var publicCode = item.getAttribute("data-code") || "";
      var title = item.getAttribute("data-title") || "";
      var source = item.getAttribute("data-source") || "";
      var image = item.getAttribute("data-image") || "";
      if (hidden) hidden.value = id;
      if (code) code.value = publicCode;
      if (selectedCode) selectedCode.textContent = publicCode;
      if (selectedTitle) selectedTitle.textContent = title;
      if (selectedSource) selectedSource.textContent = source;
      if (media) {
        media.textContent = "";
        if (image) {
          var img = document.createElement("img");
          img.src = image; img.alt = title; img.loading = "lazy";
          media.appendChild(img);
        }
      }
      if (selected) selected.hidden = false;
    }

    items.forEach(function (item) { item.addEventListener("click", function () { choose(item); }); });
    if (filter) filter.addEventListener("input", function () {
      var value = norm(filter.value);
      items.forEach(function (item) {
        var hay = [item.getAttribute("data-code"), item.getAttribute("data-sku"),
          item.getAttribute("data-title"), item.getAttribute("data-source")].join(" ").toUpperCase();
        item.hidden = Boolean(value) && hay.indexOf(value) === -1;
      });
    });
    if (code) {
      code.addEventListener("input", function () {
        var match = items.find(function (item) { return sameCode(item, code.value); });
        if (match) choose(match);
        else {
          items.forEach(function (item) { item.classList.remove("is-selected"); });
          if (hidden) hidden.value = "";
          if (selected) selected.hidden = true;
        }
      });
      code.addEventListener("blur", function () { code.value = norm(code.value); });
    }
    if (clear) clear.addEventListener("click", function () {
      choose(null);
      if (code) { code.value = ""; code.focus(); }
    });
    if (hidden && hidden.value) {
      var initial = items.find(function (item) { return item.getAttribute("data-id") === String(hidden.value); });
      if (initial) choose(initial);
    }
  }

  function initMotion() {
    if (reduced || !("IntersectionObserver" in window)) return;
    var sections = qsa(".p45-home > section");
    sections.forEach(function (section, index) {
      if (index === 0) return;
      section.classList.add("p46-reveal");
      if (index % 2 === 0) section.classList.add("p46-reveal--alt");
      section.style.setProperty("--p46-delay", String(Math.min((index % 4) * 45, 135)) + "ms");
    });
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -9% 0px", threshold: 0.08 });
    qsa(".p46-reveal").forEach(function (section) { observer.observe(section); });
  }

  document.addEventListener("DOMContentLoaded", function () {
    splitMaterials();
    initGuide();
    initReadyPicker();
    initMotion();
  });
})();