from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)


class ManualProductDialog(QDialog):
    """Operator-owned first-class Product creation without marketplace identity."""

    def __init__(
        self,
        categories: list[dict[str, Any]],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("محصول دستی / تولید داخلی")
        self.resize(690, 520)
        self._image_paths: list[str] = []
        root = QVBoxLayout(self)
        intro = QLabel(
            "این مسیر برای محصولی است که منبع Marketplace ندارد. "
            "عنوان، توضیحات و تصاویر شما factual هستند؛ وزن/زمان/ابعاد/"
            "متریال/مجوز به‌صورت خودکار حدس زده نمی‌شوند."
        )
        intro.setWordWrap(True)
        root.addWidget(intro)

        form = QGridLayout()
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("نام واقعی محصول")
        self.notes_edit = QPlainTextEdit()
        self.notes_edit.setPlaceholderText(
            "توضیح اپراتور درباره کاربرد، ظاهر و نکات واقعی محصول"
        )
        self.category_combo = QComboBox()
        for item in categories or []:
            slug = str(item.get("slug") or "").strip()
            name = str(item.get("name") or slug).strip()
            if slug:
                self.category_combo.addItem(name, slug)
        self.reference_edit = QLineEdit()
        self.reference_edit.setPlaceholderText(
            "اختیاری: https://...  فقط لینک مرجع است، نه هویت Product"
        )

        form.addWidget(QLabel("عنوان محصول *"), 0, 0)
        form.addWidget(self.title_edit, 0, 1)
        form.addWidget(QLabel("دسته"), 1, 0)
        form.addWidget(self.category_combo, 1, 1)
        form.addWidget(QLabel("لینک مرجع"), 2, 0)
        form.addWidget(self.reference_edit, 2, 1)
        form.addWidget(QLabel("توضیحات / یادداشت"), 3, 0)
        form.addWidget(self.notes_edit, 3, 1)
        root.addLayout(form)

        media_row = QGridLayout()
        self.images_label = QLabel("هیچ تصویری انتخاب نشده")
        self.images_label.setWordWrap(True)
        choose_images = QPushButton("انتخاب تصاویر…")
        choose_images.clicked.connect(self._choose_images)
        media_row.addWidget(QLabel("تصاویر اولیه"), 0, 0)
        media_row.addWidget(self.images_label, 0, 1)
        media_row.addWidget(choose_images, 0, 2)
        root.addLayout(media_row)

        hint = QLabel(
            "پس از ساخت، همین Product در ویزارد ۷مرحله‌ای باز می‌شود و "
            "Profile/Filament/SEO/انتشار سایت/Post/Story از همان مسیر بالغ ادامه دارد."
        )
        hint.setWordWrap(True)
        root.addWidget(hint)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(
            "ساخت و باز کردن در ویزارد"
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _choose_images(self) -> None:
        paths, _selected_filter = QFileDialog.getOpenFileNames(
            self,
            "انتخاب تصاویر محصول دستی",
            "",
            "Images (*.webp *.jpg *.jpeg *.png *.avif *.gif)",
        )
        if not paths:
            return
        self._image_paths = [str(path) for path in paths]
        self.images_label.setText(
            f"{len(self._image_paths)} تصویر انتخاب شد"
        )

    def values(self) -> dict[str, Any]:
        return {
            "title": self.title_edit.text().strip(),
            "notes": self.notes_edit.toPlainText().strip(),
            "category_slug": str(
                self.category_combo.currentData() or "external-other"
            ).strip(),
            "reference_url": self.reference_edit.text().strip(),
            "image_paths": list(self._image_paths),
        }

    def accept(self) -> None:
        values = self.values()
        if not values["title"]:
            QMessageBox.warning(
                self,
                "محصول دستی",
                "عنوان محصول الزامی است.",
            )
            return
        reference = str(values["reference_url"] or "").strip()
        if reference:
            parsed = urlsplit(reference)
            if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
                QMessageBox.warning(
                    self,
                    "محصول دستی",
                    "لینک مرجع باید یک آدرس کامل http/https باشد.",
                )
                return
        super().accept()
