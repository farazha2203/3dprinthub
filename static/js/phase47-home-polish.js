(function () {
  "use strict";

  function qs(selector, root) {
    return (root || document).querySelector(selector);
  }

  function qsa(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  var reduceMotion = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var faDigits = ["۰","۱","۲","۳","۴","۵","۶","۷","۸","۹"];
  function faNumber(value) {
    return String(value).replace(/\d/g, function (digit) {
      return faDigits[Number(digit)] || digit;
    });
  }

  function initPageProgress() {
    var host = document.createElement("div");
    host.className = "p47-page-progress";
    host.setAttribute("aria-hidden", "true");
    var fill = document.createElement("span");
    host.appendChild(fill);
    document.body.appendChild(host);

    var ticking = false;
    function update() {
      ticking = false;
      var doc = document.documentElement;
      var total = Math.max(1, doc.scrollHeight - window.innerHeight);
      var ratio = Math.max(0, Math.min(1, window.scrollY / total));
      fill.style.width = (ratio * 100).toFixed(2) + "%";
    }
    function requestUpdate() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }
    update();
    window.addEventListener("scroll", requestUpdate, { passive: true });
    window.addEventListener("resize", requestUpdate, { passive: true });
  }

  function initVariedSectionMotion() {
    var sections = qsa(".p45-home > section");
    var modes = ["rise", "side", "scale", "soft"];

    sections.forEach(function (section, index) {
      section.classList.add("p47-section-polish");
      if (index === 0) return;
      section.classList.add("p47-motion-" + modes[(index - 1) % modes.length]);
    });

    if (reduceMotion || !("IntersectionObserver" in window)) return;

    document.documentElement.classList.add("p47-inner-motion");
    var roots = qsa("[data-p46-guide], .p13-order-benefits, [data-p46-ready-list], [data-p14-home-model-grid]");
    roots.forEach(function (root) {
      root.setAttribute("data-p47-stagger-root", "");
      var items = qsa(".p46-guide-card, .p13-order-benefit, .p46-ready-item, .p14-model-card", root);
      items.forEach(function (item, index) {
        item.setAttribute("data-p47-stagger-item", "");
        item.style.setProperty("--p47-item-delay", String(Math.min(index, 8) * 45) + "ms");
      });
    });

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -7% 0px" });

    roots.forEach(function (root) { observer.observe(root); });
  }

  function initWizardProgress() {
    var form = qs("[data-p13-order-form]");
    var status = qs("[data-p47-wizard-status]");
    if (!form || !status) return;

    var labels = {
      1: "نوع سفارش",
      2: "مشخصات چاپ",
      3: "شرایط کاری",
      4: "تصاویر و ثبت"
    };
    var label = qs("[data-p47-step-label]", status);
    var fill = qs("[data-p47-progress-fill]", status);
    var text = qs("[data-p47-progress-text]", status);

    function refresh() {
      var step = Number(form.getAttribute("data-current-step") || "1");
      step = Math.max(1, Math.min(4, step));
      if (label) label.textContent = labels[step];
      if (fill) fill.style.width = String(step * 25) + "%";
      if (text) text.textContent = faNumber(step) + " از ۴";
    }

    refresh();

    var observer = new MutationObserver(function (records) {
      records.forEach(function (record) {
        if (record.attributeName === "data-current-step") refresh();
      });
    });
    observer.observe(form, { attributes: true });
  }

  function showToast(message) {
    var toast = qs(".p47-copy-toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.className = "p47-copy-toast";
      toast.setAttribute("role", "status");
      toast.setAttribute("aria-live", "polite");
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add("is-visible");
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(function () {
      toast.classList.remove("is-visible");
    }, 1800);
  }

  function copyText(value) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(value);
    }
    return new Promise(function (resolve, reject) {
      var area = document.createElement("textarea");
      area.value = value;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      try {
        document.execCommand("copy");
        resolve();
      } catch (error) {
        reject(error);
      } finally {
        area.remove();
      }
    });
  }

  function initProductCodeCopy() {
    qsa("[data-p47-copy-code]").forEach(function (button) {
      button.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();
        var code = button.getAttribute("data-p47-copy-code") || "";
        if (!code) return;
        copyText(code).then(function () {
          showToast("کد " + code + " کپی شد");
        }).catch(function () {
          showToast("کد محصول: " + code);
        });
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initPageProgress();
    initVariedSectionMotion();
    initWizardProgress();
    initProductCodeCopy();
  });
})();
