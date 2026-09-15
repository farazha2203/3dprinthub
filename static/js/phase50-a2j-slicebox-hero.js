(function () {
  "use strict";

  var root = document.querySelector("[data-p50j-slicebox]");
  if (!root) return;

  function boot() {
    var viewport = root.querySelector("[data-p50j-viewport]");
    var stage = root.querySelector("[data-p50j-stage]");
    var slides = Array.prototype.slice.call(root.querySelectorAll("[data-p50j-slide]"));
    var dots = Array.prototype.slice.call(root.querySelectorAll("[data-p50j-dot]"));
    var next = root.querySelector("[data-p50j-next]");
    var prev = root.querySelector("[data-p50j-prev]");
    var current = root.querySelector("[data-p50j-current]");
    var header = document.querySelector("header");
    var reduceQuery = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
    var index = 0;
    var timer = null;
    var cleanupTimer = null;
    var overlay = null;
    var touchStartX = null;
    var touchStartY = null;
    var transitioning = false;

    if (!viewport || !stage || !slides.length) return;

    function numeric(node, name, fallback, min, max) {
      var value = Number(node && node.getAttribute(name));
      if (!Number.isFinite(value)) value = fallback;
      return Math.max(min, Math.min(max, value));
    }

    function pad(value) {
      return String(value).padStart(2, "0");
    }

    function reducedMotion() {
      return !!(reduceQuery && reduceQuery.matches);
    }

    function css3dSupported() {
      return !!(
        window.CSS &&
        CSS.supports &&
        CSS.supports("transform-style", "preserve-3d") &&
        CSS.supports("perspective", "1000px")
      );
    }

    function use3d() {
      return !reducedMotion() && css3dSupported() && window.innerWidth >= 721;
    }

    function syncHeaderHeight() {
      if (!header) return;
      var height = Math.max(0, Math.round(header.getBoundingClientRect().height));
      if (height) document.documentElement.style.setProperty("--p50j-header-height", height + "px");
    }

    function orientation() {
      var requested = String(root.getAttribute("data-p50j-orientation") || "r").toLowerCase();
      if (requested === "h" || requested === "v") return requested;
      return Math.random() >= 0.5 ? "v" : "h";
    }

    function cuboidCount() {
      var random = root.getAttribute("data-p50j-cuboids-random") !== "false";
      var max = Math.round(numeric(root, "data-p50j-max-cuboids", 7, 3, 11));
      if (max % 2 === 0) max -= 1;
      if (!random) {
        var fixed = Math.round(numeric(root, "data-p50j-cuboids-count", 5, 3, 11));
        return fixed % 2 === 0 ? Math.min(11, fixed + 1) : fixed;
      }
      var options = [];
      for (var count = 3; count <= max; count += 2) options.push(count);
      return options[Math.floor(Math.random() * options.length)] || 5;
    }

    function displayDuration(slide) {
      return numeric(slide, "data-p50j-display", 7000, 2000, 30000);
    }

    function transitionDuration(slide) {
      return reducedMotion() ? 260 : numeric(slide, "data-p50j-transition", 1400, 500, 3600);
    }

    function clearTimer() {
      if (timer) window.clearTimeout(timer);
      timer = null;
    }

    function removeOverlay() {
      if (cleanupTimer) window.clearTimeout(cleanupTimer);
      cleanupTimer = null;
      if (overlay) overlay.remove();
      overlay = null;
      root.classList.remove("p50j-is-transitioning");
      root.removeAttribute("data-p50j-live-orientation");
      root.removeAttribute("data-p50j-live-cuboids");
    }

    function setActive(nextIndex) {
      index = nextIndex;
      slides.forEach(function (slide, slideIndex) {
        var active = slideIndex === index;
        slide.classList.toggle("is-active", active);
        slide.classList.remove("is-source", "is-entering");
        slide.setAttribute("aria-hidden", active ? "false" : "true");
        var links = slide.querySelectorAll("a,button");
        Array.prototype.forEach.call(links, function (node) {
          if (node.hasAttribute("data-p50j-control-exempt")) return;
          node.tabIndex = active ? 0 : -1;
        });
      });
      dots.forEach(function (dot, dotIndex) {
        var active = dotIndex === index;
        dot.classList.toggle("is-active", active);
        dot.setAttribute("aria-current", active ? "true" : "false");
        dot.setAttribute("aria-selected", active ? "true" : "false");
      });
      if (current) current.textContent = pad(index + 1);
    }

    function cloneImage(source, rect, offsetX, offsetY) {
      var image = source.cloneNode(true);
      image.className = "p50j-slicebox__image";
      image.removeAttribute("loading");
      image.removeAttribute("fetchpriority");
      image.removeAttribute("width");
      image.removeAttribute("height");
      image.setAttribute("aria-hidden", "true");
      image.style.width = rect.width + "px";
      image.style.height = rect.height + "px";
      image.style.left = -offsetX + "px";
      image.style.top = -offsetY + "px";
      var computed = window.getComputedStyle(source);
      image.style.objectFit = computed.objectFit || "cover";
      image.style.objectPosition = computed.objectPosition || "50% 50%";
      return image;
    }

    function face(className, source, rect, offsetX, offsetY) {
      var node = document.createElement("span");
      node.className = "p50j-slicebox__face " + className;
      if (source) node.appendChild(cloneImage(source, rect, offsetX, offsetY));
      return node;
    }

    function createSlicebox(outgoing, incoming, direction, duration) {
      var outgoingImage = outgoing.querySelector(".p50j-hero__media img");
      var incomingImage = incoming.querySelector(".p50j-hero__media img");
      if (!outgoingImage || !incomingImage || !use3d()) return null;

      var rect = stage.getBoundingClientRect();
      if (rect.width < 320 || rect.height < 220) return null;

      var mode = orientation();
      var count = cuboidCount();
      var sequential = numeric(root, "data-p50j-sequential", 85, 20, 220);
      var perspective = numeric(root, "data-p50j-perspective", 1200, 700, 2600);
      var disperse = numeric(root, "data-p50j-disperse", 28, 0, 90);
      var vertical = mode === "v";
      var sliceWidth = vertical ? rect.width / count : rect.width;
      var sliceHeight = vertical ? rect.height : rect.height / count;
      var depth = vertical ? sliceWidth : sliceHeight;
      var middle = (count - 1) / 2;
      var sign = direction < 0 ? -1 : 1;
      var node = document.createElement("div");
      node.className = "p50j-slicebox p50j-slicebox--" + mode;
      node.setAttribute("aria-hidden", "true");
      node.style.setProperty("--p50j-perspective", perspective + "px");
      node.style.setProperty("--p50j-duration", Math.max(540, duration - 180) + "ms");
      node.style.setProperty("--p50j-sequential", sequential + "ms");

      for (var i = 0; i < count; i += 1) {
        var x = vertical ? i * sliceWidth : 0;
        var y = vertical ? 0 : i * sliceHeight;
        var cuboid = document.createElement("span");
        cuboid.className = "p50j-slicebox__cuboid";
        cuboid.style.left = x + "px";
        cuboid.style.top = y + "px";
        cuboid.style.width = sliceWidth + 0.75 + "px";
        cuboid.style.height = sliceHeight + 0.75 + "px";
        cuboid.style.setProperty("--p50j-depth", depth + "px");
        cuboid.style.setProperty("--p50j-index", String(i));
        cuboid.style.setProperty("--p50j-disp", (i - middle) * disperse + "px");
        cuboid.style.setProperty("--p50j-turn", (vertical ? -90 : 90) * sign + "deg");
        cuboid.style.setProperty("--p50j-next-turn", (vertical ? 90 : -90) * sign + "deg");
        cuboid.appendChild(face("p50j-slicebox__face--front", outgoingImage, rect, x, y));
        cuboid.appendChild(face("p50j-slicebox__face--next", incomingImage, rect, x, y));
        cuboid.appendChild(face("p50j-slicebox__face--back", null, rect, x, y));
        cuboid.appendChild(face("p50j-slicebox__face--side", null, rect, x, y));
        node.appendChild(cuboid);
      }

      root.setAttribute("data-p50j-live-orientation", mode);
      root.setAttribute("data-p50j-live-cuboids", String(count));
      node.dataset.totalDuration = String(duration + sequential * count + 160);
      return node;
    }

    function schedule() {
      clearTimer();
      if (slides.length < 2 || document.hidden || transitioning) return;
      timer = window.setTimeout(function () {
        go(index + 1, false);
      }, displayDuration(slides[index]));
    }

    function finishTransition(nextIndex) {
      removeOverlay();
      setActive(nextIndex);
      transitioning = false;
      schedule();
    }

    function fallbackTransition(outgoing, incoming, nextIndex, duration) {
      root.classList.add("p50j-is-transitioning", "p50j-fallback-transition");
      outgoing.classList.add("is-source");
      incoming.classList.add("is-active", "is-entering");
      incoming.setAttribute("aria-hidden", "false");
      cleanupTimer = window.setTimeout(function () {
        root.classList.remove("p50j-fallback-transition");
        finishTransition(nextIndex);
      }, Math.max(220, duration));
    }

    function go(target, manual) {
      if (slides.length < 2) return;
      var nextIndex = (Number(target) + slides.length) % slides.length;
      if (nextIndex === index) {
        if (manual) schedule();
        return;
      }
      if (transitioning) return;

      clearTimer();
      removeOverlay();
      transitioning = true;
      var outgoing = slides[index];
      var incoming = slides[nextIndex];
      var duration = transitionDuration(incoming);
      var direction = nextIndex > index ? 1 : -1;
      if (index === slides.length - 1 && nextIndex === 0) direction = 1;
      if (index === 0 && nextIndex === slides.length - 1) direction = -1;

      overlay = createSlicebox(outgoing, incoming, direction, duration);
      if (!overlay) {
        fallbackTransition(outgoing, incoming, nextIndex, duration);
        return;
      }

      outgoing.classList.add("is-source");
      incoming.classList.add("is-active", "is-entering");
      incoming.setAttribute("aria-hidden", "false");
      root.classList.add("p50j-is-transitioning");
      stage.appendChild(overlay);
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () {
          if (overlay) overlay.classList.add("is-playing");
        });
      });
      cleanupTimer = window.setTimeout(function () {
        finishTransition(nextIndex);
      }, Number(overlay.dataset.totalDuration || duration + 500));
    }

    syncHeaderHeight();
    setActive(0);
    root.setAttribute("data-p50j-ready", "true");

    if (next) next.addEventListener("click", function () { go(index + 1, true); });
    if (prev) prev.addEventListener("click", function () { go(index - 1, true); });
    dots.forEach(function (dot) {
      dot.addEventListener("click", function () {
        go(Number(dot.getAttribute("data-p50j-dot") || 0), true);
      });
    });

    root.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        go(index + 1, true);
      } else if (event.key === "ArrowRight") {
        event.preventDefault();
        go(index - 1, true);
      }
    });

    root.addEventListener("touchstart", function (event) {
      if (!event.changedTouches || !event.changedTouches.length) return;
      touchStartX = event.changedTouches[0].clientX;
      touchStartY = event.changedTouches[0].clientY;
    }, { passive: true });
    root.addEventListener("touchend", function (event) {
      if (touchStartX === null || touchStartY === null || !event.changedTouches || !event.changedTouches.length) return;
      var deltaX = event.changedTouches[0].clientX - touchStartX;
      var deltaY = event.changedTouches[0].clientY - touchStartY;
      touchStartX = null;
      touchStartY = null;
      if (Math.abs(deltaX) < 45 || Math.abs(deltaX) < Math.abs(deltaY)) return;
      go(index + (deltaX < 0 ? -1 : 1), true);
    }, { passive: true });

    root.addEventListener("mouseenter", clearTimer);
    root.addEventListener("mouseleave", schedule);
    root.addEventListener("focusin", clearTimer);
    root.addEventListener("focusout", function () {
      window.setTimeout(function () {
        if (!root.contains(document.activeElement)) schedule();
      }, 0);
    });

    document.addEventListener("visibilitychange", function () {
      if (document.hidden) clearTimer();
      else schedule();
    });
    window.addEventListener("resize", function () {
      syncHeaderHeight();
      if (transitioning) {
        removeOverlay();
        transitioning = false;
        setActive(index);
      }
      schedule();
    }, { passive: true });
    if (reduceQuery && typeof reduceQuery.addEventListener === "function") {
      reduceQuery.addEventListener("change", function () {
        if (transitioning) {
          removeOverlay();
          transitioning = false;
          setActive(index);
        }
        schedule();
      });
    }

    schedule();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, { once: true });
  else boot();
})();
