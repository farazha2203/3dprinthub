from __future__ import annotations

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QGridLayout, QGroupBox, QLabel, QLineEdit, QMessageBox,
    QPushButton, QRadioButton, QVBoxLayout, QWidget,
)

from app.social_ai_design import POST_STYLES, STORY_STYLES, build_product_prompt, persist_revision


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
        self.preview = QLabel("هنوز Mock Preview ساخته نشده"); self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter); self.preview.setMinimumHeight(180)
        root.addWidget(self.preview)
        self.generate = QPushButton("🧪 تولید Mock Revision و ذخیره History")
        self.generate.clicked.connect(self.generate_mock)
        root.addWidget(self.generate)
        self.status = QLabel(""); self.status.setWordWrap(True); root.addWidget(self.status)

    def _select(self, style):
        self.selected_style = style
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
        mock_bytes = (f"MOCK-OPENROUTER-IMAGE|{self.kind}|{self.selected_style.key}|{product_id}".encode("utf-8") * 32)
        revision = persist_revision(product_id, self.kind, self.selected_style, mock_bytes, metadata)
        self.db.save_history(product_id, f"{self.kind}_ai_revision_mock", None, metadata, "Mock AI creative; no network/publish")
        self.db.save_history(product_id, f"{self.kind}_ai_revision_saved", None, revision, "Mock revision persisted; no network/publish")
        self.preview.setText(f"Mock Revision\n{self.selected_style.label}\n{self.selected_style.format}\nذخیره شد — بدون API و بدون ارسال")
        self.status.setText(f"Revision ذخیره شد: {revision['path']}\nPrompt انگلیسی ساخته شد؛ متن فارسی/URL/Mention در لایه انتشار مدیریت می‌شود.")
