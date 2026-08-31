from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .workers import TaskPool, Worker


class SettingsPage(QWidget):
    """Qt parity for mature AI Provider Hub + Site connection settings."""

    def __init__(self, db, parent=None, *, kernel=None) -> None:
        super().__init__(parent)
        if kernel is None:
            raise RuntimeError("SettingsPage requires ApplicationKernel")
        self.db = db
        self.kernel = kernel
        self.pool = TaskPool()
        self._worker: Worker | None = None
        self._model_info: list[dict[str, Any]] = []

        root = QVBoxLayout(self)
        title = QLabel("تنظیمات")
        title.setStyleSheet("font-size: 23px; font-weight: 700;")
        subtitle = QLabel(
            "Provider/Model فعال، کلیدهای امن Windows و اتصال FTP/Bridge. "
            "Secretها داخل SQLite یا Git ذخیره نمی‌شوند."
        )
        subtitle.setObjectName("Muted")
        subtitle.setWordWrap(True)
        root.addWidget(title)
        root.addWidget(subtitle)

        host = QWidget()
        host_layout = QVBoxLayout(host)
        host_layout.addWidget(self._build_ai_box())
        host_layout.addWidget(self._build_connection_box())
        host_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(host)
        root.addWidget(scroll, 1)

        self.refresh()

    def _build_ai_box(self) -> QGroupBox:
        box = QGroupBox("هوش مصنوعی / Provider Hub")
        layout = QVBoxLayout(box)
        form = QFormLayout()

        self.provider = QComboBox()
        for item in self.kernel.providers.providers():
            self.provider.addItem(item["label"], item["code"])
        self.provider.currentIndexChanged.connect(self._provider_changed)

        self.model = QComboBox()
        self.model.setEditable(True)
        self.model.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.model.setMinimumContentsLength(44)
        self.model.completer().setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.model.completer().setFilterMode(Qt.MatchFlag.MatchContains)

        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setPlaceholderText("برای جایگزینی/تست کلید جدید وارد کن؛ در SQLite ذخیره نمی‌شود")

        self.key_source = QLabel("")
        self.key_source.setObjectName("Muted")
        self.ai_active = QLabel("")
        self.ai_active.setStyleSheet("font-weight: 700;")
        self.ai_status = QLabel("آماده")
        self.ai_status.setObjectName("Muted")

        form.addRow("Provider", self.provider)
        form.addRow("Model قابل جستجو", self.model)
        form.addRow("API Key جدید", self.api_key)
        form.addRow("منبع کلید امن", self.key_source)
        form.addRow("Provider/Model فعال", self.ai_active)
        layout.addLayout(form)

        actions = QHBoxLayout()
        self.load_models_btn = QPushButton("دریافت مدل‌ها")
        self.test_ai_btn = QPushButton("🧪 تست اتصال AI")
        self.save_ai_btn = QPushButton("ذخیره امن + فعال‌کردن Provider/Model")
        self.save_ai_btn.setProperty("primary", True)
        self.clear_ai_key_btn = QPushButton("حذف کلید امن Provider")
        self.load_models_btn.clicked.connect(self._load_models)
        self.test_ai_btn.clicked.connect(self._test_ai)
        self.save_ai_btn.clicked.connect(self._save_ai)
        self.clear_ai_key_btn.clicked.connect(self._clear_ai_key)
        actions.addWidget(self.load_models_btn)
        actions.addWidget(self.test_ai_btn)
        actions.addWidget(self.save_ai_btn)
        actions.addWidget(self.clear_ai_key_btn)
        actions.addStretch(1)
        layout.addLayout(actions)
        layout.addWidget(self.ai_status)
        return box

    def _build_connection_box(self) -> QGroupBox:
        box = QGroupBox("اتصال سایت")
        layout = QVBoxLayout(box)
        form = QFormLayout()

        self.ftp_host = QLineEdit()
        self.ftp_port = QSpinBox()
        self.ftp_port.setRange(1, 65535)
        self.ftp_user = QLineEdit()
        self.ftp_password = QLineEdit()
        self.ftp_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.ftp_password.setPlaceholderText("خالی = استفاده از Credential Store")
        self.remote_root = QLineEdit()
        self.site_url = QLineEdit()
        self.bridge_token = QLineEdit()
        self.bridge_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.bridge_token.setPlaceholderText("خالی = استفاده از Credential Store")
        self.connection_secret_source = QLabel("")
        self.connection_secret_source.setObjectName("Muted")
        self.connection_status = QLabel("آماده")
        self.connection_status.setObjectName("Muted")

        form.addRow("FTP Host", self.ftp_host)
        form.addRow("FTP Port", self.ftp_port)
        form.addRow("FTP Username", self.ftp_user)
        form.addRow("FTP Password", self.ftp_password)
        form.addRow("Remote Root", self.remote_root)
        form.addRow("Site URL", self.site_url)
        form.addRow("Bridge Token", self.bridge_token)
        form.addRow("منبع Secretها", self.connection_secret_source)
        layout.addLayout(form)

        actions = QHBoxLayout()
        self.save_connection_btn = QPushButton("ذخیره امن اتصال")
        self.save_connection_btn.setProperty("primary", True)
        self.test_ftp_btn = QPushButton("تست FTP")
        self.test_bridge_btn = QPushButton("تست Bridge")
        self.save_connection_btn.clicked.connect(self._save_connection)
        self.test_ftp_btn.clicked.connect(lambda: self._test_connection("ftp"))
        self.test_bridge_btn.clicked.connect(lambda: self._test_connection("bridge"))
        actions.addWidget(self.save_connection_btn)
        actions.addWidget(self.test_ftp_btn)
        actions.addWidget(self.test_bridge_btn)
        actions.addStretch(1)
        layout.addLayout(actions)
        layout.addWidget(self.connection_status)
        return box

    def refresh(self) -> None:
        active = self.kernel.providers.active()
        provider = active.get("provider") or ""
        if provider:
            index = self.provider.findData(provider)
            if index >= 0:
                self.provider.setCurrentIndex(index)
        self.model.setEditText(active.get("model") or "")
        self._refresh_provider_status()

        values = self.kernel.connection.values()
        self.ftp_host.setText(str(values.get("ftp_host") or ""))
        self.ftp_port.setValue(int(values.get("ftp_port") or 21))
        self.ftp_user.setText(str(values.get("ftp_user") or ""))
        self.remote_root.setText(str(values.get("ftp_remote_root") or ""))
        self.site_url.setText(str(values.get("site_url") or ""))
        self.connection_secret_source.setText(
            f"FTP: {values.get('ftp_password_source') or '—'}   •   "
            f"Bridge: {values.get('bridge_token_source') or '—'}"
        )

    def _provider_changed(self) -> None:
        code = str(self.provider.currentData() or "")
        saved = str(
            self.db.setting(f"ai_model_{code}", "")
            or (
                self.db.setting("ai_model", "")
                if str(self.db.setting("ai_provider", "") or "") == code
                else ""
            )
            or ""
        )
        self.model.clear()
        self.model.setEditText(saved)
        self._refresh_provider_status()

    def _refresh_provider_status(self) -> None:
        code = str(self.provider.currentData() or "")
        self.key_source.setText(self.kernel.providers.key_source(code) if code else "—")
        active = self.kernel.providers.active()
        self.ai_active.setText(
            f"{active.get('provider') or '—'} / {active.get('model') or '—'}"
        )

    def _start_worker(self, fn, *, status_label: QLabel, start_text: str, done) -> None:
        if self._worker is not None:
            QMessageBox.information(self, "3DPrintHub", "یک تست/درخواست تنظیمات در حال اجرا است.")
            return
        status_label.setText(start_text)

        def job(progress):
            progress(10, start_text)
            result = fn()
            progress(100, "تمام")
            return result

        worker = Worker(job)
        self._worker = worker
        worker.signals.progress.connect(
            lambda value, message: status_label.setText(f"{value}% — {message}")
        )
        worker.signals.result.connect(done)
        worker.signals.error.connect(
            lambda detail: self._worker_error(status_label, detail)
        )
        worker.signals.finished.connect(self._worker_finished)
        self.pool.start(worker)

    def _worker_error(self, label: QLabel, detail: str) -> None:
        label.setText("❌ خطا")
        message = str(detail or "").splitlines()[-1] if detail else "خطای ناشناخته"
        QMessageBox.warning(self, "3DPrintHub", message)

    def _worker_finished(self) -> None:
        self._worker = None

    def _load_models(self) -> None:
        provider = str(self.provider.currentData() or "")
        key = self.api_key.text().strip()

        def done(result) -> None:
            self._model_info = list(result or [])
            current = self.model.currentText().strip()
            self.model.clear()
            for item in self._model_info:
                model_id = str(item.get("id") or item.get("name") or "").strip()
                if not model_id:
                    continue
                name = str(item.get("name") or "").strip()
                label = model_id if not name or name == model_id else f"{name} — {model_id}"
                self.model.addItem(label, model_id)
            if current:
                match = next(
                    (
                        index
                        for index in range(self.model.count())
                        if str(self.model.itemData(index) or "") == current
                        or str(self.model.itemText(index)).endswith(f"— {current}")
                    ),
                    -1,
                )
                if match >= 0:
                    self.model.setCurrentIndex(match)
                else:
                    self.model.setEditText(current)
            self.ai_status.setText(f"✅ {self.model.count()} مدل دریافت شد")

        self._start_worker(
            lambda: self.kernel.providers.models(provider, key_override=key),
            status_label=self.ai_status,
            start_text="دریافت مدل‌ها…",
            done=done,
        )

    def _selected_model_id(self) -> str:
        data = self.model.currentData()
        if data:
            return str(data).strip()
        text = self.model.currentText().strip()
        if " — " in text:
            return text.rsplit(" — ", 1)[-1].strip()
        return text.replace("models/", "", 1) if text.startswith("models/") else text

    def _test_ai(self) -> None:
        provider = str(self.provider.currentData() or "")
        model = self._selected_model_id()
        key = self.api_key.text().strip()

        def done(result) -> None:
            self.ai_status.setText(
                f"✅ اتصال {provider} موفق — "
                f"{result.get('models_count', result.get('connected', 'OK'))}"
            )

        self._start_worker(
            lambda: self.kernel.providers.test(
                provider,
                model,
                key_override=key,
            ),
            status_label=self.ai_status,
            start_text="تست Provider…",
            done=done,
        )

    def _save_ai(self) -> None:
        provider = str(self.provider.currentData() or "")
        model = self._selected_model_id()
        key = self.api_key.text().strip()
        try:
            if key:
                self.kernel.providers.save_key(provider, key)
            active = self.kernel.providers.save_default(provider, model)
        except Exception as exc:
            QMessageBox.warning(self, "هوش مصنوعی", str(exc))
            return
        self.api_key.clear()
        self._refresh_provider_status()
        self.ai_status.setText(
            f"✅ Provider پیش‌فرض: {active['provider']} / {active['model']}"
        )

    def _clear_ai_key(self) -> None:
        provider = str(self.provider.currentData() or "")
        if QMessageBox.question(
            self,
            "حذف کلید",
            f"کلید امن {provider} از Credential Store حذف شود؟",
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            self.kernel.providers.delete_key(provider)
        except Exception as exc:
            QMessageBox.warning(self, "حذف کلید", str(exc))
            return
        self._refresh_provider_status()

    def _connection_values(self) -> dict[str, Any]:
        return {
            "ftp_host": self.ftp_host.text().strip(),
            "ftp_port": self.ftp_port.value(),
            "ftp_user": self.ftp_user.text().strip(),
            "ftp_remote_root": self.remote_root.text().strip(),
            "site_url": self.site_url.text().strip(),
        }

    def _save_connection(self) -> None:
        try:
            self.kernel.connection.save(
                self._connection_values(),
                ftp_password=self.ftp_password.text(),
                bridge_token=self.bridge_token.text(),
            )
        except Exception as exc:
            QMessageBox.warning(self, "اتصال سایت", str(exc))
            return
        self.ftp_password.clear()
        self.bridge_token.clear()
        self.refresh()
        self.connection_status.setText("✅ تنظیمات اتصال ذخیره شد")

    def _test_connection(self, kind: str) -> None:
        try:
            self.kernel.connection.save(
                self._connection_values(),
                ftp_password=self.ftp_password.text(),
                bridge_token=self.bridge_token.text(),
            )
            self.ftp_password.clear()
            self.bridge_token.clear()
        except Exception as exc:
            QMessageBox.warning(self, "اتصال سایت", str(exc))
            return

        def done(result) -> None:
            if kind == "ftp":
                self.connection_status.setText(
                    f"✅ FTP متصل — {result.get('remote_path') or 'OK'}"
                )
            else:
                self.connection_status.setText(
                    f"✅ Bridge متصل — {result.get('version') or result.get('status') or 'OK'}"
                )
            self.refresh()

        self._start_worker(
            self.kernel.connection.test_ftp
            if kind == "ftp"
            else self.kernel.connection.test_bridge,
            status_label=self.connection_status,
            start_text="تست اتصال…",
            done=done,
        )
