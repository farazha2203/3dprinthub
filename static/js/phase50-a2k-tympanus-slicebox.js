(function (window, document) {
  "use strict";

  function boot() {
    var root = document.querySelector("[data-p50k-slicebox]");
    if (!root || !window.jQuery || !window.jQuery.fn || !window.jQuery.fn.slicebox) return;
    var $ = window.jQuery;
    var $slider = $("#sb-slider");
    if (!$slider.length || $slider.children("li").length < 1) return;

    var $navArrows = $("#nav-arrows").hide();
    var $navOptions = $("#nav-options").hide();
    var $navDots = $("#nav-dots").hide();
    var $nav = $navDots.children("span");
    var $shadow = $("#shadow").hide();

    var slicebox = $slider.slicebox({
      orientation: "r",
      cuboidsRandom: true,
      maxCuboidsCount: 7,
      disperseFactor: 30,
      sequentialFactor: 120,
      speed: 600,
      autoplay: true,
      interval: 6000,
      onReady: function () {
        $navArrows.show();
        $navOptions.show();
        $navDots.show();
        $shadow.show();
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
    $("#navPlay").on("click keydown", function (event) {
      if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      slicebox.play();
    });
    $("#navPause").on("click keydown", function (event) {
      if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      slicebox.pause();
    });
    $nav.each(function (index) {
      $(this).on("click keydown", function (event) {
        if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        slicebox.jump(index + 1);
      });
    });
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) slicebox.pause();
      else slicebox.play();
    });
    root.dataset.p50kReady = "1";
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})(window, document);
