(function () {
  "use strict";
  const root = document.querySelector("[data-phase26-admin-live]");
  if (!root) return;
  const snapshotUrl = root.dataset.snapshotUrl;
  let wsOpen = false;
  let timer = null;

  function socketUrl(path) {
    return (window.location.protocol === "https:" ? "wss://" : "ws://") + window.location.host + path;
  }

  function apply(data) {
    Object.keys(data || {}).forEach(function (key) {
      document.querySelectorAll('[data-metric="' + key + '"]').forEach(function (node) {
        node.textContent = String(data[key] === undefined || data[key] === null ? "0" : data[key]);
      });
    });
    const queue = document.querySelector("[data-queue-state]");
    if (queue) {
      queue.textContent = data.queue_paused ? "متوقف" : "فعال";
      queue.classList.toggle("pause", !!data.queue_paused);
    }
    const updated = document.querySelector("[data-live-updated]");
    if (updated) updated.textContent = new Date().toLocaleTimeString("fa-IR");
    root.classList.add("p26-flash");
    window.setTimeout(function () { root.classList.remove("p26-flash"); }, 500);
  }

  async function poll() {
    if (wsOpen || !snapshotUrl) return schedule(12000);
    try {
      const response = await fetch(snapshotUrl, {credentials: "same-origin", cache: "no-store", headers: {"Accept": "application/json"}});
      if (response.ok) apply(await response.json());
    } catch (_) {}
    schedule(10000);
  }

  function schedule(delay) {
    window.clearTimeout(timer);
    timer = window.setTimeout(poll, delay);
  }

  function connect() {
    const ws = new WebSocket(socketUrl(root.dataset.wsPath || "/ws/admin/link-operations/"));
    ws.onopen = function () { wsOpen = true; };
    ws.onmessage = function (event) {
      try {
        const message = JSON.parse(event.data || "{}");
        if (message.event === "operations.snapshot") apply(message.payload || {});
      } catch (_) {}
    };
    ws.onclose = function () { wsOpen = false; schedule(1000); window.setTimeout(connect, 5000); };
  }

  connect();
  schedule(1000);
})();
