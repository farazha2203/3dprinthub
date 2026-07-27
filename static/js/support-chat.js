(function () {
    "use strict";

    function csrfToken(form) {
        var input = form.querySelector('input[name="csrfmiddlewaretoken"]');
        return input ? input.value : "";
    }

    function escapeHtml(value) {
        var div = document.createElement("div");
        div.textContent = value || "";
        return div.innerHTML;
    }

    function renderMessage(message) {
        var attachment = "";
        if (message.attachment_preview_url && message.attachment_kind === "image") {
            attachment = '<a class="chat-attachment chat-attachment--image" href="' + escapeHtml(message.attachment_preview_url) + '" target="_blank"><img src="' + escapeHtml(message.attachment_preview_url) + '" alt="' + escapeHtml(message.attachment_name || "تصویر پیوست") + '"><span>' + escapeHtml(message.attachment_name || "مشاهده تصویر") + '</span></a>';
        } else if (message.attachment_preview_url && message.attachment_kind === "pdf") {
            attachment = '<a class="chat-attachment chat-attachment--pdf" href="' + escapeHtml(message.attachment_preview_url) + '" target="_blank">مشاهده PDF: ' + escapeHtml(message.attachment_name || "پیوست") + '</a>';
        } else if (message.attachment_url) {
            attachment = '<a class="chat-attachment" href="' + escapeHtml(message.attachment_url) + '">دریافت ' + escapeHtml(message.attachment_name || "پیوست") + '</a>';
        }
        return '<article class="customer-chat-message ' + (message.is_mine ? "is-mine" : "") + '" data-message-id="' + message.id + '">' +
            '<div class="customer-chat-message__meta"><strong>' + escapeHtml(message.sender) + "</strong><span>" + escapeHtml(message.created_at) + "</span></div>" +
            (message.body ? "<p>" + escapeHtml(message.body) + "</p>" : "") + attachment + "</article>";
    }

    document.querySelectorAll("[data-support-chat]").forEach(function (root) {
        var messagesUrl = root.dataset.messagesUrl;
        var sendUrl = root.dataset.sendUrl;
        var messagesBox = root.querySelector("[data-support-messages]");
        var form = root.querySelector("[data-support-form]");
        var errorBox = root.querySelector("[data-support-error]");
        var fileInput = form.querySelector('input[name="attachment"]');
        var fileName = root.querySelector("[data-support-file-name]");
        var lastId = 0;
        var loading = false;

        function showError(text) {
            errorBox.textContent = text || "خطایی رخ داد.";
            errorBox.hidden = false;
        }

        async function loadMessages(initial) {
            if (loading) return;
            loading = true;
            try {
                var url = messagesUrl + (initial || !lastId ? "" : "?after=" + lastId);
                var response = await fetch(url, {headers: {"X-Requested-With": "XMLHttpRequest"}, credentials: "same-origin"});
                if (!response.ok) return;
                var payload = await response.json();
                if (initial) messagesBox.innerHTML = "";
                payload.messages.forEach(function (message) {
                    if (!messagesBox.querySelector('[data-message-id="' + message.id + '"]')) {
                        messagesBox.insertAdjacentHTML("beforeend", renderMessage(message));
                    }
                    lastId = Math.max(lastId, Number(message.id));
                });
                if (!messagesBox.children.length) messagesBox.innerHTML = '<div class="customer-chat-loading">هنوز پیامی ثبت نشده است.</div>';
                messagesBox.scrollTop = messagesBox.scrollHeight;
            } catch (_) {
                // Polling retries automatically.
            } finally {
                loading = false;
            }
        }

        fileInput.addEventListener("change", function () {
            fileName.textContent = fileInput.files && fileInput.files[0] ? fileInput.files[0].name : "";
        });

        form.addEventListener("submit", async function (event) {
            event.preventDefault();
            errorBox.hidden = true;
            var submit = form.querySelector('button[type="submit"]');
            submit.disabled = true;
            try {
                var response = await fetch(sendUrl, {
                    method: "POST",
                    body: new FormData(form),
                    headers: {"X-CSRFToken": csrfToken(form), "X-Requested-With": "XMLHttpRequest"},
                    credentials: "same-origin",
                });
                var payload = await response.json();
                if (!response.ok || !payload.ok) {
                    showError(payload.error || "ارسال پیام انجام نشد.");
                    return;
                }
                form.reset();
                fileName.textContent = "";
                await loadMessages(false);
            } catch (_) {
                showError("ارتباط با سرور برقرار نشد. دوباره تلاش کنید.");
            } finally {
                submit.disabled = false;
            }
        });

        loadMessages(true);
        window.setInterval(function () { loadMessages(false); }, 5000);
    });
})();
