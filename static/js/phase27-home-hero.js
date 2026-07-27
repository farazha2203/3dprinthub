(function () {
  "use strict";

  function classifySlide(slide, image) {
    if (!slide || !image || !image.naturalWidth || !image.naturalHeight) return;
    var ratio = image.naturalWidth / image.naturalHeight;
    slide.classList.remove("is-portrait", "is-square", "is-landscape");
    if (ratio < 0.82) slide.classList.add("is-portrait");
    else if (ratio < 1.22) slide.classList.add("is-square");
    else slide.classList.add("is-landscape");
  }

  function initImagePair(slide) {
    var images = Array.prototype.slice.call(slide.querySelectorAll("img[data-p27-fallback]"));
    if (!images.length) return;
    var fallback = images[0].getAttribute("data-p27-fallback") || "";
    var subject = slide.querySelector(".p27-home-hero__subject") || images[0];
    var switched = false;

    function useFallback() {
      if (switched || !fallback) return;
      switched = true;
      slide.classList.add("p27-home-hero__slide--fallback");
      images.forEach(function (image) {
        image.removeAttribute("data-p27-fallback");
        if (image.src !== fallback) image.src = fallback;
        image.classList.add("is-fallback");
      });
    }

    images.forEach(function (image) {
      image.addEventListener("error", useFallback, { once: true });
    });
    subject.addEventListener("load", function () { classifySlide(slide, subject); });
    if (subject.complete && subject.naturalWidth) classifySlide(slide, subject);
  }

  function initHero() {
    var root = document.querySelector("[data-p27-home-hero]");
    if (!root) return;

    var slider = root.querySelector("[data-p27-hero-slider]");
    var slides = Array.prototype.slice.call(root.querySelectorAll("[data-p27-hero-slide]"));
    var captions = Array.prototype.slice.call(root.querySelectorAll("[data-p27-hero-caption]"));
    var dots = Array.prototype.slice.call(root.querySelectorAll("[data-p27-hero-dot]"));
    var next = root.querySelector("[data-p27-hero-next]");
    var prev = root.querySelector("[data-p27-hero-prev]");
    var reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var index = 0;
    var timer = null;

    slides.forEach(initImagePair);

    if (slides.length < 2) return;

    function show(target) {
      index = (target + slides.length) % slides.length;
      slides.forEach(function (item, itemIndex) {
        item.classList.toggle("is-active", itemIndex === index);
        item.setAttribute("aria-hidden", itemIndex === index ? "false" : "true");
        item.tabIndex = itemIndex === index ? 0 : -1;
      });
      captions.forEach(function (item, itemIndex) {
        item.classList.toggle("is-active", itemIndex === index);
        item.tabIndex = itemIndex === index ? 0 : -1;
      });
      dots.forEach(function (item, itemIndex) {
        item.classList.toggle("is-active", itemIndex === index);
        item.setAttribute("aria-current", itemIndex === index ? "true" : "false");
      });
    }

    function stop() {
      if (timer) {
        window.clearInterval(timer);
        timer = null;
      }
    }

    function start() {
      stop();
      if (!reducedMotion && !document.hidden) {
        timer = window.setInterval(function () { show(index + 1); }, 6500);
      }
    }

    if (next) next.addEventListener("click", function () { show(index + 1); start(); });
    if (prev) prev.addEventListener("click", function () { show(index - 1); start(); });
    dots.forEach(function (dot) {
      dot.addEventListener("click", function () {
        show(Number(dot.getAttribute("data-p27-hero-dot")) || 0);
        start();
      });
    });

    root.addEventListener("mouseenter", stop);
    root.addEventListener("mouseleave", start);
    root.addEventListener("focusin", stop);
    root.addEventListener("focusout", start);
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) stop(); else start();
    });
    if (slider) {
      var touchStart = null;
      slider.addEventListener("touchstart", function (event) {
        touchStart = event.changedTouches[0].clientX;
      }, { passive: true });
      slider.addEventListener("touchend", function (event) {
        if (touchStart === null) return;
        var delta = event.changedTouches[0].clientX - touchStart;
        touchStart = null;
        if (Math.abs(delta) < 45) return;
        show(index + (delta < 0 ? -1 : 1));
        start();
      }, { passive: true });
    }

    show(0);
    start();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initHero);
  } else {
    initHero();
  }
})();
