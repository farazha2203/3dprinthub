(function () {
  "use strict";

  function boot() {
    document.querySelectorAll("[data-p49c-description]").forEach(function (control) {
      var label = control.querySelector("[data-p49c-description-more]");

      function setExpanded(expanded) {
        control.classList.toggle("is-expanded", expanded);
        control.setAttribute("aria-expanded", expanded ? "true" : "false");
        if (label) label.textContent = expanded ? "بستن توضیحات" : "نمایش بیشتر";
      }

      control.addEventListener("click", function () {
        setExpanded(control.getAttribute("aria-expanded") !== "true");
      });
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
