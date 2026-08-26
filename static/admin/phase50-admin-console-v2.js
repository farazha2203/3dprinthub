(function () {
  "use strict";

  const doc = document;
  const root = doc.documentElement;
  const FILTER_IGNORE = new Set(["q", "o", "p", "ot", "is_popup", "_popup", "_to_field", "all"]);

  function text(el) {
    return (el && el.textContent ? el.textContent : "").replace(/\s+/g, " ").trim();
  }

  function icon(name) {
    const i = doc.createElement("i");
    i.className = name;
    i.setAttribute("aria-hidden", "true");
    return i;
  }

  function activeFilterCount() {
    const params = new URLSearchParams(window.location.search);
    let count = 0;
    for (const [key, value] of params.entries()) {
      if (!value || FILTER_IGNORE.has(key)) continue;
      if (key === "q") continue;
      count += 1;
    }
    return count;
  }

  function filterResetUrl() {
    const current = new URL(window.location.href);
    const keep = new URLSearchParams();
    for (const key of ["q", "o"]) {
      const value = current.searchParams.get(key);
      if (value) keep.set(key, value);
    }
    const qs = keep.toString();
    return current.pathname + (qs ? "?" + qs : "");
  }

  function localizeLegacyLabels(scope) {
    const mapping = new Map([
      ["Filter", "فیلترها"],
      ["FILTER", "فیلترها"],
      ["Show counts", "نمایش تعداد"],
      ["Hide counts", "پنهان‌کردن تعداد"],
      ["All", "همه"],
      ["Yes", "بله"],
      ["No", "خیر"],
      ["Action:", "عملیات گروهی:"],
      ["Action", "عملیات گروهی"],
      ["Run", "اجرا"],
      ["Go", "اجرا"],
      ["Search", "جستجو"],
    ]);

    scope.querySelectorAll("a, button, label, h2, h3, option").forEach((el) => {
      const current = text(el);
      if (!mapping.has(current)) return;
      if (el.tagName === "OPTION") {
        el.textContent = mapping.get(current);
      } else if (el.children.length === 0) {
        el.textContent = mapping.get(current);
      }
    });

    scope.querySelectorAll('input[type="submit"]').forEach((el) => {
      const value = (el.value || "").trim();
      if (mapping.has(value)) el.value = mapping.get(value);
    });
  }

  function decorateSearchToolbar() {
    const toolbar = doc.getElementById("toolbar");
    const searchForm = doc.getElementById("changelist-search");
    if (!toolbar || !searchForm) return;

    toolbar.classList.add("admin-list-toolbar", "card");
    searchForm.classList.add("admin-list-search");

    const searchbar = searchForm.querySelector("#searchbar");
    if (searchbar) {
      searchbar.classList.add("form-control", "admin-search-input");
      searchbar.placeholder = "جستجو در این بخش...";
      searchbar.setAttribute("aria-label", "جستجو در این بخش");
    }

    const submit = searchForm.querySelector('input[type="submit"], button[type="submit"]');
    if (submit) {
      submit.classList.add("btn", "btn-primary", "admin-search-submit");
      if (submit.tagName === "INPUT") submit.value = "جستجو";
      else submit.textContent = "جستجو";
    }

    const img = searchForm.querySelector("label img");
    if (img) img.hidden = true;
  }

  function buildFilterDrawer() {
    const changelist = doc.getElementById("changelist");
    const filter = doc.getElementById("changelist-filter");
    if (!changelist || !filter || doc.getElementById("admin-filter-drawer")) return;

    const count = activeFilterCount();
    const drawer = doc.createElement("aside");
    drawer.id = "admin-filter-drawer";
    drawer.className = "admin-filter-drawer";
    drawer.setAttribute("aria-hidden", "true");
    drawer.setAttribute("aria-label", "فیلترهای فهرست");

    const header = doc.createElement("div");
    header.className = "admin-filter-drawer__header";

    const headingWrap = doc.createElement("div");
    headingWrap.className = "admin-filter-drawer__heading";
    const heading = doc.createElement("h5");
    heading.className = "mb-0";
    heading.textContent = "فیلترها";
    headingWrap.appendChild(heading);

    const subtitle = doc.createElement("span");
    subtitle.className = "admin-filter-active-summary";
    subtitle.textContent = count ? count.toLocaleString("fa-IR") + " فیلتر فعال" : "نمایش فقط در صورت نیاز";
    headingWrap.appendChild(subtitle);

    const close = doc.createElement("button");
    close.type = "button";
    close.className = "btn btn-icon btn-ghost-secondary rounded-circle admin-filter-close";
    close.setAttribute("aria-label", "بستن فیلترها");
    close.appendChild(icon("ri-close-line fs-20"));

    header.appendChild(headingWrap);
    header.appendChild(close);

    const body = doc.createElement("div");
    body.className = "admin-filter-drawer__body";

    const footer = doc.createElement("div");
    footer.className = "admin-filter-drawer__footer";
    const reset = doc.createElement("a");
    reset.className = "btn btn-light flex-grow-1";
    reset.href = filterResetUrl();
    reset.appendChild(icon("ri-refresh-line me-1"));
    reset.appendChild(doc.createTextNode("پاک‌کردن فیلترها"));
    footer.appendChild(reset);

    const backdrop = doc.createElement("button");
    backdrop.type = "button";
    backdrop.id = "admin-filter-backdrop";
    backdrop.className = "admin-filter-backdrop";
    backdrop.setAttribute("aria-label", "بستن فیلترها");

    const nativeTitle = filter.querySelector("h2");
    if (nativeTitle) nativeTitle.hidden = true;
    localizeLegacyLabels(filter);
    filter.classList.add("admin-filter-native");
    body.appendChild(filter);

    drawer.appendChild(header);
    drawer.appendChild(body);
    drawer.appendChild(footer);
    doc.body.appendChild(backdrop);
    doc.body.appendChild(drawer);

    const toolbarForm = doc.querySelector("#toolbar form") || doc.querySelector("#changelist-search");
    const button = doc.createElement("button");
    button.type = "button";
    button.id = "admin-filter-toggle";
    button.className = "btn btn-soft-primary admin-filter-toggle";
    button.appendChild(icon("ri-filter-3-line me-1"));
    const label = doc.createElement("span");
    label.textContent = "فیلترها";
    button.appendChild(label);
    if (count) {
      const badge = doc.createElement("span");
      badge.className = "badge rounded-pill bg-primary ms-2";
      badge.textContent = count.toLocaleString("fa-IR");
      button.appendChild(badge);
    }

    if (toolbarForm) {
      const submit = toolbarForm.querySelector('input[type="submit"], button[type="submit"]');
      if (submit && submit.parentNode === toolbarForm) toolbarForm.insertBefore(button, submit);
      else toolbarForm.appendChild(button);
    } else {
      changelist.insertAdjacentElement("beforebegin", button);
    }

    function setOpen(open) {
      drawer.classList.toggle("is-open", open);
      backdrop.classList.toggle("is-open", open);
      doc.body.classList.toggle("admin-filter-open", open);
      drawer.setAttribute("aria-hidden", open ? "false" : "true");
      button.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) {
        window.setTimeout(() => {
          const focusable = drawer.querySelector("a,button,input,select");
          if (focusable) focusable.focus({ preventScroll: true });
        }, 80);
      }
    }

    button.setAttribute("aria-controls", drawer.id);
    button.setAttribute("aria-expanded", "false");
    button.addEventListener("click", () => setOpen(true));
    close.addEventListener("click", () => setOpen(false));
    backdrop.addEventListener("click", () => setOpen(false));
    doc.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && drawer.classList.contains("is-open")) setOpen(false);
    });

    doc.body.classList.add("admin-filter-drawer-ready");
  }

  function decorateActions() {
    doc.querySelectorAll("#changelist-form .actions").forEach((actions) => {
      actions.classList.add("admin-bulk-actions", "card");
      const select = actions.querySelector("select");
      if (select) select.classList.add("form-select", "form-select-sm");
      const button = actions.querySelector('button[type="submit"], input[type="submit"]');
      if (button) {
        button.classList.add("btn", "btn-soft-primary", "btn-sm");
        if (button.tagName === "INPUT") button.value = "اجرا";
        else button.textContent = "اجرا";
      }
      localizeLegacyLabels(actions);
    });
  }

  function decorateResults() {
    const results = doc.querySelector("#changelist .results");
    const table = doc.getElementById("result_list");
    if (!results || !table) return;

    results.classList.add("admin-results-card", "table-responsive");
    table.classList.add("table", "table-hover", "align-middle", "mb-0", "admin-result-table");

    table.querySelectorAll("tbody tr").forEach((row) => {
      const checkbox = row.querySelector('input[type="checkbox"]');
      if (checkbox) checkbox.classList.add("form-check-input");
    });
    table.querySelectorAll("thead input[type=checkbox]").forEach((checkbox) => checkbox.classList.add("form-check-input"));

    const meta = doc.createElement("div");
    meta.className = "admin-results-meta";
    const rowCount = table.querySelectorAll("tbody tr").length;
    meta.innerHTML = '<span class="admin-results-meta__dot"></span><span>' + rowCount.toLocaleString("fa-IR") + " ردیف در این صفحه</span>";
    results.insertAdjacentElement("beforebegin", meta);
  }

  function decoratePagination() {
    doc.querySelectorAll("#changelist .paginator").forEach((paginator) => {
      paginator.classList.add("admin-pagination", "card");
      paginator.querySelectorAll("a").forEach((link) => link.classList.add("admin-page-link"));
    });
  }

  function decorateObjectTools() {
    doc.querySelectorAll(".object-tools").forEach((tools) => {
      tools.classList.add("admin-object-tools");
      tools.querySelectorAll("a").forEach((link, index) => {
        link.classList.add("btn", index === 0 ? "btn-primary" : "btn-soft-primary");
        if (!link.querySelector("i")) link.prepend(icon(index === 0 ? "ri-add-line me-1" : "ri-external-link-line me-1"));
      });
    });
  }

  function buildFormSectionNav() {
    if (doc.body.classList.contains("change-list")) return;
    const form = doc.querySelector("#content-main form");
    if (!form || form.dataset.adminSectionNavReady === "1") return;

    const fieldsets = Array.from(form.querySelectorAll(":scope > fieldset.module, :scope > div > fieldset.module"))
      .filter((fieldset) => fieldset.querySelector("h2"));
    if (fieldsets.length < 2) return;

    const nav = doc.createElement("nav");
    nav.className = "admin-section-nav card";
    nav.setAttribute("aria-label", "بخش‌های فرم");

    const scroll = doc.createElement("div");
    scroll.className = "admin-section-nav__scroll";
    nav.appendChild(scroll);

    fieldsets.forEach((fieldset, index) => {
      const title = text(fieldset.querySelector("h2")) || "بخش " + (index + 1).toLocaleString("fa-IR");
      const id = "admin-form-section-" + (index + 1);
      fieldset.id = fieldset.id || id;
      fieldset.classList.add("admin-form-section-card");

      const link = doc.createElement("a");
      link.className = "admin-section-nav__link";
      link.href = "#" + fieldset.id;
      link.textContent = title;
      link.addEventListener("click", (event) => {
        event.preventDefault();
        fieldset.scrollIntoView({ behavior: "smooth", block: "start" });
        history.replaceState(null, "", "#" + fieldset.id);
      });
      scroll.appendChild(link);
    });

    form.insertAdjacentElement("afterbegin", nav);
    form.dataset.adminSectionNavReady = "1";
  }

  function decorateForms() {
    doc.querySelectorAll("fieldset.module, .inline-group").forEach((section) => section.classList.add("admin-form-card"));
    doc.querySelectorAll(".submit-row").forEach((row) => row.classList.add("admin-submit-bar"));
    buildFormSectionNav();
  }

  function decoratePageTitle() {
    const box = doc.querySelector(".page-title-box");
    if (!box) return;
    box.classList.add("admin-page-heading");
    const h = box.querySelector("h1,h2,h3,h4");
    if (h) h.classList.add("admin-page-heading__title");
  }

  function init() {
    root.classList.add("admin-console-v2");
    localizeLegacyLabels(doc);
    decoratePageTitle();
    decorateObjectTools();
    decorateSearchToolbar();
    buildFilterDrawer();
    decorateActions();
    decorateResults();
    decoratePagination();
    decorateForms();
  }

  if (doc.readyState === "loading") doc.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
