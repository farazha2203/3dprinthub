(function () {
    "use strict";

    var host = window.location.hostname;
    var params = new URLSearchParams(window.location.search);
    var isLocal = host === "127.0.0.1" || host === "localhost" || host === "0.0.0.0";
    var forced = params.get("theme-preview") === "1";

    if (!isLocal && !forced) {
        return;
    }

    var STORAGE_KEY = "3dprinthub-theme-preview";
    var themes = {
        original: {
            label: "طراحی اصلی قبلی",
            vars: null,
            color: "#ff9800"
        },
        "brand-gold": {
            label: "طلایی و سرمه‌ای لوگو",
            color: "#d4a338",
            vars: {
                "--brand-primary": "#d4a338",
                "--brand-primary-dark": "#a97412",
                "--brand-secondary": "#071b2b",
                "--brand-graphite": "#102c42",
                "--brand-silver": "#d7dee7",
                "--brand-light": "#f7f8fa",
                "--brand-accent": "#d4a338"
            }
        },
        hybrid: {
            label: "ترکیبی پیشنهادی",
            color: "#f59e0b",
            vars: {
                "--brand-primary": "#f59e0b",
                "--brand-primary-dark": "#d97706",
                "--brand-secondary": "#071b2b",
                "--brand-graphite": "#1e293b",
                "--brand-silver": "#cbd5e1",
                "--brand-light": "#f8fafc",
                "--brand-accent": "#d4a338"
            }
        }
    };

    var variableNames = [
        "--brand-primary",
        "--brand-primary-dark",
        "--brand-secondary",
        "--brand-graphite",
        "--brand-silver",
        "--brand-light",
        "--brand-accent"
    ];

    function applyTheme(name) {
        var theme = themes[name] || themes.original;
        var root = document.documentElement;

        variableNames.forEach(function (variableName) {
            root.style.removeProperty(variableName);
        });

        if (theme.vars) {
            Object.keys(theme.vars).forEach(function (variableName) {
                root.style.setProperty(variableName, theme.vars[variableName]);
            });
            root.setAttribute("data-theme-preview", name);
        } else {
            root.removeAttribute("data-theme-preview");
        }

        var metaTheme = document.querySelector('meta[name="theme-color"]');
        if (metaTheme) {
            metaTheme.setAttribute("content", theme.color);
        }

        localStorage.setItem(STORAGE_KEY, name);
    }

    function buildPanel() {
        if (document.querySelector(".theme-preview-panel")) {
            return;
        }

        var panel = document.createElement("aside");
        panel.className = "theme-preview-panel";
        panel.setAttribute("aria-label", "پیش‌نمایش رنگ‌بندی سایت");

        var options = Object.keys(themes).map(function (key) {
            return '<option value="' + key + '">' + themes[key].label + "</option>";
        }).join("");

        panel.innerHTML =
            '<div class="theme-preview-panel__head">' +
                '<div class="theme-preview-panel__title">پیش‌نمایش رنگ‌بندی</div>' +
                '<span class="theme-preview-panel__badge">فقط محیط محلی</span>' +
            "</div>" +
            '<select id="theme-preview-select" aria-label="انتخاب رنگ‌بندی">' + options + "</select>" +
            '<div class="theme-preview-panel__actions">' +
                '<button type="button" id="theme-preview-reset">بازگشت به اصلی</button>' +
                '<button type="button" id="theme-preview-close">بستن پنل</button>' +
            "</div>" +
            '<p class="theme-preview-panel__hint">انتخاب فقط در مرورگر شما ذخیره می‌شود و روی هاست یا دیتابیس اثری ندارد.</p>';

        document.body.appendChild(panel);

        var select = document.getElementById("theme-preview-select");
        var current = localStorage.getItem(STORAGE_KEY) || "original";
        if (!themes[current]) current = "original";
        select.value = current;

        select.addEventListener("change", function () {
            applyTheme(select.value);
        });

        document.getElementById("theme-preview-reset").addEventListener("click", function () {
            select.value = "original";
            applyTheme("original");
        });

        document.getElementById("theme-preview-close").addEventListener("click", function () {
            panel.remove();
        });
    }

    var initial = localStorage.getItem(STORAGE_KEY) || "original";
    applyTheme(initial);

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", buildPanel);
    } else {
        buildPanel();
    }
})();
