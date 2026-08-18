(function () {
  "use strict";

  var root = document.querySelector("[data-p49c-engine]");
  if (!root) return;

  // Disable the legacy Phase45 engine even when its old cached JS is still loaded.
  root.removeAttribute("data-p45-hero");

  function boot() {
    var header = document.querySelector("header");
    var slides = Array.prototype.slice.call(root.querySelectorAll("[data-p45-slide]"));
    var dots = Array.prototype.slice.call(root.querySelectorAll("[data-p45-dot]"));
    var next = root.querySelector("[data-p45-next]");
    var prev = root.querySelector("[data-p45-prev]");
    var current = root.querySelector("[data-p45-current]");
    var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var index = 0;
    var timer = null;
    var transitionTimer = null;
    var touchStart = null;
    var transitioning = false;

    if (!slides.length) return;

    function syncHeaderHeight() {
      if (!header) return;
      var height = Math.max(0, Math.round(header.getBoundingClientRect().height));
      if (height) document.documentElement.style.setProperty("--p45-header-height", height + "px");
    }

    function numberAttr(slide, name, fallback, min, max) {
      var value = Number(slide && slide.getAttribute(name));
      if (!Number.isFinite(value)) value = fallback;
      return Math.max(min, Math.min(max, value));
    }

    function effectOf(slide) {
      var effect = String(slide && slide.getAttribute("data-p49c-effect") || "cinematic_fade");
      return reduced ? "cinematic_fade" : effect;
    }

    function transitionOf(slide) {
      return reduced ? 1 : numberAttr(slide, "data-p49c-transition", 1400, 300, 4000);
    }

    function displayOf(slide) {
      return numberAttr(slide, "data-p49c-display", 7000, 2000, 30000);
    }

    function pad(value) { return String(value).padStart(2, "0"); }

    function stop() {
      if (timer) window.clearTimeout(timer);
      timer = null;
    }

    function stopTransition() {
      if (transitionTimer) window.clearTimeout(transitionTimer);
      transitionTimer = null;
      transitioning = false;
    }

    function updateNavigation() {
      dots.forEach(function (dot, i) {
        var active = i === index;
        dot.classList.toggle("is-active", active);
        dot.setAttribute("aria-current", active ? "true" : "false");
      });
      if (current) current.textContent = pad(index + 1);
    }

    function normalizeSlides() {
      slides.forEach(function (slide, i) {
        var active = i === index;
        slide.classList.toggle("is-active", active);
        slide.classList.remove("is-entering", "is-leaving");
        slide.setAttribute("aria-hidden", active ? "false" : "true");
        var link = slide.querySelector(".p45-hero__media");
        if (link) link.tabIndex = active ? 0 : -1;
      });
      updateNavigation();
    }

    function schedule() {
      stop();
      if (slides.length < 2 || document.hidden) return;
      var wait = displayOf(slides[index]);
      timer = window.setTimeout(function () { go(index + 1, false); }, wait);
    }

    function go(target, restart) {
      if (slides.length < 2) return;
      var nextIndex = (target + slides.length) % slides.length;
      if (nextIndex === index || transitioning) {
        if (restart) schedule();
        return;
      }

      stop();
      stopTransition();
      transitioning = true;

      var outgoing = slides[index];
      var incoming = slides[nextIndex];
      var effect = effectOf(incoming);
      var duration = transitionOf(incoming);

      root.setAttribute("data-p49c-active-effect", effect);
      root.style.setProperty("--p49c-transition", duration + "ms");

      incoming.classList.add("is-active", "is-entering");
      incoming.classList.remove("is-leaving");
      incoming.setAttribute("aria-hidden", "false");
      var incomingLink = incoming.querySelector(".p45-hero__media");
      if (incomingLink) incomingLink.tabIndex = 0;

      outgoing.classList.add("is-active", "is-leaving");
      outgoing.classList.remove("is-entering");
      outgoing.setAttribute("aria-hidden", "true");
      var outgoingLink = outgoing.querySelector(".p45-hero__media");
      if (outgoingLink) outgoingLink.tabIndex = -1;

      index = nextIndex;
      updateNavigation();

      // Restart CSS animations even after rapid manual navigation.
      void root.offsetWidth;

      transitionTimer = window.setTimeout(function () {
        slides.forEach(function (slide, i) {
          slide.classList.remove("is-entering", "is-leaving");
          var active = i === index;
          slide.classList.toggle("is-active", active);
          slide.setAttribute("aria-hidden", active ? "false" : "true");
        });
        transitioning = false;
        transitionTimer = null;
        if (restart !== false || !document.hidden) schedule();
      }, duration + 40);
    }

    syncHeaderHeight();
    window.addEventListener("resize", syncHeaderHeight, { passive: true });
    normalizeSlides();

    if (next) next.addEventListener("click", function () { go(index + 1, true); });
    if (prev) prev.addEventListener("click", function () { go(index - 1, true); });
    dots.forEach(function (dot) {
      dot.addEventListener("click", function () {
        go(Number(dot.getAttribute("data-p45-dot")) || 0, true);
      });
    });

    root.addEventListener("mouseenter", stop);
    root.addEventListener("mouseleave", schedule);
    root.addEventListener("focusin", stop);
    root.addEventListener("focusout", schedule);
    root.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft") go(index + 1, true);
      if (event.key === "ArrowRight") go(index - 1, true);
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
      go(index + (delta < 0 ? -1 : 1), true);
    }, { passive: true });

    document.addEventListener("visibilitychange", function () {
      if (document.hidden) stop();
      else schedule();
    });

    schedule();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
