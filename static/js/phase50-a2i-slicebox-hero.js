(function () {
  "use strict";

  function reducedMotion() {
    return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }

  function supported() {
    return !!(window.CSS && CSS.supports && CSS.supports("transform-style", "preserve-3d"));
  }

  function usable(root, outgoing, incoming) {
    if (!root || !outgoing || !incoming || reducedMotion() || !supported()) return false;
    if (window.innerWidth < 721) return false;
    return !!(outgoing.querySelector(".p45-hero__media img") && incoming.querySelector(".p45-hero__media img"));
  }

  function face(className, sourceImage) {
    var node = document.createElement("span");
    node.className = "p50i-slicebox__face " + className;
    var image = sourceImage.cloneNode(true);
    image.removeAttribute("loading");
    image.removeAttribute("fetchpriority");
    image.setAttribute("aria-hidden", "true");
    node.appendChild(image);
    return node;
  }
  function play(root, outgoing, incoming, duration, direction) {
    if (!usable(root, outgoing, incoming)) return false;
    var media = incoming.querySelector(".p45-hero__media");
    var outgoingImage = outgoing.querySelector(".p45-hero__media img");
    var incomingImage = incoming.querySelector(".p45-hero__media img");
    if (!media || !outgoingImage || !incomingImage) return false;

    var old = media.querySelector(".p50i-slicebox");
    if (old) old.remove();

    var overlay = document.createElement("span");
    overlay.className = "p50i-slicebox";
    overlay.setAttribute("aria-hidden", "true");
    overlay.style.setProperty("--p50i-duration", Math.max(500, duration - 320) + "ms");
    overlay.style.setProperty("--p50i-turn", direction < 0 ? "-180deg" : "180deg");
    var slices = 7;

    for (var i = 0; i < slices; i += 1) {
      var slice = document.createElement("span");
      slice.className = "p50i-slicebox__slice";
      slice.style.setProperty("--p50i-index", String(i));
      slice.style.setProperty("--p50i-left", ((i * 100) / slices) + "%");
      slice.style.setProperty("--p50i-right", (((slices - i - 1) * 100) / slices) + "%");
      slice.style.setProperty("--p50i-origin", (((i + 0.5) * 100) / slices) + "%");
      slice.appendChild(face("p50i-slicebox__face--front", outgoingImage));
      slice.appendChild(face("p50i-slicebox__face--back", incomingImage));
      overlay.appendChild(slice);
    }
    media.appendChild(overlay);
    root.classList.add("p50i-slicebox-active");
    void overlay.offsetWidth;
    overlay.classList.add("is-playing");

    window.setTimeout(function () {
      overlay.remove();
      root.classList.remove("p50i-slicebox-active");
    }, Math.max(600, duration) + 100);

    return true;
  }

  window.P50SliceboxHero = { play: play };
})();
