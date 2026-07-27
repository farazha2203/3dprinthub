from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from pathlib import Path

from .models import (
    CustomerReusableModel,
    Material,
    Order,
    OrderIntakeDetail,
    OrderReferencePhoto,
    OrderAttachment,
)




class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_clean(item, initial) for item in data]
        if data:
            return [single_clean(data, initial)]
        return []


ALLOWED_DOCUMENT_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv",
    ".zip", ".rar", ".7z", ".stl", ".obj", ".3mf", ".step", ".stp",
    ".iges", ".igs", ".dxf", ".dwg",
}


PHOTO_FIELDS = [
    ("photo_top", "top", "عکس از بالا"),
    ("photo_front", "front", "عکس از روبه‌رو"),
    ("photo_right", "right", "عکس از سمت راست"),
    ("photo_left", "left", "عکس از سمت چپ"),
    ("photo_extra_1", "extra_1", "عکس تکمیلی اول"),
    ("photo_extra_2", "extra_2", "عکس تکمیلی دوم"),
]


def _photo_field(label, required=False):
    return forms.ImageField(
        required=required,
        label=label,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "w-full rounded-2xl border border-slate-700 bg-slate-950 text-slate-300 p-3",
                "accept": "image/jpeg,image/png,image/webp",
            }
        ),
        help_text="JPG، PNG یا WebP؛ حداکثر ۸ مگابایت.",
    )


class Phase10OrderForm(forms.ModelForm):
    request_mode = forms.ChoiceField(
        choices=OrderIntakeDetail.REQUEST_MODE_CHOICES,
        initial="new_part",
        label="نوع سفارش",
        widget=forms.RadioSelect(attrs={"class": "request-mode-radio"}),
    )
    reusable_model = forms.ModelChoiceField(
        queryset=CustomerReusableModel.objects.none(),
        required=False,
        label="مدل سه‌بعدی محفوظ قبلی",
        empty_label="مدل قبلی را انتخاب کنید",
        widget=forms.Select(attrs={"class": "form-input"}),
        help_text="فایل برای شما نمایش یا ارسال نمی‌شود؛ فقط نام مدل موجود را انتخاب می‌کنید.",
    )
    ready_catalog_asset_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    usage_environment = forms.ChoiceField(
        choices=OrderIntakeDetail.ENVIRONMENT_CHOICES,
        initial="unknown",
        label="محیط استفاده",
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    contact_with_gasoline = forms.BooleanField(required=False, label="تماس با بنزین")
    contact_with_oil = forms.BooleanField(required=False, label="تماس با روغن")
    contact_with_grease = forms.BooleanField(required=False, label="تماس با گریس")
    contact_with_water = forms.BooleanField(required=False, label="تماس با آب یا رطوبت")
    contact_with_chemicals = forms.BooleanField(required=False, label="تماس با مواد شیمیایی")
    chemical_details = forms.CharField(
        required=False,
        label="نام یا نوع ماده شیمیایی",
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "مثلاً ضدیخ، شوینده صنعتی، اسید رقیق و..."}),
    )
    operating_temperature_min = forms.DecimalField(
        required=False,
        label="حداقل دمای کاری °C",
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "0.1"}),
    )
    operating_temperature_max = forms.DecimalField(
        required=False,
        label="حداکثر دمای کاری °C",
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "0.1"}),
    )
    required_properties = forms.CharField(
        required=False,
        label="خواص مورد انتظار قطعه",
        widget=forms.Textarea(attrs={"class": "form-input min-h-28", "placeholder": "استحکام، انعطاف، مقاومت حرارتی، مقاومت ضربه، ظاهر، آب‌بندی و..."}),
    )
    exact_dimensions = forms.CharField(
        required=False,
        label="ابعاد و اندازه‌های دقیق",
        widget=forms.Textarea(attrs={"class": "form-input min-h-28", "placeholder": "طول، عرض، ارتفاع، قطرها، فاصله سوراخ‌ها، ضخامت و واحد اندازه‌گیری"}),
    )
    installation_location = forms.CharField(
        required=False,
        label="محل و نحوه نصب",
        widget=forms.Textarea(attrs={"class": "form-input min-h-24"}),
    )
    load_conditions = forms.CharField(
        required=False,
        label="فشار، ضربه و نوع بار",
        widget=forms.Textarea(attrs={"class": "form-input min-h-24"}),
    )
    dimensional_tolerance = forms.CharField(
        required=False,
        label="تلرانس مورد نیاز",
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "مثلاً ±0.2 میلی‌متر یا نیازمند مونتاژ دقیق"}),
    )
    has_physical_sample = forms.BooleanField(required=False, label="نمونه فیزیکی قطعه موجود است")
    sample_delivery_method = forms.CharField(
        required=False,
        label="روش تحویل نمونه",
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "حضوری، پیک، پست یا هماهنگی تلفنی"}),
    )
    extra_notes = forms.CharField(
        required=False,
        label="توضیحات تکمیلی",
        widget=forms.Textarea(attrs={"class": "form-input min-h-24"}),
    )
    photo_top = _photo_field("عکس از بالا")
    photo_front = _photo_field("عکس از روبه‌رو")
    photo_right = _photo_field("عکس از سمت راست")
    photo_left = _photo_field("عکس از سمت چپ")
    photo_extra_1 = _photo_field("عکس تکمیلی اول")
    photo_extra_2 = _photo_field("عکس تکمیلی دوم")

    documents = MultipleFileField(
        required=False,
        label="مدارک و فایل‌های فنی",
        widget=MultipleFileInput(attrs={
            "class": "w-full rounded-2xl border border-slate-700 bg-slate-950 text-slate-300 p-3",
            "accept": ".pdf,.doc,.docx,.xls,.xlsx,.txt,.csv,.zip,.rar,.7z,.stl,.obj,.3mf,.step,.stp,.iges,.igs,.dxf,.dwg",
        }),
        help_text="حداکثر ۵ فایل؛ هر فایل حداکثر ۲۰ مگابایت. فایل‌ها خصوصی نگهداری می‌شوند.",
    )

    class Meta:
        model = Order
        fields = [
            "first_name", "last_name", "phone", "service_type", "material",
            "color", "quantity", "description",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "نام"}),
            "last_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "نام خانوادگی"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "مثلاً 09123456789"}),
            "service_type": forms.Select(attrs={"class": "form-input"}),
            "material": forms.Select(attrs={"class": "form-input"}),
            "color": forms.TextInput(attrs={"class": "form-input", "placeholder": "رنگ موردنظر"}),
            "quantity": forms.NumberInput(attrs={"class": "form-input", "min": "1"}),
            "description": forms.Textarea(attrs={"class": "form-input min-h-32", "placeholder": "شرح قطعه و نتیجه‌ای که انتظار دارید"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        initial_reusable = kwargs.pop("initial_reusable", None)
        ready_catalog_asset_id = kwargs.pop("ready_catalog_asset_id", None)
        super().__init__(*args, **kwargs)
        self.fields["material"].queryset = Material.objects.filter(is_active=True)
        self.fields["material"].empty_label = "متریال موردنظر را انتخاب کنید"
        if self.user and self.user.is_authenticated:
            self.fields["reusable_model"].queryset = CustomerReusableModel.objects.filter(
                customer=self.user,
                available_for_reorder=True,
            )
            profile = getattr(self.user, "customer_profile", None)
            if profile and not self.is_bound:
                self.fields["first_name"].initial = profile.first_name or self.user.first_name
                self.fields["last_name"].initial = profile.last_name or self.user.last_name
                self.fields["phone"].initial = profile.phone
        if initial_reusable and not self.is_bound:
            self.fields["request_mode"].initial = "reorder_model"
            self.fields["reusable_model"].initial = initial_reusable.pk
            self.fields["material"].initial = initial_reusable.material_hint_id
            self.fields["color"].initial = initial_reusable.default_color
            self.fields["quantity"].initial = initial_reusable.default_quantity
        if ready_catalog_asset_id and not self.is_bound:
            self.fields["request_mode"].initial = "ready_catalog"
            self.fields["ready_catalog_asset_id"].initial = ready_catalog_asset_id

    def clean(self):
        cleaned = super().clean()
        mode = cleaned.get("request_mode")
        if mode == "new_part":
            missing = [label for field, _view, label in PHOTO_FIELDS[:4] if not cleaned.get(field)]
            if missing:
                raise ValidationError("برای قطعه جدید این تصاویر الزامی‌اند: " + "، ".join(missing))
            total = sum(1 for field, _view, _label in PHOTO_FIELDS if cleaned.get(field))
            if not 4 <= total <= 6:
                raise ValidationError("برای قطعه جدید باید بین ۴ تا ۶ تصویر ارسال شود.")
        elif mode == "reorder_model":
            model = cleaned.get("reusable_model")
            if model is None:
                self.add_error("reusable_model", "مدل محفوظ قبلی را انتخاب کنید.")
            elif not self.user or not self.user.is_authenticated or model.customer_id != self.user.id:
                self.add_error("reusable_model", "این مدل متعلق به حساب شما نیست.")
        elif mode == "ready_catalog":
            asset_id = cleaned.get("ready_catalog_asset_id")
            if not asset_id:
                self.add_error("ready_catalog_asset_id", "مدل آماده انتخاب نشده است.")
            else:
                from store.catalog_sync import public_catalog_queryset

                if not public_catalog_queryset().filter(pk=asset_id).exists():
                    self.add_error("ready_catalog_asset_id", "این مدل آماده قابل سفارش عمومی نیست.")

        if cleaned.get("contact_with_chemicals") and not cleaned.get("chemical_details"):
            self.add_error("chemical_details", "نوع ماده شیمیایی را توضیح دهید.")
        min_temp = cleaned.get("operating_temperature_min")
        max_temp = cleaned.get("operating_temperature_max")
        if min_temp is not None and max_temp is not None and min_temp > max_temp:
            self.add_error("operating_temperature_max", "حداکثر دما نمی‌تواند کمتر از حداقل دما باشد.")

        for field, _view, _label in PHOTO_FIELDS:
            image = cleaned.get(field)
            if image and image.size > 8 * 1024 * 1024:
                self.add_error(field, "حجم هر تصویر باید حداکثر ۸ مگابایت باشد.")

        documents = cleaned.get("documents") or []
        if len(documents) > 5:
            self.add_error("documents", "حداکثر ۵ فایل فنی قابل ارسال است.")
        for document in documents:
            suffix = Path(document.name).suffix.lower()
            if suffix not in ALLOWED_DOCUMENT_EXTENSIONS:
                self.add_error("documents", f"فرمت فایل {document.name} مجاز نیست.")
            if document.size > 20 * 1024 * 1024:
                self.add_error("documents", f"حجم فایل {document.name} بیشتر از ۲۰ مگابایت است.")
        return cleaned

    @transaction.atomic
    def save_order(self, *, customer=None):
        order = super().save(commit=False)
        if customer and customer.is_authenticated:
            order.customer = customer
        order.save()
        self.save_m2m()
        detail_fields = [
            "request_mode", "reusable_model", "ready_catalog_asset_id", "usage_environment",
            "contact_with_gasoline", "contact_with_oil", "contact_with_grease", "contact_with_water",
            "contact_with_chemicals", "chemical_details", "operating_temperature_min",
            "operating_temperature_max", "required_properties", "exact_dimensions",
            "installation_location", "load_conditions", "dimensional_tolerance", "has_physical_sample",
            "sample_delivery_method", "extra_notes",
        ]
        detail = OrderIntakeDetail.objects.create(
            order=order,
            **{name: self.cleaned_data.get(name) for name in detail_fields},
        )
        for field, view_type, _label in PHOTO_FIELDS:
            image = self.cleaned_data.get(field)
            if image:
                OrderReferencePhoto.objects.create(order=order, view_type=view_type, image=image)
        for document in self.cleaned_data.get("documents") or []:
            OrderAttachment.objects.create(
                order=order,
                file=document,
                original_name=Path(document.name).name,
                content_type=getattr(document, "content_type", "") or "",
                size_bytes=getattr(document, "size", 0) or 0,
            )
        if detail.reusable_model_id:
            detail.reusable_model.last_ordered_at = order.created_at
            detail.reusable_model.save(update_fields=["last_ordered_at", "updated_at"])
        return order
