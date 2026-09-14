(function () {
  "use strict";

  function reducedMotion() {
    return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }

  function supported() {
    return !!(window.CSS && CSS.supports && CSS.supports("transform-style", "preserve-3d") && CSS.supports("perspective", "1000px"));
  }

  function numberAttr(root, name, fallback, min, max) {
    var value = Number(root && root.getAttribute(name));
    if (!Number.isFinite(value)) value = fallback;
    return Math.max(min, Math.min(max, value));
  }

  function usable(root, outgoing, incoming) {
    if (!root || !outgoing || !incoming || reducedMotion() || !supported()) return false;
    if (window.innerWidth < 721) return false;
    return !!(outgoing.querySelector(".p45-hero__media img") && incoming.querySelector(".p45-hero__media img"));
  }

  function randomOdd(maximum) {
    var odds = [];
    for (var value = 3; value <= maximum; value += 2) odds.push(value);
    return odds[Math.floor(Math.random() * odds.length)] || 5;
  }

  function config(root) {
    var requested = String(root.getAttribute("data-p50i-orientation") || "r").toLowerCase();
    var orientation = requested === "r" ? (Math.random() > 0.5 ? "v" : "h") : requested;
    if (orientation !== "v" && orientation !== "h") orientation = "v";
    var maximum = Math.round(numberAttr(root, "data-p50i-max-cuboids", 7, 3, 11));
    if (maximum % 2 === 0) maximum -= 1;
    var count = root.getAttribute("data-p50i-cuboids-random") === "false"
      ? Math.round(numberAttr(root, "data-p50i-cuboids-count", 5, 3, 11))
      : randomOdd(maximum);
    if (count % 2 === 0) count += 1;
    return {
      orientation: orientation,
      count: Math.max(3, Math.min(11, count)),
      perspective: numberAttr(root, "data-p50i-perspective", 1200, 700, 2400),
      disperse: numberAttr(root, "data-p50i-disperse", 28, 0, 90),
      sequential: numberAttr(root, "data-p50i-sequential", 85, 25, 220)
    };
  }

  function imageClone(source, rect, offsetX, offsetY) {
    var image = source.cloneNode(true);
    image.className = "p50i-slicebox__image";
    image.removeAttribute("loading");
    image.removeAttribute("fetchpriority");
    image.removeAttribute("width");
    image.removeAttribute("height");
    image.setAttribute("aria-hidden", "true");
    image.style.width = rect.width + "px";
    image.style.height = rect.height + "px";
    image.style.left = (-offsetX) + "px";
    image.style.top = (-offsetY) + "px";
    var computed = window.getComputedStyle(source);
    image.style.objectFit = computed.objectFit || "cover";
    image.style.objectPosition = computed.objectPosition || "50% 50%";
    return image;
  }

  function face(className, source, rect, offsetX, offsetY) {
    var node = document.createElement("span");
    node.className = "p50i-slicebox__face " + className;
    if (source) node.appendChild(imageClone(source, rect, offsetX, offsetY));
    return node;
  }

  function play(root, outgoing, incoming, duration, direction) {
    if (!usable(root, outgoing, incoming)) return false;
    var media = incoming.querySelector(".p45-hero__media");
    var outgoingImage = outgoing.querySelector(".p45-hero__media img");
    var incomingImage = incoming.querySelector(".p45-hero__media img");
    if (!media || !outgoingImage || !incomingImage) return false;

    var rect = media.getBoundingClientRect();
    if (rect.width < 320 || rect.height < 220) return false;
    var old = media.querySelector(".p50i-slicebox");
    if (old) old.remove();

    var cfg = config(root);
    var overlay = document.createElement("span");
    overlay.className = "p50i-slicebox p50i-slicebox--" + cfg.orientation;
    overlay.setAttribute("aria-hidden", "true");
    overlay.setAttribute("data-orientation", cfg.orientation);
    overlay.style.setProperty("--p50i-perspective", cfg.perspective + "px");
    overlay.style.setProperty("--p50i-duration", Math.max(520, duration - 260) + "ms");
    overlay.style.setProperty("--p50i-sequential", cfg.sequential + "ms");

    var vertical = cfg.orientation === "v";
    var sliceWidth = vertical ? rect.width / cfg.count : rect.width;
    var sliceHeight = vertical ? rect.height : rect.height / cfg.count;
    var depth = vertical ? sliceWidth : sliceHeight;
    var middle = (cfg.count - 1) / 2;
    var sign = direction < 0 ? -1 : 1;

    for (var i = 0; i < cfg.count; i += 1) {
      var x = vertical ? i * sliceWidth : 0;
      var y = vertical ? 0 : i * sliceHeight;
      var cuboid = document.createElement("span");
      cuboid.className = "p50i-slicebox__cuboid";
      cuboid.style.left = x + "px";
      cuboid.style.top = y + "px";
      cuboid.style.width = (sliceWidth + 0.6) + "px";
      cuboid.style.height = (sliceHeight + 0.6) + "px";
      cuboid.style.setProperty("--p50i-depth", depth + "px");
      cuboid.style.setProperty("--p50i-delay-index", String(i));
      cuboid.style.setProperty("--p50i-disp", ((i - middle) * cfg.disperse) + "px");
      if (vertical) {
        cuboid.style.setProperty("--p50i-next-turn", (90 * sign) + "deg");
        cuboid.style.setProperty("--p50i-back-turn", (180 * sign) + "deg");
        cuboid.style.setProperty("--p50i-other-turn", (-90 * sign) + "deg");
        cuboid.style.setProperty("--p50i-cuboid-turn", (-90 * sign) + "deg");
      } else {
        cuboid.style.setProperty("--p50i-next-turn", (-90 * sign) + "deg");
        cuboid.style.setProperty("--p50i-back-turn", (-180 * sign) + "deg");
        cuboid.style.setProperty("--p50i-other-turn", (90 * sign) + "deg");
        cuboid.style.setProperty("--p50i-cuboid-turn", (90 * sign) + "deg");
      }
      cuboid.appendChild(face("p50i-slicebox__face--front", outgoingImage, rect, x, y));
      cuboid.appendChild(face("p50i-slicebox__face--next", incomingImage, rect, x, y));
      cuboid.appendChild(face("p50i-slicebox__face--back", null, rect, x, y));
      cuboid.appendChild(face("p50i-slicebox__face--other", null, rect, x, y));
      overlay.appendChild(cuboid);
    }

    media.appendChild(overlay);
    root.classList.add("p50i-slicebox-active");
    root.setAttribute("data-p50i-live-orientation", cfg.orientation);
    root.setAttribute("data-p50i-live-cuboids", String(cfg.count));
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () { overlay.classList.add("is-playing"); });
    });

    var total = Math.max(600, duration) + cfg.sequential * cfg.count + 160;
    window.setTimeout(function () {
      overlay.remove();
      root.classList.remove("p50i-slicebox-active");
    }, total);
    return true;
  }

  window.P50SliceboxHero = { play: play };
})();
