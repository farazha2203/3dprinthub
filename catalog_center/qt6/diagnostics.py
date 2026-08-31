from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QMessageBox

from app.phase49_3i24_runtime_observability import redact


def _clean(detail: Any) -> str:
    value = redact(str(detail or "")).strip()
    return value or "خطای ناشناخته"


def humanize_ai_error(detail: Any) -> str:
    value = _clean(detail)
    low = value.casefold()

    if "returned invalid json" in low or "jsondecodeerror" in low:
        return "مدل پاسخ داد، اما JSON معتبر و قابل ذخیره تولید نکرد."
    if "خروجی ai برای" in low or "فارسی معتبر نیست" in low or "متن لاتین نامرتبط" in low:
        return "مدل پاسخ داد، اما خروجی قرارداد محتوای فارسی 3DPrintHub را پاس نکرد."
    if "response_format" in low or ("structured" in low and "unsupported" in low):
        return "مدل/Endpoint به درخواست ساختاریافته Product پاسخ سازگار نداد."
    if "http 401" in low or "http 403" in low:
        return "Provider درخواست Product را رد کرد؛ دسترسی Key/Model را بررسی کن."
    if "http 429" in low or ("rate" in low and "limit" in low):
        return "Provider محدودیت نرخ/اعتبار اعمال کرده است."
    if "timeout" in low or "timed out" in low:
        return "درخواست Product به Provider در مهلت مجاز پاسخ کامل نداد."
    if "no output text" in low or "returned no text" in low:
        return "اتصال برقرار شد، اما مدل برای درخواست Product متن قابل استفاده برنگرداند."

    lines = [line.strip() for line in value.splitlines() if line.strip()]
    for line in reversed(lines):
        if not line.startswith(("File ", "Traceback", "^")):
            return line[:600]
    return value[-600:]


def show_diagnostic_error(
    parent,
    title: str,
    detail: Any,
    *,
    context: dict[str, Any] | None = None,
) -> int:
    clean = _clean(detail)
    summary = humanize_ai_error(clean)

    context = dict(context or {})
    context_lines = [
        f"{key}: {value}"
        for key, value in context.items()
        if value not in (None, "")
    ]
    details = "\n".join(
        [
            *(["Context:"] + context_lines + [""] if context_lines else []),
            clean,
        ]
    )

    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Critical)
    box.setWindowTitle(str(title or "3DPrintHub"))
    box.setText(summary)
    box.setInformativeText(
        "جزئیات کامل خطا از دکمه «Show Details / جزئیات» قابل مشاهده و کپی است."
    )
    box.setDetailedText(details)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    return int(box.exec())
