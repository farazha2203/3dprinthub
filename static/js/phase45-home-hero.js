(function () {
  "use strict";

  function boot() {
    var root = document.querySelector("[data-p45-hero]");
    if (!root) return;

    var header = document.querySelector("header");
    function syncHeaderHeight() {
      if (!header) return;
      var height = Math.max(0, Math.round(header.getBoundingClientRect().height));
      if (height) document.documentElement.style.setProperty("--p45-header-height", height + "px");
    }
    syncHeaderHeight();
    window.addEventListener("resize", syncHeaderHeight, { passive: true });

    var slides = Array.prototype.slice.call(root.querySelectorAll("[data-p45-slide]"));
    var dots = Array.prototype.slice.call(root.querySelectorAll("[data-p45-dot]"));
    var next = root.querySelector("[data-p45-next]");
    var prev = root.querySelector("[data-p45-prev]");
    var current = root.querySelector("[data-p45-current]");
    var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var index = 0;
    var timer = null;
    var touchStart = null;

    if (!slides.length) return;

    function pad(value) { return String(value).padStart(2, "0"); }

    function show(target, restart) {
      index = (target + slides.length) % slides.length;
      slides.forEach(function (slide, i) {
        var active = i === index;
        slide.classList.toggle("is-active", active);
        slide.setAttribute("aria-hidden", active ? "false" : "true");
        var link = slide.querySelector(".p45-hero__media");
        if (link) link.tabIndex = active ? 0 : -1;
      });
      dots.forEach(function (dot, i) {
        var active = i === index;
        dot.classList.toggle("is-active", active);
        dot.setAttribute("aria-current", active ? "true" : "false");
      });
      if (current) current.textContent = pad(index + 1);
      if (restart) start();
    }

    function stop() {
      if (timer) window.clearInterval(timer);
      timer = null;
    }

    function start() {
      stop();
      if (slides.length < 2 || reduced || document.hidden) return;
      timer = window.setInterval(function () { show(index + 1, false); }, 7000);
    }

    if (next) next.addEventListener("click", function () { show(index + 1, true); });
    if (prev) prev.addEventListener("click", function () { show(index - 1, true); });
    dots.forEach(function (dot) {
      dot.addEventListener("click", function () { show(Number(dot.getAttribute("data-p45-dot")) || 0, true); });
    });

    root.addEventListener("mouseenter", stop);
    root.addEventListener("mouseleave", start);
    root.addEventListener("focusin", stop);
    root.addEventListener("focusout", start);
    root.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft") show(index + 1, true);
      if (event.key === "ArrowRight") show(index - 1, true);
    });
    root.addEventListener("touchstart", function (event) {
      if (!event.changedTouches || !event.changedTouches.length) return;
      touchStart = event.changedTouches[0].clientX;
    }, { passive: true });
    root.addEventListener("touchend", function (event) {
      if (touchStart === null || !event.changedTouches || !event.changedTouches.length) return;
      var delta = event.changedTouches[0].clientX - touchStart;
      touchStart = null;
      if (Math.abs(delta) < 45) return;
      show(index + (delta < 0 ? -1 : 1), true);
    }, { passive: true });
    document.addEventListener("visibilitychange", function () { if (document.hidden) stop(); else start(); });

    show(0, false);
    start();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
