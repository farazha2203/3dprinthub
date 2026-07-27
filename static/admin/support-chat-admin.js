(function () {
    "use strict";

    var root = document.querySelector("[data-admin-support-chat]");
    if (!root) return;

    var box = root.querySelector("[data-admin-chat-messages]");
    var form = root.querySelector("[data-admin-chat-form]");
    var error = root.querySelector("[data-admin-chat-error]");
    var fileInput = form.querySelector('input[name="attachment"]');
    var fileLabel = root.querySelector("[data-admin-chat-file]");
    var lastId = 0;
    var busy = false;

    function esc(value) {
        var div = document.createElement("div");
        div.textContent = value || "";
        return div.innerHTML;
    }

    function attachmentMarkup(message) {
        if (message.attachment_preview_url && message.attachment_kind === "image") {
            return '<a class="admin-chat-attachment admin-chat-attachment--image" href="' + esc(message.attachment_preview_url) + '" target="_blank"><img src="' + esc(message.attachment_preview_url) + '" alt="' + esc(message.attachment_name || "تصویر") + '"><span>' + esc(message.attachment_name || "تصویر") + '</span></a>';
        }
        if (message.attachment_preview_url && message.attachment_kind === "pdf") {
            return '<a class="admin-chat-attachment" href="' + esc(message.attachment_preview_url) + '" target="_blank"><i class="ri-file-pdf-2-line"></i> مشاهده ' + esc(message.attachment_name || "PDF") + '</a>';
        }
        return message.attachment_url
            ? '<a class="admin-chat-attachment" href="' + esc(message.attachment_url) + '"><i class="ri-download-2-line"></i> ' + esc(message.attachment_name || "دریافت پیوست") + '</a>'
            : "";
    }

    function row(message) {
        return '<article class="admin-chat-message ' + (message.is_mine ? "is-mine" : "") + '" data-id="' + message.id + '">' +
            '<div class="admin-chat-message__meta"><strong>' + esc(message.sender) + '</strong><span>' + esc(message.created_at) + '</span></div>' +
            (message.body ? '<p>' + esc(message.body) + '</p>' : '') +
            attachmentMarkup(message) +
            '</article>';
    }

    async function load(initial) {
        if (busy) return;
        busy = true;
        try {
            var url = root.dataset.messagesUrl + (!initial && lastId ? "?after=" + lastId : "");
            var response = await fetch(url, {
                headers: {"X-Requested-With": "XMLHttpRequest"},
                credentials: "same-origin",
            });
            if (!response.ok) throw new Error("دریافت پیام‌ها ناموفق بود.");
            var payload = await response.json();
            if (initial) box.innerHTML = "";
            (payload.messages || []).forEach(function (message) {
                box.insertAdjacentHTML("beforeend", row(message));
                lastId = Math.max(lastId, Number(message.id || 0));
            });
            if (initial && !(payload.messages || []).length) {
                box.innerHTML = '<div class="text-center text-muted py-5">هنوز پیامی ثبت نشده است.</div>';
            }
            if ((payload.messages || []).length) box.scrollTop = box.scrollHeight;
        } catch (exception) {
            if (initial) box.innerHTML = '<div class="alert alert-danger m-3">' + esc(exception.message) + '</div>';
        } finally {
            busy = false;
        }
    }

    fileInput.addEventListener("change", function () {
        fileLabel.textContent = fileInput.files[0] ? fileInput.files[0].name : "";
    });

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        error.hidden = true;
        try {
            var response = await fetch(root.dataset.sendUrl, {
                method: "POST",
                body: new FormData(form),
                headers: {"X-Requested-With": "XMLHttpRequest"},
                credentials: "same-origin",
            });
            var payload = await response.json();
            if (!response.ok || !payload.ok) throw new Error(payload.error || "ارسال پاسخ ناموفق بود.");
            box.insertAdjacentHTML("beforeend", row(payload.message));
            lastId = Math.max(lastId, Number(payload.message.id || 0));
            box.scrollTop = box.scrollHeight;
            form.reset();
            fileLabel.textContent = "";
        } catch (exception) {
            error.textContent = exception.message;
            error.hidden = false;
        }
    });

    load(true);
    window.setInterval(function () { load(false); }, 5000);
})();
