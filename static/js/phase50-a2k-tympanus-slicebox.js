(function (window, document) {
  "use strict";

  function boot() {
    var root = document.querySelector("[data-p50k-slicebox]");
    if (!root || !window.jQuery || !window.jQuery.fn || !window.jQuery.fn.slicebox) return;

    var $ = window.jQuery;
    var legacyShadow = root.querySelector("#shadow");
    if (legacyShadow) legacyShadow.remove();

    var $slider = $("#sb-slider");
    if (!$slider.length || $slider.children("li").length < 1) return;

    var $navArrows = $("#nav-arrows").hide();
    var $navDots = $("#nav-dots").hide();
    var $nav = $navDots.children("span");

    var slicebox = $slider.slicebox({
      orientation: "r",
      cuboidsRandom: true,
      disperseFactor: 30,
      onReady: function () {
        $navArrows.show();
        $navDots.show();
      },
      onBeforeChange: function (position) {
        $nav.removeClass("nav-dot-current");
        $nav.eq(position).addClass("nav-dot-current");
      }
    });

    $navArrows.children(":first").on("click", function (event) {
      event.preventDefault();
      slicebox.next();
    });

    $navArrows.children(":last").on("click", function (event) {
      event.preventDefault();
      slicebox.previous();
    });

    $nav.each(function (index) {
      $(this).on("click keydown", function (event) {
        if (
          event.type === "keydown" &&
          event.key !== "Enter" &&
          event.key !== " "
        ) return;
        event.preventDefault();
        slicebox.jump(index + 1);
      });
    });

    root.dataset.p50kReady = "1";
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})(window, document);
