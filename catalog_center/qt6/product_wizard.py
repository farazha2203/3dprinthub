from __future__ import annotations

import json
from typing import Any

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QAbstractSpinBox,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.ai_model_catalog import format_cost_quote
from app.phase49_3h_image_limits import HARD_MAX_IMAGE_LIMIT
from app.phase49_3i36_stage_finalization import STAGE_ORDER
from .diagnostics import show_diagnostic_error
from .image_gallery import ImageSeoDialog, ProductImageGrid
from .parity_dialogs import ProfileEditorDialog
from .widgets import StageStepper, WizardFooter
from .workers import TaskPool, Worker


STAGE_NAMES = [
    "عنوان و دسته‌بندی",
    "Filament، قیمت و Profile",
    "تصاویر",
    "محتوا و SEO",
    "منبع، مجوز و مشخصات",
    "اسلایدر صفحه اول",
    "آماده‌سازی و انتشار",
]

STAGE_CODES = tuple(STAGE_ORDER)


def _frame(title: str, subtitle: str = "") -> tuple[QFrame, QVBoxLayout]:
    page = QFrame()
    page.setObjectName("Card")
    layout = QVBoxLayout(page)
    label = QLabel(title)
    label.setStyleSheet("font-size: 18px; font-weight: 700;")
    layout.addWidget(label)
    if subtitle:
        hint = QLabel(subtitle)
        hint.setObjectName("Muted")
        hint.setWordWrap(True)
        layout.addWidget(hint)
    return page, layout


def _scroll(widget: QWidget) -> QScrollArea:
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setWidget(widget)
    return scroll


def _json_list(value: Any) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def _json_dict(value: Any) -> dict:
    if isinstance(value, dict):
        return dict(value)
    try:
        parsed = json.loads(value or "{}")
    except Exception:
        return {}
    return dict(parsed) if isinstance(parsed, dict) else {}


def _lines(value: Any) -> list[str]:
    if isinstance(value, list):
        raw = value
    else:
        raw = str(value or "").replace(",", "\n").splitlines()
    output: list[str] = []
    seen: set[str] = set()
    for item in raw:
        text = str(item or "").strip()
        if not text or text.casefold() in seen:
            continue
        seen.add(text.casefold())
        output.append(text)
    return output


def _human_bytes(value: int) -> str:
    size = max(0, int(value or 0))
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.2f} MB"


class ProductWizardPage(QWidget):
    def __init__(self, db, parent=None, *, kernel=None) -> None:
        super().__init__(parent)
        if kernel is None:
            raise RuntimeError("ProductWizardPage requires ApplicationKernel")
        self.db = db
        self.kernel = kernel
        self.product_id: int | None = None
        self.task_pool = TaskPool()
        self._ai_worker: Worker | None = None
        self._ai_quote_worker: Worker | None = None
        self._pending_ai_request: dict[str, Any] | None = None
        self._pending_ai_quote: dict[str, Any] | None = None
        self._image_worker: Worker | None = None

        root = QVBoxLayout(self)

        heading = QVBoxLayout()
        title = QLabel("ویزارد حرفه‌ای محصول")
        title.setStyleSheet("font-size: 23px; font-weight: 700;")
        subtitle = QLabel(
            "همان هفت مرحله بالغ Catalog Center روی Qt: "
            "❌ ناقص، ◌ کامل ولی منتظر تأیید، ✅ ثبت نهایی."
        )
        subtitle.setObjectName("Muted")
        subtitle.setWordWrap(True)
        heading.addWidget(title)
        heading.addWidget(subtitle)
        root.addLayout(heading)

        self.product_label = QLabel("هیچ محصولی انتخاب نشده است.")
        self.product_label.setStyleSheet("font-size: 16px; font-weight: 700;")
        self.product_meta = QLabel("")
        self.product_meta.setObjectName("Muted")
        self.product_meta.setWordWrap(True)
        root.addWidget(self.product_label)
        root.addWidget(self.product_meta)

        ai_box = QFrame()
        ai_box.setObjectName("Card")
        ai_layout = QHBoxLayout(ai_box)
        ai_layout.addWidget(QLabel("منبع هوش مصنوعی"))
        self.ai_source = QComboBox()
        for item in self.kernel.providers.source_modes():
            self.ai_source.addItem(item["label"], item["code"])
        self.ai_current = QPushButton("AI همین مرحله")
        self.ai_current.setProperty("primary", True)
        self.ai_all = QPushButton("AI همه مراحل محتوایی")
        self.ai_status = QLabel("آماده")
        self.ai_status.setObjectName("Muted")
        self.ai_cost_hint = QLabel(
            "قبل از ارسال، Provider/Model و هزینه تقریبی نمایش داده و تأیید می‌شود."
        )
        self.ai_cost_hint.setObjectName("Muted")
        self.ai_cost_hint.setWordWrap(True)
        ai_layout.addWidget(self.ai_source)
        ai_layout.addWidget(self.ai_current)
        ai_layout.addWidget(self.ai_all)
        ai_layout.addWidget(self.ai_status, 1)
        ai_layout.addWidget(self.ai_cost_hint, 2)
        self.ai_current.clicked.connect(lambda: self._run_ai(current_only=True))
        self.ai_all.clicked.connect(lambda: self._run_ai(current_only=False))
        root.addWidget(ai_box)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        self.stepper = StageStepper(STAGE_NAMES)
        self.stepper.setMinimumWidth(340)
        splitter.addWidget(self.stepper)

        workspace = QWidget()
        workspace_layout = QVBoxLayout(workspace)
        self.stack = QStackedWidget()
        workspace_layout.addWidget(self.stack, 1)

        self._build_stage1()
        self._build_stage2()
        self._build_stage3()
        self._build_stage4()
        self._build_stage5()
        self._build_stage6()
        self._build_stage7()

        self.image_grid.sliderChanged.connect(self._sync_slider_from_image_grid)
        self._image_selection_save_timer = QTimer(self)
        self._image_selection_save_timer.setSingleShot(True)
        self._image_selection_save_timer.setInterval(120)
        self._image_selection_save_timer.timeout.connect(
            self._persist_image_selection
        )
        self.image_grid.selectionChanged.connect(
            self._queue_image_selection_save
        )
        self.image_slider_enabled.toggled.connect(
            lambda checked: self.slider_enabled.setChecked(bool(checked))
        )
        self.slider_enabled.toggled.connect(
            lambda checked: self.image_slider_enabled.setChecked(bool(checked))
        )

        action_row = QFrame()
        action_row.setObjectName("Card")
        action_layout = QHBoxLayout(action_row)
        self.stage_state_label = QLabel("مرحله انتخاب نشده")
        self.stage_state_label.setObjectName("Muted")
        self.save_stage_btn = QPushButton("ذخیره تغییرات مرحله")
        self.save_stage_btn.setProperty("primary", True)
        self.finalize_stage_btn = QPushButton("✅ ثبت و تأیید مرحله")
        self.finalize_stage_btn.setProperty("success", True)
        self.unlock_stage_btn = QPushButton("اصلاح مرحله")
        action_layout.addWidget(self.stage_state_label, 1)
        action_layout.addWidget(self.save_stage_btn)
        action_layout.addWidget(self.finalize_stage_btn)
        action_layout.addWidget(self.unlock_stage_btn)
        workspace_layout.addWidget(action_row)

        self.footer = WizardFooter()
        workspace_layout.addWidget(self.footer)

        splitter.addWidget(workspace)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter, 1)

        self.stepper.stageChanged.connect(self._set_stage)
        self.footer.previousClicked.connect(lambda: self._move(-1))
        self.footer.nextClicked.connect(lambda: self._move(1))
        self.save_stage_btn.clicked.connect(lambda: self._save_current(notify=True))
        self.finalize_stage_btn.clicked.connect(self._finalize_current)
        self.unlock_stage_btn.clicked.connect(self._unlock_current)
        self._set_stage(0)

    # ------------------------------------------------------------------
    # Stage builders
    # ------------------------------------------------------------------
    def _build_stage1(self) -> None:
        page, layout = _frame(
            "۱. عنوان و دسته‌بندی",
            "عنوان اصلی منبع برای کنترل هویت نمایش داده می‌شود؛ عنوان فارسی و دسته سایت قابل ویرایش‌اند.",
        )
        form = QFormLayout()
        self.source_title = QLineEdit()
        self.source_title.setReadOnly(True)
        self.title_fa = QLineEdit()
        self.category = QComboBox()
        self.category.setEditable(False)
        form.addRow("عنوان اصلی / انگلیسی منبع", self.source_title)
        form.addRow("عنوان فارسی", self.title_fa)
        form.addRow("دسته‌بندی سایت", self.category)
        layout.addLayout(form)

        category_actions = QHBoxLayout()
        self.add_category_name = QLineEdit()
        self.add_category_name.setPlaceholderText("نام فارسی دسته جدید")
        self.add_category_slug = QLineEdit()
        self.add_category_slug.setPlaceholderText("slug-english")
        add_category = QPushButton("افزودن دسته")
        add_category.clicked.connect(self._add_category)
        category_actions.addWidget(self.add_category_name)
        category_actions.addWidget(self.add_category_slug)
        category_actions.addWidget(add_category)
        layout.addLayout(category_actions)
        layout.addStretch(1)
        self.stack.addWidget(page)

    def _build_stage2(self) -> None:
        page, layout = _frame(
            "۲. Filament، قیمت و Profile",
            "هر Profile یک سایز است و می‌تواند چند وزن/زمان چاپ × چند Filament/رنگ/قیمت داشته باشد.",
        )
        basics = QGroupBox("اطلاعات تولید محصول")
        basic_form = QGridLayout(basics)
        self.product_type = QComboBox()
        self.product_type.addItem("محصول آماده", "ready_product")
        self.product_type.addItem("سفارش سفارشی", "custom_order")
        self.product_type.addItem("نمونه کار", "portfolio")
        self.dimensions = QLineEdit()
        self.dimensions.setPlaceholderText("مثال: 20 × 15 × 8 cm")
        self.use_case_class = QLineEdit()
        basic_form.addWidget(QLabel("نوع محصول"), 0, 0)
        basic_form.addWidget(self.product_type, 0, 1)
        basic_form.addWidget(QLabel("ابعاد کلی"), 0, 2)
        basic_form.addWidget(self.dimensions, 0, 3)
        basic_form.addWidget(QLabel("کاربرد / کلاس"), 1, 0)
        basic_form.addWidget(self.use_case_class, 1, 1, 1, 3)
        layout.addWidget(basics)

        self.profile_table = QTableWidget(0, 7)
        self.profile_table.setHorizontalHeaderLabels(
            (
                "نام پروفایل",
                "سایز",
                "ابعاد واقعی",
                "وزن/زمان‌ها",
                "Filamentها",
                "حالت‌های تولید",
                "قیمت",
            )
        )
        self.profile_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.profile_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.profile_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.profile_table, 1)

        profile_actions = QHBoxLayout()
        for label, callback, primary in (
            ("پروفایل جدید", self._new_profile, True),
            ("ویرایش پروفایل", self._edit_profile, False),
            ("کپی پروفایل", self._clone_profile, False),
            ("حذف پروفایل", self._delete_profile, False),
        ):
            button = QPushButton(label)
            if primary:
                button.setProperty("primary", True)
            button.clicked.connect(callback)
            profile_actions.addWidget(button)
        profile_actions.addStretch(1)
        layout.addLayout(profile_actions)
        self.stack.addWidget(page)

    def _build_stage3(self) -> None:
        page, layout = _frame(
            "۳. تصاویر محصول",
            "گالری تصویری چهارستونه مانند نسخه بالغ قبلی؛ انتخاب/حذف گروهی، تصویر اصلی، "
            "تصویر اسلایدر، اندازه/حجم، SEO تکی/گروهی و بازیابی تصاویر در همین مرحله.",
        )

        control = QFrame()
        control.setObjectName("Card")
        actions = QHBoxLayout(control)

        select_all = QPushButton("انتخاب همه")
        clear_all = QPushButton("لغو انتخاب همه")
        edit_seo = QPushButton("ویرایش SEO انتخاب‌شده‌ها")
        apply_seo = QPushButton("اعمال SEO فارسی محصول")
        delete_selected = QPushButton("حذف انتخاب‌شده‌ها")
        screenshot = QPushButton("دریافت اسکرین‌شات صفحه محصول")
        recover = QPushButton("بازیابی تصاویر از صفحه محصول")
        recover.setProperty("primary", True)

        self.image_recover_limit = QSpinBox()
        self.image_recover_limit.setRange(1, HARD_MAX_IMAGE_LIMIT)
        self.image_recover_limit.setValue(5)
        self.image_recover_limit.setSuffix(" عکس")

        select_all.clicked.connect(
            lambda: self.image_grid.set_all_selected(True)
        )
        clear_all.clicked.connect(
            lambda: self.image_grid.set_all_selected(False)
        )
        edit_seo.clicked.connect(self._edit_selected_image_seo)
        apply_seo.clicked.connect(self._apply_product_image_seo)
        delete_selected.clicked.connect(self._delete_selected_images)
        screenshot.clicked.connect(self._capture_product_screenshot)
        recover.clicked.connect(self._recover_product_images)

        for widget in (
            select_all,
            clear_all,
            edit_seo,
            apply_seo,
            delete_selected,
            screenshot,
        ):
            actions.addWidget(widget)
        actions.addStretch(1)
        actions.addWidget(QLabel("تعداد عکس"))
        actions.addWidget(self.image_recover_limit)
        actions.addWidget(recover)
        layout.addWidget(control)

        slider_box = QFrame()
        slider_box.setObjectName("Card")
        slider_layout = QHBoxLayout(slider_box)
        self.image_slider_enabled = QCheckBox(
            "این محصول در اسلایدر صفحه اول نمایش داده شود"
        )
        slider_hint = QLabel(
            "دایره «اسلایدر» روی کارت، عکس اسلایدر را تعیین می‌کند؛ "
            "دایره «اصلی» عکس اصلی Product است."
        )
        slider_hint.setObjectName("Muted")
        slider_hint.setWordWrap(True)
        slider_layout.addWidget(self.image_slider_enabled)
        slider_layout.addWidget(slider_hint, 1)
        layout.addWidget(slider_box)

        self.image_task_status = QLabel("آماده")
        self.image_task_status.setObjectName("Muted")
        layout.addWidget(self.image_task_status)

        self.image_grid = ProductImageGrid(columns=4)
        self.image_grid.deleteRequested.connect(self._delete_single_image)
        self.image_grid.seoRequested.connect(
            lambda url: self._edit_image_seo([url])
        )
        layout.addWidget(self.image_grid, 1)

        self.stack.addWidget(page)

    def _build_stage4(self) -> None:
        page, layout = _frame(
            "۴. محتوا و SEO",
            "اطلاعات اصلی/انگلیسی منبع جدا از SEO فارسی فروشگاه ایران نمایش داده می‌شود؛ "
            "دیتای منبع فقط مرجع است و خروجی فارسی قابل ویرایش.",
        )

        tabs = QTabWidget()

        source_host = QWidget()
        source_form = QFormLayout(source_host)
        self.content_source_title = QLineEdit()
        self.content_source_title.setReadOnly(True)
        self.source_category = QLineEdit()
        self.source_category.setReadOnly(True)
        self.source_tags = QPlainTextEdit()
        self.source_tags.setReadOnly(True)
        self.source_tags.setMaximumHeight(110)
        self.source_description = QPlainTextEdit()
        self.source_description.setReadOnly(True)
        self.source_description.setMinimumHeight(220)
        self.source_content_specs = QPlainTextEdit()
        self.source_content_specs.setReadOnly(True)
        self.source_content_specs.setMinimumHeight(150)

        source_form.addRow("عنوان اصلی / انگلیسی", self.content_source_title)
        source_form.addRow("دسته اصلی منبع", self.source_category)
        source_form.addRow("Tag / Keyword اصلی منبع", self.source_tags)
        source_form.addRow("توضیحات اصلی منبع", self.source_description)
        source_form.addRow("مشخصات خام منبع", self.source_content_specs)
        tabs.addTab(_scroll(source_host), "اصل محصول / Source")

        fa_host = QWidget()
        form = QFormLayout(fa_host)
        self.short_description_fa = QTextEdit()
        self.short_description_fa.setMaximumHeight(110)
        self.description_fa = QTextEdit()
        self.description_fa.setMinimumHeight(210)
        self.use_description = QTextEdit()
        self.use_description.setMaximumHeight(110)
        self.seo_title_fa = QLineEdit()
        self.seo_description_fa = QTextEdit()
        self.seo_description_fa.setMaximumHeight(110)
        self.categories_fa = QPlainTextEdit()
        self.categories_fa.setMaximumHeight(90)
        self.tags_fa = QPlainTextEdit()
        self.tags_fa.setMaximumHeight(90)
        self.hashtags_fa = QPlainTextEdit()
        self.hashtags_fa.setMaximumHeight(90)
        self.keywords_fa = QPlainTextEdit()
        self.keywords_fa.setMaximumHeight(90)
        self.sales_bullets = QPlainTextEdit()
        self.sales_bullets.setMaximumHeight(120)
        self.social_caption = QTextEdit()
        self.social_caption.setMaximumHeight(120)

        form.addRow("توضیح کوتاه فارسی", self.short_description_fa)
        form.addRow("توضیح کامل فارسی", self.description_fa)
        form.addRow("کاربرد فارسی", self.use_description)
        form.addRow("SEO Title فارسی / ایران", self.seo_title_fa)
        form.addRow("SEO Description فارسی / ایران", self.seo_description_fa)
        form.addRow("دسته‌های فارسی - هر خط یکی", self.categories_fa)
        form.addRow("Tagهای فارسی - هر خط یکی", self.tags_fa)
        form.addRow("Hashtagها - هر خط یکی", self.hashtags_fa)
        form.addRow("Keywordهای هدف ایران - هر خط یکی", self.keywords_fa)
        form.addRow("Bullet فروش - هر خط یکی", self.sales_bullets)
        form.addRow("Social Caption فارسی", self.social_caption)
        tabs.addTab(_scroll(fa_host), "SEO و محتوای فارسی / ایران")

        layout.addWidget(tabs, 1)
        self.stack.addWidget(page)

    def _build_stage5(self) -> None:
        page, layout = _frame(
            "۵. منبع، مجوز و مشخصات",
            "هویت منبع، صاحب/طراح، مجوز تجاری و مشخصات فنی قبل از انتشار بازبینی می‌شوند.",
        )
        host = QWidget()
        form = QFormLayout(host)

        self.source_url = QLineEdit()
        self.source_url.setReadOnly(True)
        self.spec_source_title = QLineEdit()
        self.spec_source_title.setReadOnly(True)
        self.author_name = QLineEdit()
        self.license_name = QLineEdit()
        self.license_url = QLineEdit()
        self.commercial_status = QComboBox()
        self.commercial_status.addItem("نیازمند بررسی", "review")
        self.commercial_status.addItem("مجاز", "allowed")
        self.commercial_status.addItem("مالکیت خودمان", "owned")
        self.commercial_status.addItem("Public Domain", "public_domain")
        self.commercial_status.addItem("غیرمجاز", "forbidden")
        self.technical_summary = QTextEdit()
        self.technical_summary.setMinimumHeight(130)
        self.specs_fa = QPlainTextEdit()
        self.specs_fa.setMinimumHeight(130)
        self.specs_fa.setPlaceholderText('{"ویژگی": "مقدار"}')
        self.technical_features = QPlainTextEdit()
        self.technical_features.setMinimumHeight(150)
        self.technical_features.setPlaceholderText('{"ویژگی": "مقدار"}')
        self.source_specs = QPlainTextEdit()
        self.source_specs.setReadOnly(True)
        self.source_specs.setMinimumHeight(120)

        form.addRow("URL منبع", self.source_url)
        form.addRow("عنوان اصلی منبع", self.spec_source_title)
        form.addRow("طراح / Author", self.author_name)
        form.addRow("نام مجوز", self.license_name)
        form.addRow("URL مجوز", self.license_url)
        form.addRow("وضعیت استفاده تجاری", self.commercial_status)
        form.addRow("خلاصه فنی فارسی", self.technical_summary)
        form.addRow("مشخصات فارسی JSON", self.specs_fa)
        form.addRow("ویژگی‌های فنی JSON", self.technical_features)
        form.addRow("مشخصات خام منبع", self.source_specs)
        layout.addWidget(_scroll(host), 1)
        self.stack.addWidget(page)

    def _build_stage6(self) -> None:
        page, layout = _frame(
            "۶. اسلایدر صفحه اول",
            "تمام تنظیمات Product-local اسلایدر: متن، تصویر، افکت، زمان‌بندی و نحوه نمایش.",
        )
        host = QWidget()
        form = QFormLayout(host)

        self.slider_enabled = QCheckBox("نمایش این محصول در اسلایدر")
        self.slider_title = QLineEdit()
        self.slider_description = QTextEdit()
        self.slider_description.setMaximumHeight(100)
        self.slider_alt = QLineEdit()
        self.slider_focus = QLineEdit()
        self.slider_image = QComboBox()
        self.slider_image.setEditable(True)
        self.slider_button = QLineEdit()
        self.slider_transition = QComboBox()
        self.slider_transition.addItems(["fade", "slide", "zoom", "none"])
        self.slider_transition_ms = QSpinBox()
        self.slider_transition_ms.setRange(0, 60_000)
        self.slider_transition_ms.setSingleStep(100)
        self.slider_transition_ms.setSuffix(" ms")
        self.slider_display_ms = QSpinBox()
        self.slider_display_ms.setRange(500, 300_000)
        self.slider_display_ms.setSingleStep(500)
        self.slider_display_ms.setSuffix(" ms")
        self.slider_sort = QSpinBox()
        self.slider_sort.setRange(-100_000, 100_000)
        self.slider_sort.setSingleStep(1)

        self.slider_presentation = QComboBox()
        self.slider_presentation.addItems(["product_fit", "cover", "contain"])
        self.slider_object_fit = QComboBox()
        self.slider_object_fit.addItems(["contain", "cover", "fill"])
        self.slider_focal = QComboBox()
        self.slider_focal.addItems(["center", "top", "bottom", "left", "right"])
        self.slider_scale = QDoubleSpinBox()
        self.slider_scale.setRange(10, 300)
        self.slider_scale.setDecimals(1)
        self.slider_x = QDoubleSpinBox()
        self.slider_x.setRange(0, 100)
        self.slider_y = QDoubleSpinBox()
        self.slider_y.setRange(0, 100)
        self.slider_bg_mode = QComboBox()
        self.slider_bg_mode.addItems(["none", "color", "blur"])
        self.slider_bg_color = QLineEdit()
        self.slider_blur = QSpinBox()
        self.slider_blur.setRange(0, 100)
        self.slider_desktop_w = QDoubleSpinBox()
        self.slider_desktop_w.setRange(10, 100)
        self.slider_desktop_h = QDoubleSpinBox()
        self.slider_desktop_h.setRange(10, 100)
        self.slider_mobile_w = QDoubleSpinBox()
        self.slider_mobile_w.setRange(10, 100)
        self.slider_mobile_h = QDoubleSpinBox()
        self.slider_mobile_h.setRange(10, 100)

        for control in (
            self.slider_transition_ms,
            self.slider_display_ms,
            self.slider_sort,
            self.slider_scale,
            self.slider_x,
            self.slider_y,
            self.slider_blur,
            self.slider_desktop_w,
            self.slider_desktop_h,
            self.slider_mobile_w,
            self.slider_mobile_h,
        ):
            control.setButtonSymbols(
                QAbstractSpinBox.ButtonSymbols.NoButtons
            )
        for control in (
            self.slider_scale,
            self.slider_x,
            self.slider_y,
            self.slider_desktop_w,
            self.slider_desktop_h,
            self.slider_mobile_w,
            self.slider_mobile_h,
        ):
            control.setSuffix(" %")
            control.setSingleStep(5)
        self.slider_blur.setSuffix(" px")
        self.slider_blur.setSingleStep(2)

        form.addRow(self.slider_enabled)
        form.addRow("عنوان اسلایدر", self.slider_title)
        form.addRow("توضیح اسلایدر", self.slider_description)
        form.addRow("Alt", self.slider_alt)
        form.addRow("Focus Keyword", self.slider_focus)
        form.addRow("تصویر", self.slider_image)
        form.addRow("متن دکمه", self.slider_button)
        form.addRow("افکت", self.slider_transition)
        form.addRow("مدت Transition ms", self.slider_transition_ms)
        form.addRow("مدت نمایش ms", self.slider_display_ms)
        form.addRow("ترتیب", self.slider_sort)
        form.addRow("Presentation Mode", self.slider_presentation)
        form.addRow("Object Fit", self.slider_object_fit)
        form.addRow("Focal Position", self.slider_focal)
        form.addRow("Scale %", self.slider_scale)
        form.addRow("Position X %", self.slider_x)
        form.addRow("Position Y %", self.slider_y)
        form.addRow("Background Mode", self.slider_bg_mode)
        form.addRow("Background Color", self.slider_bg_color)
        form.addRow("Blur px", self.slider_blur)
        form.addRow("Desktop Max Width %", self.slider_desktop_w)
        form.addRow("Desktop Max Height %", self.slider_desktop_h)
        form.addRow("Mobile Max Width %", self.slider_mobile_w)
        form.addRow("Mobile Max Height %", self.slider_mobile_h)
        layout.addWidget(_scroll(host), 1)
        self.stack.addWidget(page)

    def _build_stage7(self) -> None:
        page, layout = _frame(
            "۷. آماده‌سازی و انتشار",
            "انتخاب مقصد انتشار + وضعیت واقعی همه مراحل قبل از ورود به صف Site.",
        )
        self.approved_for_sale = QCheckBox("تأیید برای فروش")
        self.publish_product = QCheckBox("انتشار به عنوان Product")
        self.publish_portfolio = QCheckBox("انتشار به عنوان Portfolio / نمونه کار")
        layout.addWidget(self.approved_for_sale)
        layout.addWidget(self.publish_product)
        layout.addWidget(self.publish_portfolio)

        self.readiness_text = QPlainTextEdit()
        self.readiness_text.setReadOnly(True)
        layout.addWidget(self.readiness_text, 1)
        self.stack.addWidget(page)

    # ------------------------------------------------------------------
    # Product loading and stage state
    # ------------------------------------------------------------------
    def load_product(self, product_id: int) -> None:
        row = self.kernel.products.get(int(product_id))
        if row is None:
            self.product_id = None
            self.product_label.setText("محصول پیدا نشد.")
            return

        self.product_id = int(product_id)
        title = row.get("title_fa") or row.get("source_title") or "بدون عنوان"
        self.product_label.setText(f"#{product_id} — {title}")
        self.product_meta.setText(
            f"منبع: {row.get('source_name') or row.get('source_code') or '—'}"
            f"  •  وضعیت: {row.get('workflow_status') or '—'}"
            f"  •  Server ID: {row.get('server_id') or '—'}"
        )

        self._load_stage1(row)
        self._load_stage2(row)
        self._load_stage3(row)
        self._load_stage4(row)
        self._load_stage5(row)
        self._load_stage6(row)
        self._load_stage7(row)
        self._refresh_stage_statuses()
        self._set_stage(self.stepper.current_stage())

    def refresh(self) -> None:
        if self.product_id is not None:
            self.load_product(self.product_id)

    def _load_stage1(self, row: dict[str, Any]) -> None:
        self.source_title.setText(str(row.get("source_title") or ""))
        self.title_fa.setText(str(row.get("title_fa") or ""))
        categories = self.kernel.categories.list()
        current = str(row.get("local_category_slug") or "")
        self.category.blockSignals(True)
        self.category.clear()
        for item in categories:
            self.category.addItem(item["name"], item["slug"])
        index = self.category.findData(current)
        if index < 0 and current:
            self.category.addItem(current, current)
            index = self.category.count() - 1
        self.category.setCurrentIndex(max(0, index))
        self.category.blockSignals(False)

    def _load_stage2(self, row: dict[str, Any]) -> None:
        index = self.product_type.findData(str(row.get("product_type") or "ready_product"))
        self.product_type.setCurrentIndex(index if index >= 0 else 0)
        self.dimensions.setText(str(row.get("dimensions") or ""))
        self.use_case_class.setText(str(row.get("use_case_class") or ""))
        self._reload_profiles()

    def _load_stage3(self, row: dict[str, Any]) -> None:
        items = self.kernel.images.local_items(int(row["id"]))
        self.image_grid.set_items(items)
        self.image_slider_enabled.blockSignals(True)
        self.image_slider_enabled.setChecked(
            bool(int(row.get("homepage_slider_enabled") or 0))
        )
        self.image_slider_enabled.blockSignals(False)
        missing = sum(1 for item in items if not item.get("downloaded"))
        self.image_task_status.setText(
            f"{len(items)} تصویر • {missing} فایل محلی مفقود/دریافت‌نشده"
        )

    def _load_stage4(self, row: dict[str, Any]) -> None:
        self.content_source_title.setText(str(row.get("source_title") or ""))
        self.source_category.setText(str(row.get("source_category") or ""))
        self.source_tags.setPlainText(
            "\n".join(str(item) for item in _json_list(row.get("tags_json")))
        )
        self.source_description.setPlainText(
            str(row.get("source_description") or "")
        )
        self.source_content_specs.setPlainText(
            json.dumps(
                _json_dict(row.get("source_specs_json")),
                ensure_ascii=False,
                indent=2,
            )
        )
        self.short_description_fa.setPlainText(str(row.get("short_description_fa") or ""))
        self.description_fa.setPlainText(str(row.get("description_fa") or ""))
        self.use_description.setPlainText(str(row.get("use_description") or ""))
        self.seo_title_fa.setText(str(row.get("seo_title_fa") or ""))
        self.seo_description_fa.setPlainText(str(row.get("seo_description_fa") or ""))
        self.categories_fa.setPlainText("\n".join(str(item) for item in _json_list(row.get("categories_fa_json"))))
        self.tags_fa.setPlainText("\n".join(str(item) for item in _json_list(row.get("tags_fa_json"))))
        self.hashtags_fa.setPlainText("\n".join(str(item) for item in _json_list(row.get("hashtags_fa_json"))))
        self.keywords_fa.setPlainText("\n".join(str(item) for item in _json_list(row.get("keywords_json"))))
        self.sales_bullets.setPlainText("\n".join(str(item) for item in _json_list(row.get("sales_bullets_json"))))
        self.social_caption.setPlainText(str(row.get("social_caption_fa") or ""))

    def _load_stage5(self, row: dict[str, Any]) -> None:
        self.source_url.setText(str(row.get("source_url") or ""))
        self.spec_source_title.setText(str(row.get("source_title") or ""))
        self.author_name.setText(str(row.get("author_name") or ""))
        self.license_name.setText(str(row.get("license_name") or ""))
        self.license_url.setText(str(row.get("license_url") or ""))
        status = str(row.get("commercial_status") or "review")
        index = self.commercial_status.findData(status)
        self.commercial_status.setCurrentIndex(index if index >= 0 else 0)
        self.technical_summary.setPlainText(str(row.get("technical_summary_fa") or ""))
        self.specs_fa.setPlainText(
            json.dumps(_json_dict(row.get("specs_fa_json")), ensure_ascii=False, indent=2)
        )
        self.technical_features.setPlainText(
            json.dumps(_json_dict(row.get("technical_features_json")), ensure_ascii=False, indent=2)
        )
        self.source_specs.setPlainText(
            json.dumps(_json_dict(row.get("source_specs_json")), ensure_ascii=False, indent=2)
        )

    def _load_stage6(self, row: dict[str, Any]) -> None:
        self.slider_enabled.setChecked(bool(int(row.get("homepage_slider_enabled") or 0)))
        self.slider_title.setText(str(row.get("homepage_slider_title_fa") or ""))
        self.slider_description.setPlainText(str(row.get("homepage_slider_description_fa") or ""))
        self.slider_alt.setText(str(row.get("homepage_slider_alt_text") or ""))
        self.slider_focus.setText(str(row.get("homepage_slider_focus_keyword") or ""))

        image_urls = [
            str(item.get("url") or "")
            for item in self.kernel.images.local_items(int(row["id"]))
            if item.get("url")
        ]
        current_image = str(row.get("homepage_slider_image_url") or "")
        if hasattr(self, "image_slider_enabled"):
            self.image_slider_enabled.blockSignals(True)
            self.image_slider_enabled.setChecked(
                bool(int(row.get("homepage_slider_enabled") or 0))
            )
            self.image_slider_enabled.blockSignals(False)
        self.slider_image.clear()
        self.slider_image.addItems(image_urls)
        self.slider_image.setEditText(current_image)

        self.slider_button.setText(str(row.get("homepage_slider_button_text") or "مشاهده محصول"))
        self._set_combo_text(self.slider_transition, str(row.get("homepage_slider_transition_effect") or "fade"))
        self.slider_transition_ms.setValue(int(row.get("homepage_slider_transition_duration_ms") or 700))
        self.slider_display_ms.setValue(int(row.get("homepage_slider_display_duration_ms") or 6000))
        self.slider_sort.setValue(int(row.get("homepage_slider_sort_order") or 0))
        self._set_combo_text(self.slider_presentation, str(row.get("homepage_slider_presentation_mode") or "product_fit"))
        self._set_combo_text(self.slider_object_fit, str(row.get("homepage_slider_object_fit") or "contain"))
        self._set_combo_text(self.slider_focal, str(row.get("homepage_slider_focal_position") or "center"))
        self.slider_scale.setValue(float(row.get("homepage_slider_image_scale_percent") or 100))
        self.slider_x.setValue(float(row.get("homepage_slider_position_x_percent") or 50))
        self.slider_y.setValue(float(row.get("homepage_slider_position_y_percent") or 50))
        self._set_combo_text(self.slider_bg_mode, str(row.get("homepage_slider_background_mode") or "none"))
        self.slider_bg_color.setText(str(row.get("homepage_slider_background_color") or ""))
        self.slider_blur.setValue(int(row.get("homepage_slider_background_blur_px") or 0))
        self.slider_desktop_w.setValue(float(row.get("homepage_slider_desktop_max_width_percent") or 100))
        self.slider_desktop_h.setValue(float(row.get("homepage_slider_desktop_max_height_percent") or 100))
        self.slider_mobile_w.setValue(float(row.get("homepage_slider_mobile_max_width_percent") or 100))
        self.slider_mobile_h.setValue(float(row.get("homepage_slider_mobile_max_height_percent") or 100))

    def _load_stage7(self, row: dict[str, Any]) -> None:
        self.approved_for_sale.setChecked(bool(int(row.get("approved_for_sale") or 0)))
        self.publish_product.setChecked(bool(int(row.get("publish_as_product") or 0)))
        self.publish_portfolio.setChecked(bool(int(row.get("publish_as_portfolio") or 0)))
        self._refresh_readiness_text()

    @staticmethod
    def _set_combo_text(combo: QComboBox, value: str) -> None:
        index = combo.findText(value)
        if index < 0 and value:
            combo.addItem(value)
            index = combo.count() - 1
        combo.setCurrentIndex(max(0, index))

    # ------------------------------------------------------------------
    # Stage save/finalize/unlock
    # ------------------------------------------------------------------
    def _save_current(self, *, notify: bool = False) -> bool:
        if self.product_id is None:
            if notify:
                QMessageBox.warning(self, "3DPrintHub", "ابتدا یک محصول را انتخاب کن.")
            return False
        code = STAGE_CODES[self.stack.currentIndex()]
        handlers = {
            "quick": self._save_stage1,
            "commerce": self._save_stage2,
            "images": self._save_stage3,
            "content": self._save_stage4,
            "specs": self._save_stage5,
            "slider": self._save_stage6,
            "publish": self._save_stage7,
        }
        try:
            handlers[code]()
        except Exception as exc:
            if notify:
                QMessageBox.warning(self, "ذخیره مرحله", str(exc))
            return False
        self._refresh_stage_statuses()
        if notify:
            QMessageBox.information(self, "3DPrintHub", "تغییرات این مرحله ذخیره شد.")
        return True

    def _save_stage1(self) -> None:
        title = self.title_fa.text().strip()
        category = str(self.category.currentData() or "").strip()
        if not title:
            raise ValueError("عنوان فارسی خالی است.")
        if not category:
            raise ValueError("دسته سایت انتخاب نشده است.")
        self.kernel.stages.update(
            self.product_id,
            "quick",
            {"title_fa": title, "local_category_slug": category},
        )

    def _save_stage2(self) -> None:
        self.kernel.stages.update(
            self.product_id,
            "commerce",
            {
                "product_type": str(self.product_type.currentData() or "ready_product"),
                "dimensions": self.dimensions.text().strip(),
                "use_case_class": self.use_case_class.text().strip(),
            },
        )

    def _save_stage3(self) -> None:
        selected = self.image_grid.selected_urls()
        primary = self.image_grid.primary_url()
        if primary and primary not in selected:
            selected.insert(0, primary)

        alts: list[str] = []
        for url in selected:
            item = self.image_grid.item_for_url(url) or {}
            alts.append(str(item.get("alt_text") or "").strip())

        self.kernel.stages.update(
            self.product_id,
            "images",
            {
                "selected_images_json": json.dumps(
                    selected,
                    ensure_ascii=False,
                ),
                "primary_image_url": primary,
                "image_alt_texts_json": json.dumps(
                    alts,
                    ensure_ascii=False,
                ),
            },
        )

        # Slider ownership stays in the Slider stage even though the visual
        # choice is conveniently exposed on image cards.
        self.kernel.stages.update(
            self.product_id,
            "slider",
            {
                "homepage_slider_enabled": (
                    1 if self.image_slider_enabled.isChecked() else 0
                ),
                "homepage_slider_image_url": self.image_grid.slider_url(),
            },
            event_type="qt_image_slider_choice",
        )

    def _save_stage4(self) -> None:
        self.kernel.stages.update(
            self.product_id,
            "content",
            {
                "short_description_fa": self.short_description_fa.toPlainText().strip(),
                "description_fa": self.description_fa.toPlainText().strip(),
                "use_description": self.use_description.toPlainText().strip(),
                "seo_title_fa": self.seo_title_fa.text().strip(),
                "seo_description_fa": self.seo_description_fa.toPlainText().strip(),
                "categories_fa_json": json.dumps(_lines(self.categories_fa.toPlainText()), ensure_ascii=False),
                "tags_fa_json": json.dumps(_lines(self.tags_fa.toPlainText()), ensure_ascii=False),
                "hashtags_fa_json": json.dumps(_lines(self.hashtags_fa.toPlainText()), ensure_ascii=False),
                "keywords_json": json.dumps(_lines(self.keywords_fa.toPlainText()), ensure_ascii=False),
                "sales_bullets_json": json.dumps(_lines(self.sales_bullets.toPlainText()), ensure_ascii=False),
                "social_caption_fa": self.social_caption.toPlainText().strip(),
            },
        )

    def _save_stage5(self) -> None:
        try:
            specs = json.loads(self.specs_fa.toPlainText().strip() or "{}")
            if not isinstance(specs, dict):
                raise ValueError
        except Exception:
            raise ValueError("مشخصات فارسی باید JSON Object معتبر باشد.")
        try:
            features = json.loads(self.technical_features.toPlainText().strip() or "{}")
            if not isinstance(features, dict):
                raise ValueError
        except Exception:
            raise ValueError("ویژگی‌های فنی باید JSON Object معتبر باشد.")

        self.kernel.stages.update(
            self.product_id,
            "specs",
            {
                "author_name": self.author_name.text().strip(),
                "license_name": self.license_name.text().strip(),
                "license_url": self.license_url.text().strip(),
                "commercial_status": str(self.commercial_status.currentData() or "review"),
                "technical_summary_fa": self.technical_summary.toPlainText().strip(),
                "specs_fa_json": json.dumps(specs, ensure_ascii=False),
                "technical_features_json": json.dumps(features, ensure_ascii=False),
            },
        )

    def _save_stage6(self) -> None:
        self.kernel.stages.update(
            self.product_id,
            "slider",
            {
                "homepage_slider_enabled": 1 if self.slider_enabled.isChecked() else 0,
                "homepage_slider_title_fa": self.slider_title.text().strip(),
                "homepage_slider_description_fa": self.slider_description.toPlainText().strip(),
                "homepage_slider_alt_text": self.slider_alt.text().strip(),
                "homepage_slider_focus_keyword": self.slider_focus.text().strip(),
                "homepage_slider_image_url": self.slider_image.currentText().strip(),
                "homepage_slider_button_text": self.slider_button.text().strip(),
                "homepage_slider_transition_effect": self.slider_transition.currentText().strip(),
                "homepage_slider_transition_duration_ms": self.slider_transition_ms.value(),
                "homepage_slider_display_duration_ms": self.slider_display_ms.value(),
                "homepage_slider_sort_order": self.slider_sort.value(),
                "homepage_slider_presentation_mode": self.slider_presentation.currentText().strip(),
                "homepage_slider_object_fit": self.slider_object_fit.currentText().strip(),
                "homepage_slider_focal_position": self.slider_focal.currentText().strip(),
                "homepage_slider_image_scale_percent": self.slider_scale.value(),
                "homepage_slider_position_x_percent": self.slider_x.value(),
                "homepage_slider_position_y_percent": self.slider_y.value(),
                "homepage_slider_background_mode": self.slider_bg_mode.currentText().strip(),
                "homepage_slider_background_color": self.slider_bg_color.text().strip(),
                "homepage_slider_background_blur_px": self.slider_blur.value(),
                "homepage_slider_desktop_max_width_percent": self.slider_desktop_w.value(),
                "homepage_slider_desktop_max_height_percent": self.slider_desktop_h.value(),
                "homepage_slider_mobile_max_width_percent": self.slider_mobile_w.value(),
                "homepage_slider_mobile_max_height_percent": self.slider_mobile_h.value(),
            },
        )

    def _save_stage7(self) -> None:
        self.kernel.stages.update(
            self.product_id,
            "publish",
            {
                "approved_for_sale": 1 if self.approved_for_sale.isChecked() else 0,
                "publish_as_product": 1 if self.publish_product.isChecked() else 0,
                "publish_as_portfolio": 1 if self.publish_portfolio.isChecked() else 0,
            },
        )

    def _finalize_current(self) -> None:
        if self.product_id is None:
            return
        code = STAGE_CODES[self.stack.currentIndex()]
        if not self._save_current(notify=False):
            QMessageBox.warning(self, "تأیید مرحله", "ابتدا خطاهای ذخیره همین مرحله را برطرف کن.")
            return
        try:
            self.kernel.stages.finalize(self.product_id, code)
        except Exception as exc:
            QMessageBox.warning(self, "تأیید مرحله", str(exc))
            self._refresh_stage_statuses()
            return
        self.load_product(self.product_id)
        QMessageBox.information(self, "تأیید مرحله", "مرحله ثبت نهایی شد.")

    def _unlock_current(self) -> None:
        if self.product_id is None:
            return
        code = STAGE_CODES[self.stack.currentIndex()]
        if not QMessageBox.question(
            self,
            "اصلاح مرحله",
            "قفل این مرحله باز شود؟ تا ثبت دوباره، اطلاعات این مرحله قابل تغییر است.",
        ) == QMessageBox.StandardButton.Yes:
            return
        try:
            self.kernel.stages.unlock(self.product_id, code)
        except Exception as exc:
            QMessageBox.warning(self, "اصلاح مرحله", str(exc))
            return
        self.load_product(self.product_id)

    # ------------------------------------------------------------------
    # Category / Profiles / Images
    # ------------------------------------------------------------------
    def _add_category(self) -> None:
        name = self.add_category_name.text().strip()
        slug = self.add_category_slug.text().strip().lower()
        slug = "-".join(part for part in "".join(
            ch if (ch.isascii() and (ch.isalnum() or ch == "-")) else "-"
            for ch in slug
        ).split("-") if part)
        if not name or not slug:
            QMessageBox.warning(self, "دسته", "نام فارسی و slug انگلیسی لازم است.")
            return
        current = _json_list(self.db.setting("custom_categories_json", "[]"))
        if any(
            isinstance(item, dict)
            and (
                str(item.get("slug") or "") == slug
                or str(item.get("name") or "") == name
            )
            for item in current
        ):
            QMessageBox.information(self, "دسته", "این دسته از قبل وجود دارد.")
            return
        current.append({"slug": slug, "name": name})
        self.db.set_setting("custom_categories_json", json.dumps(current, ensure_ascii=False))
        row = self.kernel.products.get(self.product_id) if self.product_id else None
        self._load_stage1(row or {})
        index = self.category.findData(slug)
        if index >= 0:
            self.category.setCurrentIndex(index)

    def _selected_profile(self) -> dict[str, Any] | None:
        row = self.profile_table.currentRow()
        if row < 0:
            return None
        item = self.profile_table.item(row, 0)
        return dict(item.data(Qt.ItemDataRole.UserRole) or {}) if item else None

    def _reload_profiles(self) -> None:
        if self.product_id is None:
            self.profile_table.setRowCount(0)
            return
        profiles = self.kernel.commerce.profiles(self.product_id)
        self.profile_table.setRowCount(len(profiles))
        for row_index, profile in enumerate(profiles):
            production_count = len(profile.get("production_rows") or [])
            filament_count = len(profile.get("material_options") or [])
            combinations = production_count * filament_count
            dimensions = " × ".join(
                f"{float(profile.get(key) or 0):g}"
                for key in ("part_length_cm", "part_width_cm", "part_height_cm")
            )
            summary = self.kernel.commerce.summary(profile)
            if summary.get("min") and summary.get("max"):
                price = (
                    f"{summary['min']:,}"
                    if summary["min"] == summary["max"]
                    else f"{summary['min']:,} – {summary['max']:,}"
                )
            else:
                price = "—"
            values = (
                profile.get("name") or "—",
                profile.get("size_label") or "—",
                dimensions,
                str(production_count),
                str(filament_count),
                str(combinations),
                price,
            )
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if col == 0:
                    item.setData(Qt.ItemDataRole.UserRole, profile)
                self.profile_table.setItem(row_index, col, item)

    def _new_profile(self) -> None:
        if self.product_id is None:
            return
        dialog = ProfileEditorDialog(
            self.kernel.filaments.list(),
            parent=self,
            filament_core=self.kernel.filaments,
        )
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                self.kernel.commerce.upsert_profile(self.product_id, dialog.values())
            except Exception as exc:
                QMessageBox.warning(self, "پروفایل", str(exc))
                return
            self._reload_profiles()
            self._refresh_stage_statuses()

    def _edit_profile(self) -> None:
        if self.product_id is None:
            return
        profile = self._selected_profile()
        if not profile:
            QMessageBox.warning(self, "پروفایل", "یک پروفایل را انتخاب کن.")
            return
        dialog = ProfileEditorDialog(
            self.kernel.filaments.list(),
            profile=profile,
            parent=self,
            filament_core=self.kernel.filaments,
        )
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                self.kernel.commerce.upsert_profile(
                    self.product_id,
                    dialog.values(),
                    replace_key=str(profile.get("key") or ""),
                )
            except Exception as exc:
                QMessageBox.warning(self, "پروفایل", str(exc))
                return
            self._reload_profiles()
            self._refresh_stage_statuses()

    def _clone_profile(self) -> None:
        if self.product_id is None:
            return
        profile = self._selected_profile()
        if not profile:
            QMessageBox.warning(self, "پروفایل", "یک پروفایل را انتخاب کن.")
            return

        draft = dict(profile)
        draft.pop("key", None)
        draft["name"] = f"{profile.get('name') or 'پروفایل'} - کپی"
        draft["size_label"] = f"{profile.get('size_label') or ''} - کپی".strip()

        dialog = ProfileEditorDialog(
            self.kernel.filaments.list(),
            profile=draft,
            parent=self,
            filament_core=self.kernel.filaments,
        )
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        try:
            self.kernel.commerce.upsert_profile(
                self.product_id,
                dialog.values(),
            )
        except Exception as exc:
            QMessageBox.warning(self, "پروفایل", str(exc))
            return

        self._reload_profiles()
        self._refresh_stage_statuses()

    def _delete_profile(self) -> None:
        if self.product_id is None:
            return
        profile = self._selected_profile()
        if not profile:
            return
        if QMessageBox.question(
            self,
            "حذف پروفایل",
            f"پروفایل «{profile.get('name') or ''}» حذف شود؟",
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            self.kernel.commerce.delete_profile(self.product_id, str(profile.get("key") or ""))
        except Exception as exc:
            QMessageBox.warning(self, "پروفایل", str(exc))
            return
        self._reload_profiles()
        self._refresh_stage_statuses()

    def _sync_slider_from_image_grid(self, url: str) -> None:
        if hasattr(self, "slider_image"):
            self.slider_image.setEditText(str(url or ""))

    def _delete_single_image(self, url: str) -> None:
        if self.product_id is None or not url:
            return
        if QMessageBox.question(
            self,
            "حذف تصویر",
            "این تصویر از Product حذف شود؟ فایل محلی برای Recovery پاک نمی‌شود.",
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            self.kernel.images.remove_urls(
                self.product_id,
                [url],
            )
        except Exception as exc:
            QMessageBox.warning(self, "حذف تصویر", str(exc))
            return
        self.load_product(self.product_id)

    def _delete_selected_images(self) -> None:
        if self.product_id is None:
            return
        urls = self.image_grid.selected_urls()
        if not urls:
            QMessageBox.warning(
                self,
                "حذف گروهی",
                "حداقل یک تصویر را انتخاب کن.",
            )
            return
        if QMessageBox.question(
            self,
            "حذف گروهی تصاویر",
            f"{len(urls)} تصویر از Product حذف شوند؟ فایل‌های محلی برای Recovery پاک نمی‌شوند.",
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            self.kernel.images.remove_urls(
                self.product_id,
                urls,
            )
        except Exception as exc:
            QMessageBox.warning(self, "حذف گروهی", str(exc))
            return
        self.load_product(self.product_id)

    def _edit_selected_image_seo(self) -> None:
        urls = self.image_grid.selected_urls()
        if not urls:
            QMessageBox.warning(
                self,
                "SEO تصاویر",
                "حداقل یک تصویر را انتخاب کن.",
            )
            return
        self._edit_image_seo(urls)

    def _edit_image_seo(self, urls: list[str]) -> None:
        if self.product_id is None:
            return
        items = [
            self.image_grid.item_for_url(url)
            for url in urls
        ]
        items = [item for item in items if item]
        if not items:
            return
        dialog = ImageSeoDialog(items, parent=self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        try:
            self.kernel.images.update_metadata(
                self.product_id,
                urls,
                dialog.values(),
            )
        except Exception as exc:
            QMessageBox.warning(self, "SEO تصاویر", str(exc))
            return
        self.load_product(self.product_id)

    def _apply_product_image_seo(self) -> None:
        if self.product_id is None:
            return
        urls = self.image_grid.selected_urls()
        if not urls:
            QMessageBox.warning(
                self,
                "SEO تصاویر",
                "برای اعمال SEO فارسی، حداقل یک تصویر را انتخاب کن.",
            )
            return
        row = self.kernel.products.get(self.product_id) or {}
        title = (
            str(row.get("seo_title_fa") or "").strip()
            or str(row.get("title_fa") or "").strip()
            or str(row.get("source_title") or "").strip()
        )
        caption = (
            str(row.get("short_description_fa") or "").strip()
            or str(row.get("seo_description_fa") or "").strip()
        )
        keywords: list[str] = []
        for field in ("keywords_json", "tags_fa_json", "hashtags_fa_json"):
            for item in _json_list(row.get(field)):
                value = str(item or "").strip().lstrip("#")
                if value and value not in keywords:
                    keywords.append(value)

        try:
            for index, url in enumerate(urls, 1):
                self.kernel.images.update_metadata(
                    self.product_id,
                    [url],
                    {
                        "alt_text": f"{title} - تصویر {index}"[:220],
                        "title": title[:220],
                        "caption": caption[:500],
                        "keywords": keywords[:16],
                    },
                )
        except Exception as exc:
            QMessageBox.warning(self, "SEO تصاویر", str(exc))
            return
        self.load_product(self.product_id)

    def _start_image_task(self, label: str, fn) -> None:
        if self._image_worker is not None:
            QMessageBox.information(
                self,
                "تصاویر",
                "یک عملیات تصویر در حال اجرا است.",
            )
            return
        self.image_task_status.setText(label)

        def job(progress):
            return fn(progress)

        worker = Worker(job)
        self._image_worker = worker
        worker.signals.progress.connect(
            lambda value, message: self.image_task_status.setText(
                f"{value}% — {message}"
            )
        )
        worker.signals.result.connect(
            lambda _result: self._image_task_done()
        )
        worker.signals.error.connect(self._image_task_error)
        worker.signals.finished.connect(self._image_task_finished)
        self.task_pool.start(worker)

    def _recover_product_images(self) -> None:
        if self.product_id is None:
            return
        limit = self.image_recover_limit.value()
        self._start_image_task(
            "بازیابی تصاویر…",
            lambda progress: self.kernel.acquisition.recover_product_images(
                self.product_id,
                image_limit=limit,
                progress=progress,
            ),
        )

    def _capture_product_screenshot(self) -> None:
        if self.product_id is None:
            return

        def task(progress):
            progress(10, "باز کردن صفحه محصول…")
            path = self.kernel.images.capture_source_screenshot(
                self.product_id
            )
            progress(100, "اسکرین‌شات ذخیره شد")
            return path

        self._start_image_task(
            "دریافت اسکرین‌شات…",
            task,
        )

    def _image_task_done(self) -> None:
        self.image_task_status.setText("✅ عملیات تصویر تمام شد")
        if self.product_id is not None:
            self.load_product(self.product_id)

    def _image_task_error(self, detail: str) -> None:
        self.image_task_status.setText("❌ عملیات تصویر ناموفق")
        message = (
            str(detail or "").splitlines()[-1]
            if detail
            else "خطای ناشناخته"
        )
        QMessageBox.warning(self, "تصاویر", message)

    def _image_task_finished(self) -> None:
        self._image_worker = None

    def _rebuild_image_metadata(self) -> None:
        if self.product_id is None:
            return
        if not self._save_stage3_safely():
            return
        try:
            self.kernel.images.finalize(self.product_id)
        except Exception as exc:
            QMessageBox.warning(self, "Metadata تصویر", str(exc))
            return
        self.load_product(self.product_id)

    def _save_stage3_safely(self) -> bool:
        try:
            self._save_stage3()
            return True
        except Exception as exc:
            QMessageBox.warning(self, "تصاویر", str(exc))
            return False

    def _queue_image_selection_save(self) -> None:
        if self.product_id is None:
            return
        self._image_selection_save_timer.start()

    def _persist_image_selection(self) -> None:
        if self.product_id is None:
            return
        if not self._save_stage3_safely():
            return
        selected_count = len(self.image_grid.selected_urls())
        self.image_task_status.setText(
            f"✅ انتخاب {selected_count} تصویر ذخیره شد"
        )
        self._refresh_stage_statuses()


    # ------------------------------------------------------------------
    # AI + status
    # ------------------------------------------------------------------
    def _run_ai(self, *, current_only: bool) -> None:
        if self.product_id is None:
            QMessageBox.warning(
                self,
                "هوش مصنوعی",
                "ابتدا محصول را انتخاب کن.",
            )
            return
        if (
            self._ai_worker is not None
            or self._ai_quote_worker is not None
        ):
            QMessageBox.information(
                self,
                "هوش مصنوعی",
                "یک عملیات AI در حال اجرا است.",
            )
            return

        mode = str(self.ai_source.currentData() or "data")
        code = STAGE_CODES[self.stack.currentIndex()]
        if current_only and code in {"commerce", "publish"}:
            QMessageBox.information(
                self,
                "هوش مصنوعی",
                "این مرحله اپراتوری است؛ AI قیمت/Profile/Filament/انتشار را تغییر نمی‌دهد.",
            )
            return

        if current_only and code == "images":
            self._run_image_smart_repair()
            return

        if not current_only:
            answer = QMessageBox.question(
                self,
                "اصلاح کامل محتوایی با AI",
                "این اجرا برای اصلاح ترجمه و SEO، مراحل محتوایی نهایی‌شده "
                "(عنوان/محتوا/اسلایدر) را دوباره برای بازبینی باز می‌کند.\n\n"
                "داده‌های فنی قابل اثبات Source (دسته، زمان چاپ، وزن، ابعاد و "
                "Filamentهای موجود در کتابخانه) بدون حدس به محصول/Profile اول "
                "افزوده می‌شوند. قیمت فقط از تنظیمات واقعی Filament محاسبه می‌شود.\n\n"
                "مجوز/وضعیت تجاری و انتشار همچنان اپراتوری می‌مانند. تصاویر با "
                "Finalizer محلی WebP/SEO بازسازی می‌شوند و هر مرحله واقعاً کامل "
                "به‌صورت خودکار سبز می‌شود.\n\nادامه داده شود؟",
                (
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No
                ),
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
            try:
                self.kernel.stages.prepare_ai_content_repair(
                    int(self.product_id)
                )
            except Exception as exc:
                QMessageBox.warning(
                    self,
                    "اصلاح کامل محتوایی",
                    str(exc),
                )
                return
            self.load_product(int(self.product_id))

        request = {
            "product_id": int(self.product_id),
            "mode": mode,
            "target_stage": code if current_only else None,
        }
        self._pending_ai_request = request
        self._pending_ai_quote = None
        self.ai_current.setEnabled(False)
        self.ai_all.setEnabled(False)
        self.ai_status.setText(
            "محاسبه هزینه و سازگاری Model…"
        )

        def quote_job(progress):
            progress(10, "خواندن Provider/Model فعال")
            quote = self.kernel.providers.estimate_product_ai(
                request["product_id"],
                request["mode"],
                target_stage=request["target_stage"],
            )
            progress(100, "برآورد آماده")
            return quote

        worker = Worker(quote_job)
        self._ai_quote_worker = worker
        worker.signals.progress.connect(
            lambda value, message: self.ai_status.setText(
                f"{value}% — {message}"
            )
        )
        worker.signals.result.connect(self._ai_quote_ready)
        worker.signals.error.connect(self._ai_quote_error)
        worker.signals.finished.connect(
            self._ai_quote_finished
        )
        self.task_pool.start(worker)

    def _run_image_smart_repair(self) -> None:
        """Repair image SEO from persisted Product/local files without page fetch.

        Image SEO filenames and embedded metadata are deterministic derived
        state. They must not depend on a live MakerWorld/Product HTTP request.
        """
        if self.product_id is None:
            return

        product_id = int(self.product_id)
        status = next(
            (
                item
                for item in self.kernel.stages.statuses(product_id)
                if item.get("stage") == "images"
            ),
            {},
        )
        if not bool(status.get("finalized")):
            if not self._save_stage3_safely():
                return

        self.ai_current.setEnabled(False)
        self.ai_all.setEnabled(False)
        self.ai_cost_hint.setText(
            "هزینه این مرحله: صفر • SEO/Alt/نام فایل SEO/Metadata "
            "از دیتای ذخیره‌شده و فایل‌های محلی ساخته می‌شود."
        )
        self.ai_status.setText(
            "تکمیل هوشمند محلی تصاویر…"
        )

        def job(progress):
            before = next(
                (
                    item
                    for item in self.kernel.stages.statuses(
                        product_id
                    )
                    if item.get("stage") == "images"
                ),
                {},
            )
            progress(
                20,
                "بررسی Alt، نام SEO و Metadata تصاویر",
            )
            finalized = self.kernel.images.finalize(product_id)
            progress(
                85,
                "بازبینی نقص‌های تصویر بعد از نهایی‌سازی",
            )
            after = next(
                (
                    item
                    for item in self.kernel.stages.statuses(
                        product_id
                    )
                    if item.get("stage") == "images"
                ),
                {},
            )
            progress(100, "تصاویر بازبینی شدند")
            return {
                "product_id": product_id,
                "local_image_repair": True,
                "target_stages": ["images"],
                "changed_fields": [
                    "image_alt_texts_json",
                    "image_metadata_json",
                    "selected_images_json",
                    "primary_image_url",
                ],
                "before_missing": list(
                    before.get("missing") or []
                ),
                "after_missing": list(
                    after.get("missing") or []
                ),
                "image_finalize": dict(finalized or {}),
            }

        worker = Worker(job)
        self._ai_worker = worker
        worker.signals.progress.connect(
            lambda value, message: self.ai_status.setText(
                f"{value}% — {message}"
            )
        )
        worker.signals.result.connect(self._ai_done)
        worker.signals.error.connect(
            self._image_smart_error
        )
        worker.signals.finished.connect(
            self._ai_finished
        )
        self.task_pool.start(worker)

    def _image_smart_error(self, detail: str) -> None:
        self.ai_status.setText(
            "❌ تکمیل SEO تصاویر ناموفق"
        )
        show_diagnostic_error(
            self,
            "خطای تکمیل هوشمند تصاویر",
            detail,
            context={
                "product_id": self.product_id,
                "provider": "local-deterministic",
                "model": "image-seo-finalizer",
                "source_mode": "saved/local-files",
                "stage": "images",
            },
        )

    def _ai_quote_ready(self, quote) -> None:
        self._pending_ai_quote = dict(quote or {})

    def _ai_quote_error(self, detail: str) -> None:
        self._pending_ai_quote = None
        self.ai_status.setText("❌ برآورد AI ناموفق")
        active = self.kernel.providers.active()
        show_diagnostic_error(
            self,
            "پیش‌بررسی هوش مصنوعی",
            detail,
            context={
                "product_id": self.product_id,
                "provider": active.get("provider"),
                "model": active.get("model"),
                "source_mode": str(
                    self.ai_source.currentData() or ""
                ),
            },
        )

    def _ai_quote_finished(self) -> None:
        self._ai_quote_worker = None
        request = self._pending_ai_request
        quote = self._pending_ai_quote
        self._pending_ai_request = None
        self._pending_ai_quote = None

        if not request or not quote:
            self.ai_current.setEnabled(True)
            self.ai_all.setEnabled(True)
            return

        if self.product_id != request["product_id"]:
            self.ai_status.setText(
                "محصول عوض شده؛ AI اجرا نشد."
            )
            self.ai_current.setEnabled(True)
            self.ai_all.setEnabled(True)
            return

        quote_text = format_cost_quote(quote)
        if quote.get("free"):
            cost_short = "رایگان"
        elif quote.get("cost_known"):
            cost_short = "$" + (
                f"{float(quote.get('estimated_usd') or 0):.6f}"
            )
        else:
            cost_short = "نامشخص"
        self.ai_cost_hint.setText(
            f"هزینه آخرین برآورد: {cost_short}"
        )

        answer = QMessageBox.question(
            self,
            "تأیید هزینه و اجرای هوش مصنوعی",
            quote_text + "\n\nاجرا شود؟",
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.ai_status.setText(
                "اجرای AI توسط اپراتور لغو شد."
            )
            self.ai_current.setEnabled(True)
            self.ai_all.setEnabled(True)
            return

        active_now = self.kernel.providers.active()
        if (
            str(active_now.get("provider") or "")
            != str(quote.get("provider") or "")
            or str(active_now.get("model") or "")
            != str(quote.get("model") or "")
        ):
            self.ai_status.setText(
                "Provider/Model بعد از برآورد تغییر کرده؛ "
                "دوباره AI را بزن."
            )
            self.ai_current.setEnabled(True)
            self.ai_all.setEnabled(True)
            return

        QTimer.singleShot(
            0,
            lambda req=dict(request): self._start_ai_execution(
                req
            ),
        )

    def _start_ai_execution(
        self,
        request: dict[str, Any],
    ) -> None:
        product_id = int(request["product_id"])
        mode = str(request["mode"])
        target = request.get("target_stage")
        self.ai_status.setText(
            "AI در حال ارسال/دریافت Product…"
        )

        def job(progress):
            progress(10, "شروع درخواست Product")
            result = dict(
                self.kernel.ai.execute(
                    product_id,
                    mode,
                    target_stage=target,
                    refresh_existing=True,
                )
                or {}
            )
            result["_qt_full_content_run"] = target is None
            progress(100, "تمام")
            return result

        worker = Worker(job)
        self._ai_worker = worker
        worker.signals.progress.connect(
            lambda value, message: self.ai_status.setText(
                f"{value}% — {message}"
            )
        )
        worker.signals.result.connect(self._ai_done)
        worker.signals.error.connect(self._ai_error)
        worker.signals.finished.connect(
            self._ai_finished
        )
        self.task_pool.start(worker)

    def _ai_done(self, result=None) -> None:
        result = dict(result or {})
        result_product_id = int(
            result.get("product_id")
            or self.product_id
            or 0
        )
        if (
            self.product_id is not None
            and result_product_id
            and int(self.product_id) != result_product_id
        ):
            self.ai_status.setText(
                "نتیجه برای محصول دیگری بود؛ نمایش فعلی تغییر نکرد."
            )
            return

        full_content_run = bool(
            result.pop("_qt_full_content_run", False)
        )

        if self.product_id is not None and full_content_run:
            result = self.kernel.postprocess_full_product_ai(
                int(self.product_id),
                result,
            )

        if self.product_id is not None:
            self.load_product(self.product_id)

        statuses = (
            self.kernel.stages.statuses(self.product_id)
            if self.product_id is not None
            else []
        )
        target_stages = {
            str(value or "")
            for value in (
                result.get("target_stages")
                or STAGE_CODES
            )
            if str(value or "")
        }
        relevant = [
            item
            for item in statuses
            if str(item.get("stage") or "") in target_stages
        ]
        remaining_ai = sum(
            int(item.get("ai_fixable_count") or 0)
            for item in relevant
        )
        remaining_operator = sum(
            int(item.get("operator_count") or 0)
            for item in relevant
        )
        changed = len(
            {
                str(value or "")
                for value in (
                    result.get("changed_fields") or []
                )
                if str(value or "")
            }
        )
        source_note = (
            " • لینک 403/429 بود؛ دیتای ذخیره‌شده استفاده شد"
            if result.get("source_fallback")
            else ""
        )

        if remaining_ai:
            self.ai_status.setText(
                f"⚠️ اجرا شد • {changed} تغییر • "
                f"{remaining_ai} مورد قابل تکمیل هوشمند هنوز باقی است{source_note}"
            )
            return

        if result.get("local_image_repair"):
            finalized = dict(
                result.get("image_finalize") or {}
            )
            kept = int(finalized.get("kept") or 0)
            if remaining_operator:
                self.ai_status.setText(
                    f"✅ SEO تصاویر تکمیل شد • {kept} تصویر • "
                    f"{remaining_operator} مورد دستی باقی است"
                )
            else:
                self.ai_status.setText(
                    f"✅ SEO/Alt/نام SEO/Metadata تصاویر تکمیل شد • "
                    f"{kept} تصویر"
                )
            return

        if remaining_operator:
            self.ai_status.setText(
                f"✅ بخش هوشمند تکمیل شد • {changed} تغییر • "
                f"{remaining_operator} مورد اپراتوری/واقعی باقی است{source_note}"
            )
        else:
            self.ai_status.setText(
                f"✅ AI تکمیل شد • {changed} فیلد تغییر کرد{source_note}"
            )

    def _ai_error(self, detail: str) -> None:
        self.ai_status.setText("❌ AI خطا")
        active = self.kernel.providers.active()
        show_diagnostic_error(
            self,
            "خطای هوش مصنوعی Product",
            detail,
            context={
                "product_id": self.product_id,
                "provider": active.get("provider"),
                "model": active.get("model"),
                "source_mode": str(
                    self.ai_source.currentData() or ""
                ),
                "stage": STAGE_CODES[
                    self.stack.currentIndex()
                ],
            },
        )

    def _ai_finished(self) -> None:
        self.ai_current.setEnabled(True)
        self.ai_all.setEnabled(True)
        self._ai_worker = None

    def _refresh_stage_statuses(self) -> None:
        if self.product_id is None:
            self.stepper.set_statuses([])
            return
        statuses = self.kernel.stages.statuses(self.product_id)
        self.stepper.set_statuses(statuses)
        self._refresh_readiness_text()
        current = self.stack.currentIndex()
        if 0 <= current < len(statuses):
            item = statuses[current]
            missing = item.get("missing") or []
            suffix = f" — کمبود: {', '.join(missing[:4])}" if missing else ""
            self.stage_state_label.setText(
                f"{item['icon']} {item['label']}{suffix}"
            )
            self.unlock_stage_btn.setEnabled(bool(item.get("finalized")))
            self.finalize_stage_btn.setEnabled(not bool(item.get("finalized")) or STAGE_CODES[current] == "images")

    def _refresh_readiness_text(self) -> None:
        if self.product_id is None:
            self.readiness_text.setPlainText("")
            return
        statuses = self.kernel.stages.statuses(self.product_id)
        lines = []
        for item in statuses:
            lines.append(f"{item['icon']} {item['label']}")
            for missing in (item.get("missing") or [])[:8]:
                lines.append(f"    - {missing}")
        self.readiness_text.setPlainText("\n".join(lines))

    def _set_stage(self, index: int) -> None:
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)
            self.footer.set_position(index, self.stack.count())
            code = STAGE_CODES[index]
            self.ai_current.setEnabled(code not in {"commerce", "publish"} and self._ai_worker is None)
            self._refresh_stage_statuses()

    def _move(self, delta: int) -> None:
        current = self.stack.currentIndex()
        target = max(0, min(self.stack.count() - 1, current + int(delta)))
        self.stepper.set_stage(target)
