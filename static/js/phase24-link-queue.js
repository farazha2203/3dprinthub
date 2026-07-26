(function () {
  "use strict";
  const card = document.querySelector("[data-link-job]");
  if (!card) return;

  const statusUrl = card.dataset.statusUrl;
  const resultUrl = card.dataset.resultUrl || window.location.href;
  const label = card.querySelector("[data-job-label]");
  const message = card.querySelector("[data-job-message]");
  const progress = card.querySelector("[data-job-progress]");
  const percent = card.querySelector("[data-job-percent]");
  const stage = card.querySelector("[data-job-stage]");
  const attempt = card.querySelector("[data-job-attempt]");
  const progressBar = card.querySelector("[role='progressbar']");
  let timer = null;
  let errors = 0;

  function schedule(delay) {
    window.clearTimeout(timer);
    timer = window.setTimeout(poll, delay);
  }

  function update(data) {
    const value = Math.max(0, Math.min(Number(data.progress_percent || 0), 100));
    if (label) label.textContent = data.job_status_label || data.job_status || data.status || "در حال پردازش";
    if (message) message.textContent = data.progress_message || "در حال پردازش لینک";
    if (progress) progress.style.width = value + "%";
    if (percent) percent.textContent = String(value);
    if (stage) stage.textContent = data.progress_stage || data.job_status || "processing";
    if (attempt) attempt.textContent = String(data.attempt_count || 0);
    if (progressBar) progressBar.setAttribute("aria-valuenow", String(value));

    if (data.is_terminal) {
      card.dataset.terminal = "1";
      if (data.job_status === "failed" || data.status === "failed") card.dataset.failed = "1";
      window.clearTimeout(timer);
      timer = window.setTimeout(function () { window.location.replace(data.result_url || resultUrl); }, 700);
      return;
    }
    const retryDelay = data.job_status === "retry" ? 4000 : 2200;
    schedule(retryDelay);
  }

  async function poll() {
    try {
      const response = await fetch(statusUrl, {
        credentials: "same-origin",
        headers: { "Accept": "application/json", "X-Requested-With": "XMLHttpRequest" },
        cache: "no-store"
      });
      if (!response.ok) throw new Error("HTTP " + response.status);
      const data = await response.json();
      errors = 0;
      update(data);
    } catch (error) {
      errors += 1;
      if (message) message.textContent = "ارتباط لحظه‌ای برقرار نشد؛ نتیجه در سرور ادامه دارد.";
      schedule(Math.min(3000 * errors, 15000));
    }
  }

  schedule(500);
})();
