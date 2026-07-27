(function () {
  "use strict";
  if (window.__phase26RealtimeLoaded) return;
  window.__phase26RealtimeLoaded = true;

  function socketUrl(path) {
    return (window.location.protocol === "https:" ? "wss://" : "ws://") + window.location.host + path;
  }

  function setNotificationCount(value) {
    const count = Math.max(Number(value || 0), 0);
    document.querySelectorAll("[data-notification-count]").forEach(function (node) {
      node.textContent = count ? String(count) : "";
      node.hidden = !count;
    });
  }

  function toast(payload) {
    if (!payload || !payload.title) return;
    const item = document.createElement("a");
    item.href = payload.url || "/store/account/notifications/";
    item.dir = "rtl";
    item.style.cssText = "position:fixed;left:22px;bottom:22px;z-index:99999;max-width:360px;background:#0f2745;color:#fff;border:1px solid rgba(184,137,37,.65);border-radius:18px;padding:15px 17px;box-shadow:0 18px 50px rgba(15,39,69,.28);text-decoration:none;font-family:IRANSans,Tahoma,sans-serif";
    const title = document.createElement("strong");
    title.style.cssText = "display:block;margin-bottom:6px";
    title.textContent = String(payload.title);
    const message = document.createElement("span");
    message.style.cssText = "font-size:12px;line-height:1.9;opacity:.9";
    message.textContent = String(payload.message || "");
    item.appendChild(title);
    item.appendChild(message);
    document.body.appendChild(item);
    window.setTimeout(function () { item.remove(); }, 9000);
  }

  const notificationRoot = document.querySelector("[data-realtime-notification-root]");
  if (notificationRoot) {
    let retry = 1000;
    function connectNotifications() {
      const ws = new WebSocket(socketUrl(notificationRoot.dataset.wsPath || "/ws/customer/notifications/"));
      ws.onopen = function () { retry = 1000; };
      ws.onmessage = function (event) {
        try {
          const message = JSON.parse(event.data || "{}");
          const payload = message.payload || {};
          if (payload.unread_count !== undefined) setNotificationCount(payload.unread_count);
          if (message.event === "notification.created") toast(payload);
        } catch (_) {}
      };
      ws.onclose = function () {
        window.setTimeout(connectNotifications, retry);
        retry = Math.min(retry * 2, 30000);
      };
    }
    connectNotifications();
  }

  const card = document.querySelector("[data-link-job][data-ws-path]");
  if (card) {
    let retry = 1000;
    let terminalHandled = false;
    function applyJob(data) {
      const value = Math.max(0, Math.min(Number(data.progress_percent || 0), 100));
      const label = card.querySelector("[data-job-label]");
      const message = card.querySelector("[data-job-message]");
      const progress = card.querySelector("[data-job-progress]");
      const percent = card.querySelector("[data-job-percent]");
      const stage = card.querySelector("[data-job-stage]");
      const attempt = card.querySelector("[data-job-attempt]");
      const bar = card.querySelector("[role='progressbar']");
      if (label) label.textContent = data.job_status_label || data.job_status || data.status || "در حال پردازش";
      if (message) message.textContent = data.progress_message || "در حال پردازش لینک";
      if (progress) progress.style.width = value + "%";
      if (percent) percent.textContent = String(value);
      if (stage) stage.textContent = data.progress_stage || data.job_status || "processing";
      if (attempt) attempt.textContent = String(data.attempt_count || 0);
      if (bar) bar.setAttribute("aria-valuenow", String(value));
      if (data.is_terminal && !terminalHandled) {
        terminalHandled = true;
        window.setTimeout(function () { window.location.replace(data.result_url || card.dataset.resultUrl || window.location.href); }, 650);
      }
    }
    function connectJob() {
      const ws = new WebSocket(socketUrl(card.dataset.wsPath));
      ws.onopen = function () { retry = 1000; card.dataset.realtimeConnected = "1"; };
      ws.onmessage = function (event) {
        try {
          const message = JSON.parse(event.data || "{}");
          if (message.event === "link.job") applyJob(message.payload || {});
        } catch (_) {}
      };
      ws.onclose = function () {
        card.dataset.realtimeConnected = "0";
        if (!terminalHandled) {
          window.setTimeout(connectJob, retry);
          retry = Math.min(retry * 2, 30000);
        }
      };
    }
    connectJob();
  }
})();
