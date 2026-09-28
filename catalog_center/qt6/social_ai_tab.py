from __future__ import annotations

import hashlib
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox, QGridLayout, QGroupBox, QLabel, QLineEdit, QMessageBox,
    QPushButton, QRadioButton, QVBoxLayout, QWidget, QHBoxLayout,
)

from app.social_ai_design import POST_STYLES, STORY_STYLES, build_product_prompt


class SocialAICreativeTab(QWidget):
    """Mock-only AI creative tab; no network call or provider publish."""

    def __init__(self, db, kernel, selected_ids, *, kind: str, parent=None):
        super().__init__(parent)
        self.db, self.kernel, self.selected_ids = db, kernel, selected_ids
        self.kind = str(kind)
        self.styles = STORY_STYLES if self.kind == "story" else POST_STYLES
        self.selected_style = self.styles[0]
        root = QVBoxLayout(self)
        root.addWidget(QLabel(
            f"AI {('Story' if self.kind == 'story' else 'Post')} — Mock Preview و انتخاب سبک؛ ارسال واقعی قفل است"
        ))
        self.ai_content = QCheckBox("AI Content فعال — فقط بر اساس داده معتبر Product")
        self.ai_content.setChecked(True)
        self.mention_enabled = QCheckBox("Mention فعال")
        self.mention = QLineEdit(); self.mention.setPlaceholderText("@handle دقیق")
        self.link_status = QLabel("URL و Mention داخل تصویر چاپ نمی‌شوند؛ فقط metadata انتشار.")
        root.addWidget(self.ai_content); root.addWidget(self.mention_enabled); root.addWidget(self.mention)
        root.addWidget(self.link_status)
        grid = QGridLayout(); self.radios = []
        for index, style in enumerate(self.styles):
            radio = QRadioButton(f"{index + 1}. {style.label} — {style.format}")
            radio.setToolTip(style.description)
            radio.clicked.connect(lambda _checked=False, item=style: self._select(item))
            if index == 0: radio.setChecked(True)
            box = QGroupBox(style.description); box_layout = QVBoxLayout(box); box_layout.addWidget(radio)
            grid.addWidget(box, index // 2, index % 2); self.radios.append(radio)
        root.addLayout(grid)
        self.preview = QLabel("هنوز Preview ساخته نشده")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(180)
        self.preview.setScaledContents(False)
        root.addWidget(self.preview)
        self.revision_status = QLabel("این کارت از SQLite revisionهای همین Product را می‌خواند.")
        self.revision_status.setWordWrap(True)
        root.addWidget(self.revision_status)
        self.generate = QPushButton("🧪 تولید Mock Revision و ذخیره History")
        self.generate.clicked.connect(self.generate_mock)
        root.addWidget(self.generate)
        actions = QHBoxLayout()
        self.approve = QPushButton("✅ تأیید Preview و ذخیره")
        self.approve.setEnabled(False)
        self.approve.clicked.connect(self.approve_revision)
        self.prepare_send = QPushButton(f"📤 آماده‌سازی ارسال {('Story' if self.kind == 'story' else 'Post')}")
        self.prepare_send.setEnabled(False)
        self.prepare_send.clicked.connect(self.prepare_for_send)
        actions.addWidget(self.approve); actions.addWidget(self.prepare_send)
        root.addLayout(actions)
        self.status = QLabel(""); self.status.setWordWrap(True); root.addWidget(self.status)
        self.current_revision = None
        self._load_saved_revision()

    def _select(self, style):
        self.selected_style = style
        self.current_revision = None
        ids = list(self.selected_ids())
        if ids:
            for row in self.db.social_ai_revisions(int(ids[0]), self.kind, limit=100):
                if row.get("style_key") == style.key:
                    self.current_revision = row
                    self._show_revision(row)
                    break
            else:
                self.preview.clear()
                self.revision_status.setText("برای این سبک هنوز revision ذخیره نشده است.")
                self.approve.setEnabled(False)
                self.prepare_send.setEnabled(False)
        self.status.setText(f"سبک انتخاب‌شده: {style.label} — {style.description}")

    def generate_mock(self):
        ids = list(self.selected_ids())
        if not ids:
            QMessageBox.warning(self, "AI Creative", "ابتدا یک Product انتخاب کن.")
            return
        handle = self.mention.text().strip()
        if self.mention_enabled.isChecked() and (not handle.startswith("@") or len(handle) > 31):
            QMessageBox.warning(self, "Mention", "Mention باید @handle دقیق باشد.")
            return
        product_id = int(ids[0])
        product = dict(self.db.product(product_id) or {})
        prompt = build_product_prompt(product, self.selected_style)
        metadata = {
            "mode": "mock",
            "kind": self.kind,
            "style": self.selected_style.key,
            "format": self.selected_style.format,
            "prompt": prompt,
            "ai_content": bool(self.ai_content.isChecked()),
            "mention": handle if self.mention_enabled.isChecked() else "",
            "link_mode": "provider_metadata",
            "published": False,
        }
        source_bytes = self._product_image_bytes(product)
        if not source_bytes:
            QMessageBox.warning(self, "Preview", "عکس واقعی Product برای ساخت Preview پیدا نشد.")
            return
        # This gate deliberately shows the real Product image in the same card.
        # It is a local preview, not a claim that OpenRouter has generated it.
        mock_bytes = source_bytes
        metadata["preview_kind"] = "source_image_mock_preview"
        metadata["ai_generated"] = False
        digest = hashlib.sha256(mock_bytes).hexdigest()
        revision = {
            **metadata,
            "product_id": product_id,
            "kind": self.kind,
            "style": self.selected_style.key,
            "sha256": digest,
            "bytes": len(mock_bytes),
            "storage": "sqlite_blob",
            "immutable_revision": True,
            "published": False,
        }
        row = self.db.save_social_ai_revision(
            product_id, self.kind, self.selected_style.key, digest, mock_bytes,
            revision,
        )
        self.db.save_history(product_id, f"{self.kind}_ai_revision_mock", None, metadata, "Mock AI creative; no network/publish")
        self.db.save_history(product_id, f"{self.kind}_ai_revision_saved", None, {**revision, "storage": "sqlite_blob", "db_revision_id": row.get("id") if row else None}, "Revision persisted in SQLite; no network/publish")
        self.current_revision = row
        self._show_revision(row)
        self.status.setText("Preview همین‌جا از SQLite نمایش داده شد؛ تولید واقعی AI و ارسال هنوز قفل است.")

    def _product_image_bytes(self, product):
        try:
            paths = self.kernel.images.display_local_paths(product)
        except Exception:
            paths = []
        for raw in paths:
            try:
                path = Path(str(raw))
                if path.is_file():
                    data = path.read_bytes()
                    if len(data) >= 64:
                        return data
            except OSError:
                continue
        return b""

    def _load_saved_revision(self):
        ids = list(self.selected_ids())
        if not ids:
            return
        rows = self.db.social_ai_revisions(int(ids[0]), self.kind, limit=20)
        for row in rows:
            if row.get("style_key") == self.selected_style.key:
                self.current_revision = row
                self._show_revision(row)
                return

    def _show_revision(self, row):
        raw = bytes(row.get("image_blob") or b"")
        pixmap = QPixmap()
        pixmap.loadFromData(raw)
        if pixmap.isNull():
            self.preview.setText("Revision ذخیره شده، اما bytes تصویر معتبر نیست")
        else:
            self.preview.setPixmap(pixmap.scaled(420, 520, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        approved = bool(row.get("approved"))
        selected = bool(row.get("selected_for_publish"))
        self.approve.setEnabled(not approved)
        self.prepare_send.setEnabled(approved)
        self.revision_status.setText(
            f"Revision #{row.get('id')} • ذخیره داخل SQLite • سبک: {row.get('style_key')} • "
            f"تأیید: {'بله' if approved else 'خیر'} • آماده ارسال: {'بله' if selected else 'خیر'}"
        )

    def approve_revision(self):
        if not self.current_revision:
            return
        self.db.update_social_ai_revision_state(self.current_revision["id"], approved=True)
        self.current_revision = next((r for r in self.db.social_ai_revisions(self.current_revision["product_id"], self.kind) if r["id"] == self.current_revision["id"]), self.current_revision)
        self._show_revision(self.current_revision)

    def prepare_for_send(self):
        if not self.current_revision or not self.current_revision.get("approved"):
            return
        self.db.update_social_ai_revision_state(self.current_revision["id"], selected_for_publish=True)
        self.current_revision["selected_for_publish"] = 1
        self._show_revision(self.current_revision)
        self.status.setText("برای ارسال علامت‌گذاری شد؛ اتصال این revision به provider بعد از گیت OpenRouter/ارسال فعال می‌شود.")
