(function () {
  "use strict";

  var autocompleteMap = {
    first_name: "given-name",
    last_name: "family-name",
    phone: "tel",
    mobile: "tel",
    email: "email",
    username: "username",
    password: "current-password",
    password1: "new-password",
    password2: "new-password",
    password_confirm: "new-password",
    national_code: "off",
    q: "off"
  };

  function ensureId(field, index) {
    if (field.id) return field.id;
    var base = field.name || "field";
    field.id = "p491-" + base.replace(/[^a-zA-Z0-9_-]+/g, "-") + "-" + index;
    return field.id;
  }

  function hasAccessibleName(field) {
    if (field.getAttribute("aria-label") || field.getAttribute("aria-labelledby")) return true;
    if (field.closest("label")) return true;
    if (!field.id) return false;
    try {
      return !!document.querySelector('label[for="' + CSS.escape(field.id) + '"]');
    } catch (_error) {
      return false;
    }
  }

  function labelText(field) {
    return field.getAttribute("placeholder") || field.getAttribute("aria-label") || field.name || "فیلد فرم";
  }

  function enhance() {
    var fields = document.querySelectorAll("form input:not([type=hidden]), form select, form textarea");
    fields.forEach(function (field, index) {
      var id = ensureId(field, index);
      var key = (field.name || "").toLowerCase();
      if (!field.hasAttribute("autocomplete")) {
        if (autocompleteMap[key]) field.setAttribute("autocomplete", autocompleteMap[key]);
        else if (field.type === "search") field.setAttribute("autocomplete", "off");
      }
      if (!hasAccessibleName(field)) {
        var label = document.createElement("label");
        label.className = "p491-sr-only";
        label.htmlFor = id;
        label.textContent = labelText(field);
        field.parentNode.insertBefore(label, field);
      }
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", enhance);
  else enhance();
})();
