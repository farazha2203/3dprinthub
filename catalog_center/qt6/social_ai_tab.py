from __future__ import annotations

import hashlib
import json
import mimetypes
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox, QGridLayout, QGroupBox, QLabel, QLineEdit, QMessageBox,
    QPushButton, QRadioButton, QVBoxLayout, QWidget, QHBoxLayout, QSpinBox,
)

from app.social_ai_design import POST_STYLES, STORY_STYLES, brand_reference_image, build_product_prompt
from app.secure_secrets import get_provider_key
from qt6.workers import Worker
from PySide6.QtCore import QThreadPool


class SocialAICreativeTab(QWidget):
    """Generate and persist private Story/Post image revisions for operator review."""

    def __init__(self, db, kernel, selected_ids, *, kind: str, on_send=None, parent=None):
        super().__init__(parent)
        self.db, self.kernel, self.selected_ids = db, kernel, selected_ids
        self.kind = str(kind)
        self.on_send = on_send
        self.styles = STORY_STYLES if self.kind == "story" else POST_STYLES
        self.selected_style = self.styles[0]
        root = QVBoxLayout(self)
        root.addWidget(QLabel(
            f"AI {('Story' if self.kind == 'story' else 'Post')} — طراحی واقعی تصویر با Image AI؛ انتشار فقط پس از مسیر تأیید جداگانه"
        ))
        self.image_model_status = QLabel(self._image_model_status_text())
        self.image_model_status.setObjectName("Muted")
        self.image_model_status.setWordWrap(True)
        root.addWidget(self.image_model_status)
        self.ai_content = QCheckBox("ساخت چیدمان و متن تبلیغاتی فارسی از اطلاعات Product با AI")
        self.ai_content.setChecked(True)
        self.ai_content.setToolTip("عنوان و توضیح ذخیره‌شده همراه CTA فارسی به prompt تصویرسازی فرستاده می‌شوند؛ ادعای تازه ساخته نمی‌شود. URL و Mention کلیک‌پذیر فقط metadata انتشار هستند.")
        self.discount_enabled = QCheckBox("در این طرح تخفیف نمایش داده شود")
        self.discount_percent = QSpinBox(); self.discount_percent.setRange(1, 90); self.discount_percent.setSuffix("٪")
        self.discount_percent.setEnabled(False)
        self.discount_enabled.toggled.connect(self.discount_percent.setEnabled)
        self.mention_enabled = QCheckBox("Mention فعال")
        self.mention = QLineEdit(); self.mention.setPlaceholderText("@handle دقیق")
        self.link_status = QLabel("URL و Mention داخل تصویر چاپ نمی‌شوند؛ فقط metadata انتشار.")
        root.addWidget(self.ai_content)
        discount_row = QHBoxLayout(); discount_row.addWidget(self.discount_enabled); discount_row.addWidget(self.discount_percent)
        root.addLayout(discount_row)
        root.addWidget(self.mention_enabled); root.addWidget(self.mention)
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
        self.generate = QPushButton("✨ تولید واقعی با Image AI و ذخیره در SQLite")
        self.generate.setToolTip("تصویر و prompt سبک انتخابی به Image Model ذخیره‌شده فرستاده می‌شود؛ خروجی در SQLite همین Catalog ذخیره می‌شود.")
        self.generate.clicked.connect(self.generate_image)
        root.addWidget(self.generate)
        self.mock_generate = QPushButton("پیش‌نمایش آزمایشی محلی (بدون ارسال به AI)")
        self.mock_generate.setToolTip("فقط برای آزمون UI؛ عکس اصلی را بدون تغییر به‌عنوان Mock ذخیره می‌کند.")
        self.mock_generate.clicked.connect(self.generate_mock)
        root.addWidget(self.mock_generate)
        actions = QHBoxLayout()
        self.approve = QPushButton("✅ تأیید Preview و ذخیره")
        self.approve.setEnabled(False)
        self.approve.clicked.connect(self.approve_revision)
        self.prepare_send = QPushButton(f"📤 آماده‌سازی ارسال {('Story' if self.kind == 'story' else 'Post')}")
        self.prepare_send.setEnabled(False)
        self.prepare_send.clicked.connect(self.prepare_for_send)
        self.send_button = QPushButton(f"🚀 ارسال {('Story' if self.kind == 'story' else 'Post')} تأییدشده")
        self.send_button.setEnabled(False)
        self.send_button.setToolTip("پس از تأیید و آماده‌سازی، مسیر ارسال موجود را برای همین Product باز می‌کند؛ تأیید نهایی ارسال جداگانه نمایش داده می‌شود.")
        self.send_button.clicked.connect(self.send_approved_revision)
        actions.addWidget(self.approve); actions.addWidget(self.prepare_send); actions.addWidget(self.send_button)
        root.addLayout(actions)
        self.status = QLabel(""); self.status.setWordWrap(True); root.addWidget(self.status)
        self.current_revision = None
        self._generation_worker = None
        self._task_pool = QThreadPool.globalInstance()
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
                self.send_button.setEnabled(False)
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
        discount_percent = int(self.discount_percent.value()) if self.discount_enabled.isChecked() else 0
        prompt = build_product_prompt(
            product, self.selected_style, ai_content=self.ai_content.isChecked(), discount_percent=discount_percent,
        )
        metadata = {
            "mode": "mock",
            "kind": self.kind,
            "style": self.selected_style.key,
            "format": self.selected_style.format,
            "prompt": prompt,
            "ai_content": bool(self.ai_content.isChecked()),
            "discount_percent": discount_percent,
            "mention": handle if self.mention_enabled.isChecked() else "",
            "link_mode": "provider_metadata",
            "published": False,
            "image_provider": str(self.db.setting("social_image_provider", "openrouter") or "openrouter"),
            "image_model": str(self.db.setting("social_image_model", "") or ""),
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

    def generate_image(self) -> None:
        """Call the saved OpenRouter image model off-thread, then persist the returned bytes."""
        from app.social_ai_design import (
            generate_image_revision,
            generation_request_fingerprint,
            supports_aspect_ratio,
        )

        ids = list(self.selected_ids())
        if not ids:
            QMessageBox.warning(self, "AI Creative", "ابتدا یک Product انتخاب کن.")
            return
        if self._generation_worker is not None:
            QMessageBox.information(self, "AI Creative", "تولید تصویر این Product هنوز در حال اجرا است.")
            return
        model = str(self.db.setting("social_image_model", "") or "").strip()
        provider = str(self.db.setting("social_image_provider", "openrouter") or "openrouter").strip().lower()
        provider_tag = str(self.db.setting("social_image_provider_tag", "") or "").strip()
        if provider != "openrouter" or not model or not provider_tag:
            QMessageBox.warning(
                self,
                "Image AI تنظیم نشده",
                "برای همین Catalog در Settings → هوش تصویری مستقل، Image Model را کشف و ذخیره کن.",
            )
            return
        try:
            supported_parameters = json.loads(str(self.db.setting("social_image_supported_parameters_json", "{}") or "{}"))
        except (TypeError, ValueError):
            supported_parameters = {}
        if not isinstance(supported_parameters, dict) or not supports_aspect_ratio(supported_parameters, self.selected_style.format):
            QMessageBox.warning(
                self,
                "نسبت تصویر پشتیبانی نمی‌شود",
                f"Provider/model ذخیره‌شده نسبت {self.selected_style.format} این سبک را صریحاً اعلام نکرده است. در Settings، Discovery را تازه کن و endpoint سازگار انتخاب کن.",
            )
            return
        if "input_references" not in supported_parameters:
            QMessageBox.warning(self, "Reference image", "endpoint ذخیره‌شده استفاده از عکس محصول را تأیید نکرده است؛ Discovery را تازه کن.")
            return
        from app.social_ai_design import supports_reference_count
        if not supports_reference_count(supported_parameters, 2):
            QMessageBox.warning(self, "Brand reference", "endpoint انتخاب‌شده دو تصویر مرجع (محصول + لوگوی رسمی) را پشتیبانی نمی‌کند.")
            return
        api_key = str(get_provider_key("openrouter") or "").strip()
        if not api_key:
            QMessageBox.warning(self, "OpenRouter", "کلید OpenRouter در Windows Credential Store این نشست قابل‌خواندن نیست.")
            return
        handle = self.mention.text().strip()
        if self.mention_enabled.isChecked() and (not handle.startswith("@") or len(handle) > 31):
            QMessageBox.warning(self, "Mention", "Mention باید @handle دقیق باشد.")
            return

        product_id = int(ids[0])
        product = dict(self.db.product(product_id) or {})
        image = self._product_image(product)
        if not image:
            QMessageBox.warning(self, "Product image", "عکس واقعی Product برای ارسال به Image AI پیدا نشد.")
            return
        reference_bytes, reference_mime = image
        brand_bytes, brand_mime = brand_reference_image()
        if not brand_bytes:
            QMessageBox.warning(self, "3DPrintHub logo", "فایل مرجع لوگوی رسمی پیدا نشد؛ برای جلوگیری از لوگوی جعلی، تصویرسازی متوقف شد.")
            return
        ai_content = bool(self.ai_content.isChecked())
        discount_percent = int(self.discount_percent.value()) if self.discount_enabled.isChecked() else 0
        prompt = build_product_prompt(
            product, self.selected_style, ai_content=ai_content, discount_percent=discount_percent,
        )
        fingerprint = generation_request_fingerprint(
            product_id, self.kind, self.selected_style, model, prompt, reference_bytes,
            provider_tag=provider_tag,
            brand_reference_bytes=brand_bytes,
        )
        previous = self.db.social_ai_revision_by_request_fingerprint(product_id, self.kind, fingerprint)
        if previous:
            self.current_revision = previous
            self._show_revision(previous)
            self.status.setText("درخواست دقیقاً مشابه قبلاً تولید شده بود؛ همان revision بارگذاری شد و API دوباره صدا زده نشد.")
            return

        raw_cost = self.db.setting("social_image_cost_usd", "")
        cost_unit = str(self.db.setting("social_image_cost_unit", "unknown") or "unknown")
        raw_input_cost = self.db.setting("social_image_input_cost_usd", "")
        input_cost_unit = str(self.db.setting("social_image_input_cost_unit", "unknown") or "unknown")
        try:
            cost = float(raw_cost) if str(raw_cost).strip() else None
        except (TypeError, ValueError):
            cost = None
        try:
            input_cost = float(raw_input_cost) if str(raw_input_cost).strip() else None
        except (TypeError, ValueError):
            input_cost = None
        cost_label = (
            "تعرفهٔ خروجی نامشخص است"
            if cost is None else f"تعرفهٔ خروجی: ${cost:g} / {cost_unit}"
        )
        if input_cost is None:
            input_label = "تعرفهٔ ورودی تصویر نامشخص است"
        else:
            input_label = f"تعرفهٔ هر تصویر مرجع: ${input_cost:g} / {input_cost_unit} × 2 تصویر مرجع"
        estimated_cost = None
        if cost is not None and cost_unit == "image" and input_cost is not None and input_cost_unit == "image":
            estimated_cost = cost + (2 * input_cost)
        if estimated_cost is not None:
            cost_label += f" • تخمین این درخواست: حدود ${estimated_cost:g} (هزینه نهایی usage پاسخ است)"
        if cost_unit == "token" or input_cost_unit == "token":
            cost_label += " (مبلغ نهایی به تعداد توکن‌های واقعی وابسته است)"
        answer = QMessageBox.question(
            self,
            "تولید یک تصویر با Image AI",
            f"مدل: {model}\nProvider: {provider_tag} (بدون fallback)\nسبک: {self.selected_style.label}\nقالب: {self.selected_style.format}\n{cost_label}\n{input_label}\n\nفقط یک تصویر و prompt به OpenRouter فرستاده می‌شود؛ خروجی در SQLite همین Catalog ذخیره می‌شود؛ چیزی تأیید یا منتشر نمی‌شود. ادامه؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        style = self.selected_style
        kind = self.kind
        mention_enabled = bool(self.mention_enabled.isChecked())
        self.generate.setEnabled(False)
        self.mock_generate.setEnabled(False)
        self.status.setText(f"در حال ارسال تصویر Product و prompt سبک «{style.label}» به {provider}/{model}…")

        def request(progress):
            progress(5, "ارسال reference image و prompt به OpenRouter")
            result = generate_image_revision(
                api_key,
                model,
                prompt,
                reference_bytes,
                aspect_ratio=style.format,
                reference_mime_type=reference_mime,
                brand_reference_bytes=brand_bytes,
                brand_reference_mime_type=brand_mime,
                provider_tag=provider_tag,
            )
            progress(100, "تصویر از Image AI دریافت شد")
            return result

        worker = Worker(request)
        self._generation_worker = worker
        worker.signals.progress.connect(
            lambda value, message: self.status.setText(f"{value}% — {message}")
        )
        worker.signals.result.connect(
            lambda result: self._image_generation_succeeded(
                product_id, kind, style, prompt, handle, fingerprint,
                reference_bytes, brand_bytes, ai_content, discount_percent, mention_enabled, result,
            )
        )
        worker.signals.error.connect(self._image_generation_failed)
        worker.signals.finished.connect(self._image_generation_finished)
        self._task_pool.start(worker)

    def _image_generation_succeeded(
        self, product_id, kind, style, prompt, handle, fingerprint, reference_bytes,
        brand_bytes, ai_content, discount_percent, mention_enabled, result,
    ) -> None:
        image_bytes = bytes(result.get("bytes") or b"")
        if len(image_bytes) < 64:
            self._image_generation_failed("Image AI پاسخ تصویر معتبر برنگرداند؛ revision ذخیره نشد.")
            return
        digest = hashlib.sha256(image_bytes).hexdigest()
        metadata = {
            "mode": "openrouter_image_generation",
            "kind": kind,
            "style": style.key,
            "style_description": style.description,
            "format": style.format,
            "aspect_ratio": style.format,
            "prompt": prompt,
            "ai_content": ai_content,
            "discount_percent": int(discount_percent or 0),
            "mention": handle if mention_enabled else "",
            "link_mode": "provider_metadata",
            "published": False,
            "ai_generated": True,
            "image_provider": "openrouter",
            "image_model": str(result.get("model") or self.db.setting("social_image_model", "") or ""),
            "image_provider_tag": str(self.db.setting("social_image_provider_tag", "") or ""),
            "provider_usage": result.get("usage") or {},
            "provider_cost_usd": result.get("cost_usd"),
            "provider_cost_unit": str(self.db.setting("social_image_cost_unit", "unknown") or "unknown"),
            "provider_input_cost_usd_per_reference": self.db.setting("social_image_input_cost_usd", None),
            "provider_input_cost_unit": str(self.db.setting("social_image_input_cost_unit", "unknown") or "unknown"),
            "provider_reference_count": 2,
            "request_fingerprint": fingerprint,
            "source_image_sha256": hashlib.sha256(reference_bytes).hexdigest(),
            "brand_reference_sha256": hashlib.sha256(brand_bytes).hexdigest(),
            "preview_kind": "provider_generated_image",
        }
        try:
            row = self.db.save_social_ai_revision(
                product_id, kind, style.key, digest, image_bytes, metadata,
                approved=False, selected_for_publish=False, mime_type="image/png",
            )
            if not row:
                raise RuntimeError("SQLite did not return the saved image revision.")
            self.db.save_history(
                product_id,
                f"{kind}_ai_revision_provider_generated",
                None,
                {**metadata, "revision_id": row["id"], "sha256": digest, "bytes": len(image_bytes)},
                "OpenRouter image generation completed; saved in SQLite; not approved or published",
            )
        except Exception as exc:
            self._image_generation_failed(f"تصویر از AI دریافت شد ولی ذخیرهٔ SQLite ناموفق بود: {exc}")
            return
        self.current_revision = row
        self._show_revision(row)
        cost = metadata.get("provider_cost_usd")
        try:
            cost_text = "" if cost is None else f" • هزینه: ${float(cost):.4f}"
        except (TypeError, ValueError):
            cost_text = ""
        self.status.setText(f"✅ تصویر واقعی AI دریافت و در SQLite همین Product ذخیره شد{cost_text}. هنوز تأیید یا منتشر نشده است.")

    def _image_generation_failed(self, detail: str) -> None:
        self.status.setText("❌ تولید Image AI ناموفق بود؛ revision جدیدی ذخیره نشد. جزئیات در پنجرهٔ خطا است.")
        QMessageBox.warning(self, "خطای تولید تصویر AI", str(detail or "خطای نامشخص"))

    def _image_generation_finished(self) -> None:
        self._generation_worker = None
        self.generate.setEnabled(True)
        self.mock_generate.setEnabled(True)

    def _image_model_status_text(self) -> str:
        provider = str(self.db.setting("social_image_provider", "openrouter") or "openrouter")
        model = str(self.db.setting("social_image_model", "") or "").strip()
        if model:
            return f"Image AI مستقل: {provider} / {model} • این انتخاب از Text AI جداست."
        return "Image AI مستقل هنوز انتخاب نشده؛ فعلاً فقط Preview محلی/Mock فعال است."

    def _product_image_bytes(self, product):
        image = self._product_image(product)
        return image[0] if image else b""

    def _product_image(self, product=None):
        if product is None:
            ids = list(self.selected_ids())
            product = dict(self.db.product(int(ids[0])) or {}) if ids else {}
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
                        mime = mimetypes.guess_type(path.name)[0] or "image/png"
                        if not mime.startswith("image/"):
                            mime = "image/png"
                        return data, mime
            except OSError:
                continue
        return None

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
        try:
            metadata = json.loads(str(row.get("metadata_json") or "{}"))
        except (TypeError, ValueError):
            metadata = {}
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
        self.send_button.setEnabled(
            bool(self.on_send) and approved and selected
            and bool(metadata.get("ai_generated"))
        )
        source = "تصویر تولیدشده با AI" if bool(metadata.get("ai_generated")) else "Mock محلی؛ بدون درخواست AI"
        self.revision_status.setText(
            f"Revision #{row.get('id')} • SQLite • {source} • سبک: {row.get('style_key')} • "
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
        self.current_revision = next(
            (r for r in self.db.social_ai_revisions(self.current_revision["product_id"], self.kind)
             if r["id"] == self.current_revision["id"]),
            self.current_revision,
        )
        self._show_revision(self.current_revision)
        self.status.setText("Revision تأییدشده برای مسیر ارسال استاندارد همین Product آماده شد. دکمهٔ ارسال، تأیید نهایی و Gateهای فعلی را اجرا می‌کند.")

    def send_approved_revision(self):
        row = self.current_revision or {}
        if (
            not self.on_send
            or not row.get("approved")
            or not row.get("selected_for_publish")
        ):
            return
        self.on_send(self.kind, int(row["product_id"]))
