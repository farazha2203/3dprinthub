(() => {
    "use strict";

    const doc = document.documentElement;
    const body = document.body;
    const sidebar = document.querySelector(".app-menu.navbar-menu");
    const sidebarScroll = document.getElementById("scrollbar");
    const navbar = document.getElementById("navbar-nav");
    const mobileBreakpoint = 992;
    let sidebarSimpleBar = null;

    const normalizePath = (value) => {
        try {
            const url = new URL(value, window.location.origin);
            return url.pathname.replace(/\/+$/, "") || "/";
        } catch (_) {
            return String(value || "").replace(/\/+$/, "") || "/";
        }
    };

    const refreshSidebar = () => {
        window.requestAnimationFrame(() => {
            if (sidebarSimpleBar?.recalculate) sidebarSimpleBar.recalculate();
        });
    };

    const initSimpleBar = () => {
        if (!sidebarScroll || !window.SimpleBar) return;
        const existing = window.SimpleBar.instances?.get?.(sidebarScroll) || window.SimpleBar.getInstance?.(sidebarScroll);
        sidebarSimpleBar = existing || new window.SimpleBar(sidebarScroll, {
            autoHide: false,
            forceVisible: "y",
        });
        refreshSidebar();
    };

    const openAncestors = (link) => {
        let collapse = link.closest(".collapse.menu-dropdown");
        while (collapse) {
            collapse.classList.add("show");
            const trigger = document.querySelector(`[aria-controls="${CSS.escape(collapse.id)}"]`);
            trigger?.classList.add("active");
            trigger?.classList.remove("collapsed");
            trigger?.setAttribute("aria-expanded", "true");
            collapse = collapse.parentElement?.closest(".collapse.menu-dropdown") || null;
        }
    };

    const markActiveNavigation = () => {
        if (!navbar) return;
        const currentPath = normalizePath(window.location.pathname);
        let bestMatch = null;
        let bestLength = -1;

        navbar.querySelectorAll("a.nav-link[href]").forEach((link) => {
            const href = link.getAttribute("href") || "";
            if (!href || href.startsWith("#") || link.target === "_blank") return;
            const linkPath = normalizePath(link.href);
            const exact = currentPath === linkPath;
            const nested = linkPath !== "/admin" && linkPath !== "/" && currentPath.startsWith(`${linkPath}/`);
            if ((exact || nested) && linkPath.length > bestLength) {
                bestMatch = link;
                bestLength = linkPath.length;
            }
        });

        if (bestMatch) {
            bestMatch.classList.add("active");
            bestMatch.setAttribute("aria-current", "page");
            openAncestors(bestMatch);
            window.setTimeout(() => {
                bestMatch.scrollIntoView({ block: "nearest", behavior: "instant" });
                refreshSidebar();
            }, 60);
        }
    };

    const closeSiblingCollapses = (shownCollapse) => {
        const parentList = shownCollapse.parentElement?.parentElement;
        if (!parentList) return;
        parentList.querySelectorAll(":scope > .nav-item > .collapse.menu-dropdown.show").forEach((candidate) => {
            if (candidate === shownCollapse) return;
            window.bootstrap?.Collapse.getOrCreateInstance(candidate, { toggle: false }).hide();
        });
    };

    const initCollapses = () => {
        if (!navbar || !window.bootstrap) return;
        navbar.querySelectorAll(".collapse.menu-dropdown").forEach((collapse) => {
            window.bootstrap.Collapse.getOrCreateInstance(collapse, { toggle: false });
            collapse.addEventListener("show.bs.collapse", () => closeSiblingCollapses(collapse));
            collapse.addEventListener("shown.bs.collapse", refreshSidebar);
            collapse.addEventListener("hidden.bs.collapse", refreshSidebar);
        });
    };

    const setSidebarSize = (size) => {
        doc.setAttribute("data-sidebar-size", size);
        try {
            sessionStorage.setItem("data-sidebar-size", size);
        } catch (_) {
            // Storage may be disabled without affecting navigation.
        }
        refreshSidebar();
    };

    const closeMobileSidebar = () => {
        body.classList.remove("vertical-sidebar-enable");
        document.querySelector(".hamburger-icon")?.classList.remove("open");
    };

    const toggleSidebar = () => {
        if (window.innerWidth < mobileBreakpoint) {
            body.classList.toggle("vertical-sidebar-enable");
            document.querySelector(".hamburger-icon")?.classList.toggle("open");
            return;
        }
        const current = doc.getAttribute("data-sidebar-size") || "lg";
        setSidebarSize(current === "lg" ? "sm" : "lg");
    };

    const initSidebarControls = () => {
        document.getElementById("topnav-hamburger-icon")?.addEventListener("click", toggleSidebar);
        document.getElementById("vertical-hover")?.addEventListener("click", () => {
            if (window.innerWidth >= mobileBreakpoint) {
                const current = doc.getAttribute("data-sidebar-size") || "lg";
                setSidebarSize(current === "sm-hover" ? "lg" : "sm-hover");
            }
        });
        document.querySelector(".vertical-overlay")?.addEventListener("click", closeMobileSidebar);
        navbar?.querySelectorAll("a.nav-link:not([data-bs-toggle='collapse'])").forEach((link) => {
            link.addEventListener("click", () => {
                if (window.innerWidth < mobileBreakpoint) closeMobileSidebar();
            });
        });
        window.addEventListener("resize", () => {
            if (window.innerWidth >= mobileBreakpoint) closeMobileSidebar();
            refreshSidebar();
        });
    };

    const initTheme = () => {
        const button = document.querySelector(".light-dark-mode");
        if (!button) return;
        const applyIcon = () => {
            const dark = doc.getAttribute("data-bs-theme") === "dark";
            const icon = button.querySelector("i");
            if (icon) icon.className = dark ? "bx bx-sun fs-22" : "bx bx-moon fs-22";
        };
        button.addEventListener("click", () => {
            const next = doc.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
            doc.setAttribute("data-bs-theme", next);
            try {
                sessionStorage.setItem("data-bs-theme", next);
            } catch (_) {
                // Ignore unavailable storage.
            }
            applyIcon();
        });
        applyIcon();
    };

    const initFullscreen = () => {
        document.querySelectorAll("[data-toggle='fullscreen']").forEach((button) => {
            button.addEventListener("click", async () => {
                try {
                    if (!document.fullscreenElement) await document.documentElement.requestFullscreen();
                    else await document.exitFullscreen();
                } catch (_) {
                    // Fullscreen can be blocked by browser policy.
                }
            });
        });
    };

    const initMenuSearch = () => {
        const search = document.getElementById("admin-menu-search");
        const empty = document.getElementById("admin-menu-empty");
        if (!search || !navbar) return;

        const resetSearchState = () => {
            navbar.querySelectorAll("[data-admin-search-hidden='true']").forEach((element) => {
                element.hidden = false;
                delete element.dataset.adminSearchHidden;
            });
            navbar.querySelectorAll("[data-admin-search-open='true']").forEach((collapse) => {
                if (collapse.dataset.adminInitiallyOpen !== "true") {
                    collapse.classList.remove("show");
                    const trigger = document.querySelector(`[aria-controls="${CSS.escape(collapse.id)}"]`);
                    trigger?.classList.add("collapsed");
                    trigger?.setAttribute("aria-expanded", "false");
                }
                delete collapse.dataset.adminSearchOpen;
                delete collapse.dataset.adminInitiallyOpen;
            });
            navbar.querySelectorAll(":scope > .menu-title").forEach((title) => { title.hidden = false; });
            if (empty) empty.hidden = true;
        };

        search.addEventListener("input", () => {
            const query = search.value.trim().toLocaleLowerCase("fa-IR");
            resetSearchState();
            if (!query) {
                refreshSidebar();
                return;
            }

            let visibleCount = 0;
            navbar.querySelectorAll(":scope > .menu-title").forEach((title) => { title.hidden = true; });
            navbar.querySelectorAll(":scope > .nav-item").forEach((item) => {
                const leafLinks = Array.from(item.querySelectorAll("a.nav-link"));
                const matchingLinks = leafLinks.filter((link) => link.textContent.toLocaleLowerCase("fa-IR").includes(query));
                const matches = matchingLinks.length > 0;
                item.hidden = !matches;
                if (!matches) {
                    item.dataset.adminSearchHidden = "true";
                    return;
                }

                visibleCount += 1;
                item.querySelectorAll(".collapse.menu-dropdown").forEach((collapse) => {
                    collapse.dataset.adminInitiallyOpen = collapse.classList.contains("show") ? "true" : "false";
                    collapse.dataset.adminSearchOpen = "true";
                    collapse.classList.add("show");
                    const trigger = document.querySelector(`[aria-controls="${CSS.escape(collapse.id)}"]`);
                    trigger?.classList.remove("collapsed");
                    trigger?.setAttribute("aria-expanded", "true");
                });
                item.querySelectorAll(".menu-dropdown .nav-item").forEach((subItem) => {
                    const subMatches = subItem.textContent.toLocaleLowerCase("fa-IR").includes(query);
                    subItem.hidden = !subMatches;
                    if (!subMatches) subItem.dataset.adminSearchHidden = "true";
                });
            });
            if (empty) empty.hidden = visibleCount > 0;
            refreshSidebar();
        });
    };

    const initFormPresentation = () => {
        document.querySelectorAll("#content input:not([type='checkbox']):not([type='radio']):not([type='submit']):not([type='button']):not([type='hidden']):not([type='file']), #content textarea").forEach((element) => {
            element.classList.add("form-control");
        });
        document.querySelectorAll("#content select").forEach((element) => element.classList.add("form-select"));
        document.querySelectorAll("#content input[type='checkbox'], #content input[type='radio']").forEach((element) => element.classList.add("form-check-input"));
    };

    const initVelzonPlugins = () => {
        try { window.feather?.replace(); } catch (_) { /* Icon fallback remains visible. */ }
        try { window.Waves?.init(); } catch (_) { /* Decorative only. */ }

        if (window.Choices) {
            document.querySelectorAll("select[data-choices]:not([data-choice])").forEach((select) => {
                try { new window.Choices(select, { shouldSort: false, searchEnabled: select.options.length > 8 }); } catch (_) { /* Native select remains. */ }
            });
        }
        if (window.flatpickr) {
            if (window.flatpickr.l10ns?.fa) window.flatpickr.localize(window.flatpickr.l10ns.fa);
            document.querySelectorAll("[data-provider='flatpickr']").forEach((input) => {
                try { window.flatpickr(input, { allowInput: true, dateFormat: input.dataset.dateFormat || "Y-m-d" }); } catch (_) { /* Native input remains. */ }
            });
        }
    };

    const initRevenueChart = () => {
        const labelsElement = document.getElementById("admin-revenue-labels");
        const valuesElement = document.getElementById("admin-revenue-values");
        const chartElement = document.getElementById("admin-revenue-chart");
        if (!labelsElement || !valuesElement || !chartElement || !window.ApexCharts) return;
        try {
            const labels = JSON.parse(labelsElement.textContent);
            const values = JSON.parse(valuesElement.textContent);
            const chart = new window.ApexCharts(chartElement, {
                chart: { type: "area", height: 350, toolbar: { show: false }, fontFamily: "IRANSans, Tahoma, sans-serif" },
                series: [{ name: "درآمد", data: values }],
                xaxis: { categories: labels },
                yaxis: { labels: { formatter: (value) => new Intl.NumberFormat("fa-IR").format(Math.round(value)) } },
                dataLabels: { enabled: false },
                stroke: { curve: "smooth", width: 3 },
                colors: ["#c89b2c"],
                fill: { type: "gradient", gradient: { shadeIntensity: 1, opacityFrom: 0.35, opacityTo: 0.05, stops: [0, 90, 100] } },
                grid: { borderColor: "rgba(120, 140, 155, 0.18)", strokeDashArray: 4 },
                tooltip: { y: { formatter: (value) => `${new Intl.NumberFormat("fa-IR").format(value)} تومان` } },
            });
            chart.render();
        } catch (_) {
            chartElement.innerHTML = '<div class="alert alert-light mb-0">نمودار در این صفحه قابل نمایش نیست.</div>';
        }
    };

    const initUnreadBadge = () => {
        const badge = document.getElementById("admin-chat-unread-badge");
        if (!badge?.dataset.url) return;
        const update = async () => {
            try {
                const response = await fetch(badge.dataset.url, {
                    headers: { "X-Requested-With": "XMLHttpRequest" },
                    credentials: "same-origin",
                });
                if (!response.ok) return;
                const payload = await response.json();
                const count = Number(payload.unread || 0);
                badge.textContent = new Intl.NumberFormat("fa-IR").format(count);
                badge.hidden = count < 1;
                refreshSidebar();
            } catch (_) {
                // A polling failure must never affect the admin shell.
            }
        };
        update();
        window.setInterval(update, 15000);
    };

    const boot = () => {
        if (!sidebar || !navbar) return;
        initSimpleBar();
        initCollapses();
        markActiveNavigation();
        initSidebarControls();
        initTheme();
        initFullscreen();
        initMenuSearch();
        initFormPresentation();
        initVelzonPlugins();
        initRevenueChart();
        initUnreadBadge();
        body.classList.add("admin-shell-ready");
        refreshSidebar();
    };

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, { once: true });
    else boot();
})();
