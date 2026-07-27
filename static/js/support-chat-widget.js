(function () {
    "use strict";

    var root = document.querySelector("[data-support-widget]");
    if (!root) return;

    var toggle = root.querySelector("[data-support-toggle]");
    var close = root.querySelector("[data-support-close]");
    var panel = root.querySelector("[data-support-panel]");
    var messages = root.querySelector("[data-support-widget-messages]");
    var form = root.querySelector("[data-support-widget-form]");
    var error = root.querySelector("[data-support-widget-error]");
    var badge = root.querySelector("[data-support-widget-badge]");
    var page = root.querySelector("[data-support-widget-page]");
    var stateUrl = root.dataset.stateUrl;
    var sendUrl = "";
    var messagesUrl = "";
    var lastId = 0;
    var loaded = false;

    function esc(value) {
        var div = document.createElement("div");
        div.textContent = value || "";
        return div.innerHTML;
    }

    function attachmentMarkup(message) {
        if (message.attachment_preview_url && message.attachment_kind === "image") {
            return '<a class="support-widget__attachment support-widget__attachment--image" href="' + esc(message.attachment_preview_url) + '" target="_blank"><img src="' + esc(message.attachment_preview_url) + '" alt="' + esc(message.attachment_name || "تصویر") + '"></a>';
        }
        if (message.attachment_preview_url && message.attachment_kind === "pdf") {
            return '<a class="support-widget__attachment" href="' + esc(message.attachment_preview_url) + '" target="_blank">مشاهده PDF: ' + esc(message.attachment_name || "پیوست") + '</a>';
        }
        return message.attachment_url
            ? '<a class="support-widget__attachment" href="' + esc(message.attachment_url) + '">دریافت ' + esc(message.attachment_name || "پیوست") + '</a>'
            : "";
    }

    function item(message) {
        return '<article class="support-widget__message ' + (message.is_mine ? "is-mine" : "") + '" data-id="' + message.id + '">' +
            '<small>' + esc(message.sender) + ' · ' + esc(message.created_at) + '</small>' +
            (message.body ? '<p>' + esc(message.body) + '</p>' : '') +
            attachmentMarkup(message) +
            '</article>';
    }

    function badgeSet(value) {
        var count = Number(value || 0);
        badge.textContent = new Intl.NumberFormat("fa-IR").format(count);
        badge.hidden = count < 1;
    }

    async function state(create) {
        try {
            var response = await fetch(stateUrl + (create ? "?create=1" : ""), {
                headers: {"X-Requested-With": "XMLHttpRequest"},
                credentials: "same-origin",
            });
            if (!response.ok) return;
            var payload = await response.json();
            sendUrl = payload.send_url;
            messagesUrl = payload.messages_url;
            page.href = payload.page_url;
            messages.innerHTML = (payload.messages || []).map(item).join("") || "<p>هنوز پیامی ثبت نشده است.</p>";
            (payload.messages || []).forEach(function (message) {
                lastId = Math.max(lastId, Number(message.id || 0));
            });
            messages.scrollTop = messages.scrollHeight;
            badgeSet(payload.unread);
            loaded = true;
        } catch (_) {
            // درخواست بعدی دوباره تلاش می‌کند.
        }
    }

    async function refresh() {
        if (!messagesUrl || panel.hidden) return;
        try {
            var url = messagesUrl + (lastId ? "?after=" + lastId : "");
            var response = await fetch(url, {
                headers: {"X-Requested-With": "XMLHttpRequest"},
                credentials: "same-origin",
            });
            if (!response.ok) return;
            var payload = await response.json();
            (payload.messages || []).forEach(function (message) {
                messages.insertAdjacentHTML("beforeend", item(message));
                lastId = Math.max(lastId, Number(message.id || 0));
            });
            if ((payload.messages || []).length) {
                messages.scrollTop = messages.scrollHeight;
                badgeSet(0);
            }
        } catch (_) {
            // درخواست بعدی دوباره تلاش می‌کند.
        }
    }

    toggle.addEventListener("click", function () {
        panel.hidden = !panel.hidden;
        toggle.setAttribute("aria-expanded", String(!panel.hidden));
        if (!panel.hidden) {
            if (!loaded) state(true);
            else refresh();
        }
    });

    close.addEventListener("click", function () {
        panel.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
    });

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        error.hidden = true;
        if (!sendUrl) await state(true);
        try {
            var response = await fetch(sendUrl, {
                method: "POST",
                body: new FormData(form),
                headers: {"X-Requested-With": "XMLHttpRequest"},
                credentials: "same-origin",
            });
            var payload = await response.json();
            if (!response.ok || !payload.ok) throw new Error(payload.error || "ارسال پیام ناموفق بود.");
            messages.insertAdjacentHTML("beforeend", item(payload.message));
            lastId = Math.max(lastId, Number(payload.message.id || 0));
            messages.scrollTop = messages.scrollHeight;
            form.reset();
        } catch (exception) {
            error.textContent = exception.message;
            error.hidden = false;
        }
    });

    window.setInterval(function () {
        if (loaded) refresh();
    }, 15000);
})();
