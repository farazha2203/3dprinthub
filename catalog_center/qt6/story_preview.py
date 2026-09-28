from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox, QGridLayout, QGroupBox, QLabel, QLineEdit, QMessageBox,
    QPushButton, QRadioButton, QSpinBox, QVBoxLayout, QWidget,
)

from app.instagram_story_asset import prepare_product_story_asset


class StoryPreviewTab(QWidget):
    """Local-only Story workbench. It never publishes or mutates Catalog data."""

    def __init__(self, db, kernel, selected_ids, parent=None):
        super().__init__(parent)
        self.db, self.kernel, self.selected_ids = db, kernel, selected_ids
        self._approved = False
        root = QVBoxLayout(self)
        root.addWidget(QLabel("چهار قالب Story عمودی ۱۰۸۰×۱۹۲۰ — Preview محلی، سپس تأیید اپراتور و Sticker دستی"))
        self.photo_check = QCheckBox("استفاده از عکس واقعی محصول و هماهنگ‌سازی رنگ با همان عکس")
        self.photo_check.setChecked(True)
        root.addWidget(self.photo_check)
        controls = QGridLayout()
        self.discount = QSpinBox(); self.discount.setRange(0, 100); self.discount.setSuffix("٪")
        self.discount_ok = QCheckBox("درصد تخفیف توسط اپراتور تأیید شده")
        self.mention = QLineEdit(); self.mention.setPlaceholderText("@handle اختیاری؛ فقط منشن واردشده اپراتور")
        controls.addWidget(QLabel("تخفیف دقیق"), 0, 0); controls.addWidget(self.discount, 0, 1); controls.addWidget(self.discount_ok, 0, 2)
        controls.addWidget(QLabel("Mention"), 1, 0); controls.addWidget(self.mention, 1, 1, 1, 2)
        root.addLayout(controls)
        self.cards = []
        grid = QGridLayout()
        names = ("1 — Classic Gold/Navy Hero", "2 — Technical Blueprint", "3 — Editorial Classic", "4 — Premium Conversion")
        for idx, name in enumerate(names, 1):
            box = QGroupBox(name); layout = QVBoxLayout(box)
            image = QLabel("هنوز Preview ساخته نشده"); image.setAlignment(Qt.AlignmentFlag.AlignCenter); image.setMinimumSize(300, 533)
            image.setStyleSheet("background:#101923;border:1px solid #c99a3a;")
            choose = QRadioButton("انتخاب این قالب")
            choose.clicked.connect(lambda _=False, i=idx: self._choose(i))
            layout.addWidget(image); layout.addWidget(choose)
            grid.addWidget(box, (idx - 1) // 2, (idx - 1) % 2); self.cards.append((image, choose))
        root.addLayout(grid)
        self.status = QLabel("محصول انتخاب‌شده از گالری/جدول را انتخاب کن."); self.status.setWordWrap(True)
        root.addWidget(self.status)
        self.link_status = QLabel("Link Sticker: هنوز تأیید نشده — PNG به‌تنهایی کلیک‌پذیر نیست.")
        self.link_status.setWordWrap(True)
        root.addWidget(self.link_status)
        self.generate = QPushButton("🖼 تولید Preview چهار قالب")
        self.approve = QPushButton("✅ تأیید Preview و آماده‌سازی انتشار دستی")
        self.approve.setEnabled(False)
        self.generate.clicked.connect(self.generate_previews); self.approve.clicked.connect(self.approve_preview)
        root.addWidget(self.generate); root.addWidget(self.approve)

    def _choose(self, template_id: int):
        self.selected_template = template_id; self._approved = False; self.approve.setEnabled(True)
        self.status.setText(f"قالب {template_id} انتخاب شد؛ هنوز تأیید نهایی اپراتور ثبت نشده است.")

    def generate_previews(self):
        ids = list(self.selected_ids())
        if not ids:
            QMessageBox.warning(self, "Story", "ابتدا یک Product را در گالری یا جدول انتخاب کن."); return
        if self.discount.value() and not self.discount_ok.isChecked():
            QMessageBox.warning(self, "Story", "تخفیف تا زمان تأیید صریح اپراتور وارد Preview نمی‌شود."); return
        handle = self.mention.text().strip()
        if handle and (not handle.startswith("@") or len(handle) > 31 or not handle[1:].replace("_", "").replace(".", "").isalnum()):
            QMessageBox.warning(self, "Story", "Mention باید به شکل @handle معتبر باشد."); return
        product_id = ids[0]
        post_receipts = {
            "instagram_published",
            "instagram_submitted",
        }
        receipts = self.db.sync_receipts(int(product_id), limit=100)
        if not any(str(item["status"] or "") in post_receipts for item in receipts):
            QMessageBox.warning(
                self,
                "Story",
                "این Product هنوز Post اینستاگرام تأییدشده ندارد؛ ابتدا Post را ارسال و receipt آن را ثبت کن.",
            )
            return
        payload = self.kernel.instagram.preview(product_id)
        # InstagramCore.preview already returns the canonical payload directly;
        # older UI code incorrectly expected an extra wrapper key and therefore
        # reported a missing Product URL for valid published Products.
        payload = payload.get("canonical_site_payload") or payload
        if not str(payload.get("product_url") or "").startswith("https://"):
            QMessageBox.warning(self, "Story", "URL canonical عمومی Product آماده نیست."); return
        if not self.photo_check.isChecked():
            QMessageBox.warning(self, "Story", "در این نسخه Preview فقط با عکس واقعی و قابل ردیابی محصول مجاز است."); return
        try:
            settings = self.kernel.connection.settings(require_bridge=False)
            generated_paths = []
            for template_id, (image, _button) in enumerate(self.cards, 1):
                _button.setChecked(template_id == getattr(self, "selected_template", 1))
                result = prepare_product_story_asset(
                    self.db, product_id, settings, payload,
                    publish_to_site=False, template_id=template_id,
                    discount_percent=(self.discount.value() if self.discount_ok.isChecked() else 0),
                )
                pixmap = QPixmap(result["local_path"])
                image.setPixmap(pixmap.scaled(image.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                generated_paths.append(result["local_path"])
            self.selected_template = 1; self._approved = False; self.approve.setEnabled(True)
            self.db.save_history(
                int(product_id),
                "story_preview_generated",
                None,
                {
                    "template_ids": [1, 2, 3, 4],
                    "discount_percent": int(self.discount.value() if self.discount_ok.isChecked() else 0),
                    "product_url": str(payload["product_url"]),
                    "local_paths": generated_paths,
                },
                "Four-template Story Preview generated; operator approval and Link Sticker confirmation still required.",
            )
            self.status.setText(
                f"۴ Preview محلی برای Product #{product_id} آماده شد.\n"
                f"URL دقیق محصول: {payload['product_url']}\n"
                f"فایل قالب ۱: {generated_paths[0]}\n"
                "ارسال واقعی انجام نشده است."
            )
            self.link_status.setText(
                "Link Sticker: دستی لازم است — همین URL را در Instagram Link Sticker وارد و سپس تأیید اپراتور را ثبت کنید."
            )
        except Exception as exc:
            QMessageBox.critical(self, "Story Preview", str(exc))

    def approve_preview(self):
        self._approved = True; self.approve.setEnabled(False)
        self.status.setText("Preview تأیید شد؛ مرحله بعد فقط آماده‌سازی دستی Link Sticker/Mention است. انتشار خودکار همچنان قفل است.")
