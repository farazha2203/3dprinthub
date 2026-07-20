from django import forms

from .models import ProductComment, ProductRequest


class ProductCommentForm(forms.ModelForm):
    class Meta:
        model = ProductComment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "class": "form-input min-h-28",
                    "placeholder": "سؤال یا دیدگاه خود را درباره این محصول بنویسید...",
                }
            )
        }


class ProductRequestForm(forms.ModelForm):
    class Meta:
        model = ProductRequest
        fields = [
            "request_type",
            "full_name",
            "phone",
            "title",
            "brand",
            "model",
            "year",
            "description",
        ]
        widgets = {
            "request_type": forms.Select(attrs={"class": "form-input"}),
            "full_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "نام و نام خانوادگی"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "مثلاً 09123456789"}),
            "title": forms.TextInput(attrs={"class": "form-input", "placeholder": "مثلاً چرخ‌دنده آینه پژو 405"}),
            "brand": forms.TextInput(attrs={"class": "form-input", "placeholder": "برند دستگاه یا وسیله"}),
            "model": forms.TextInput(attrs={"class": "form-input", "placeholder": "مدل"}),
            "year": forms.TextInput(attrs={"class": "form-input", "placeholder": "سال ساخت یا نسخه"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-input min-h-40",
                    "placeholder": "کاربرد قطعه، خرابی، ابعاد تقریبی، شرایط دمایی و هر نکته مهم را بنویسید.",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            profile = getattr(user, "customer_profile", None)
            full_name = user.get_full_name().strip()
            if profile:
                full_name = f"{profile.first_name} {profile.last_name}".strip() or full_name
                self.fields["phone"].initial = profile.phone
            self.fields["full_name"].initial = full_name

# BEGIN STORE COMMERCE PHASE 2
from .models import ProductReview, ProductVariant, ShippingMethod, StoreAddress, StoreOrder, StorePayment


class AddToCartForm(forms.Form):
    variant_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={"class": "form-input", "min": 1}))

    def __init__(self, *args, product=None, **kwargs):
        self.product = product
        super().__init__(*args, **kwargs)
        self.variant = None

    def clean(self):
        cleaned = super().clean()
        variant_id = cleaned.get("variant_id")
        quantity = cleaned.get("quantity")
        if not variant_id or not quantity:
            return cleaned
        try:
            variant = ProductVariant.objects.select_related("product").get(
                pk=variant_id,
                product=self.product,
                is_active=True,
            )
        except ProductVariant.DoesNotExist:
            raise forms.ValidationError("تنوع انتخاب‌شده معتبر نیست.")
        if variant.stock_status == "out_of_stock":
            raise forms.ValidationError("این تنوع در حال حاضر موجود نیست.")
        if quantity < variant.minimum_quantity:
            raise forms.ValidationError(f"حداقل تعداد سفارش {variant.minimum_quantity} عدد است.")
        if variant.maximum_quantity and quantity > variant.maximum_quantity:
            raise forms.ValidationError(f"حداکثر تعداد سفارش {variant.maximum_quantity} عدد است.")
        self.variant = variant
        return cleaned


class CheckoutForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=[("bank_transfer", "کارت به کارت / واریز بانکی")],
        widget=forms.RadioSelect,
        label="روش پرداخت",
    )
    save_address = forms.BooleanField(required=False, initial=True, label="ذخیره این آدرس برای خریدهای بعدی")

    class Meta:
        model = StoreOrder
        fields = [
            "shipping_method", "full_name", "phone", "email", "province", "city",
            "address", "postal_code", "customer_note",
        ]
        widgets = {
            "shipping_method": forms.Select(attrs={"class": "form-input"}),
            "full_name": forms.TextInput(attrs={"class": "form-input"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "09123456789"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "province": forms.TextInput(attrs={"class": "form-input"}),
            "city": forms.TextInput(attrs={"class": "form-input"}),
            "address": forms.Textarea(attrs={"class": "form-input min-h-28"}),
            "postal_code": forms.TextInput(attrs={"class": "form-input"}),
            "customer_note": forms.Textarea(attrs={"class": "form-input min-h-24"}),
        }

    def __init__(self, *args, user=None, subtotal=0, **kwargs):
        self.user = user
        self.subtotal = subtotal
        super().__init__(*args, **kwargs)
        self.fields["shipping_method"].queryset = ShippingMethod.objects.filter(is_active=True)
        if user and user.is_authenticated and not self.is_bound:
            address = StoreAddress.objects.filter(user=user, is_default=True).first()
            profile = getattr(user, "customer_profile", None)
            if address:
                for field in ["full_name", "phone", "province", "city", "address", "postal_code"]:
                    self.fields[field].initial = getattr(address, field)
            else:
                full_name = user.get_full_name().strip()
                if profile:
                    full_name = f"{profile.first_name} {profile.last_name}".strip() or full_name
                    self.fields["phone"].initial = profile.phone
                    self.fields["address"].initial = profile.address
                self.fields["full_name"].initial = full_name
                self.fields["email"].initial = user.email


class ManualPaymentForm(forms.ModelForm):
    class Meta:
        model = StorePayment
        fields = ["card_holder", "receipt_image", "note"]
        widgets = {
            "card_holder": forms.TextInput(attrs={"class": "form-input"}),
            "receipt_image": forms.ClearableFileInput(attrs={"class": "form-input", "accept": "image/*"}),
            "note": forms.Textarea(attrs={"class": "form-input min-h-24"}),
        }

    def clean_receipt_image(self):
        image = self.cleaned_data.get("receipt_image")
        if not image and not self.instance.receipt_image:
            raise forms.ValidationError("تصویر رسید پرداخت را بارگذاری کنید.")
        return image


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ["rating", "title", "body"]
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} ستاره") for i in range(5, 0, -1)], attrs={"class": "form-input"}),
            "title": forms.TextInput(attrs={"class": "form-input"}),
            "body": forms.Textarea(attrs={"class": "form-input min-h-32"}),
        }
# END STORE COMMERCE PHASE 2

# BEGIN CUSTOMER PORTAL PHASE 3 CHECKOUT FORM
from website.forms import IRAN_PROVINCES, normalize_digits


class CheckoutForm(forms.ModelForm):
    saved_address = forms.ModelChoiceField(
        required=False,
        queryset=StoreAddress.objects.none(),
        label="آدرس ذخیره‌شده",
        empty_label="ورود آدرس جدید",
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    payment_method = forms.ChoiceField(
        choices=[("bank_transfer", "کارت به کارت / واریز بانکی")],
        widget=forms.RadioSelect,
        label="روش پرداخت",
    )
    save_address = forms.BooleanField(required=False, initial=True, label="ذخیره این آدرس برای خریدهای بعدی")

    class Meta:
        model = StoreOrder
        fields = [
            "shipping_method", "full_name", "phone", "email", "province", "city",
            "address", "postal_code", "customer_note",
        ]
        widgets = {
            "shipping_method": forms.Select(attrs={"class": "form-input"}),
            "full_name": forms.TextInput(attrs={"class": "form-input"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "09123456789", "inputmode": "numeric"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "province": forms.Select(choices=IRAN_PROVINCES, attrs={"class": "form-input"}),
            "city": forms.TextInput(attrs={"class": "form-input"}),
            "address": forms.Textarea(attrs={"class": "form-input min-h-28"}),
            "postal_code": forms.TextInput(attrs={"class": "form-input", "inputmode": "numeric", "maxlength": "10"}),
            "customer_note": forms.Textarea(attrs={"class": "form-input min-h-24"}),
        }

    def __init__(self, *args, user=None, subtotal=0, **kwargs):
        self.user = user
        self.subtotal = subtotal
        super().__init__(*args, **kwargs)
        self.fields["shipping_method"].queryset = ShippingMethod.objects.filter(is_active=True)
        if user and user.is_authenticated:
            self.fields["saved_address"].queryset = StoreAddress.objects.filter(user=user)
            if self.is_bound and self.data.get("saved_address"):
                for field_name in ["full_name", "phone", "province", "city", "address", "postal_code"]:
                    self.fields[field_name].required = False
            if not self.is_bound:
                saved = StoreAddress.objects.filter(user=user, is_default=True).first()
                profile = getattr(user, "customer_profile", None)
                if saved:
                    self.fields["saved_address"].initial = saved
                    self._set_address_initial(saved)
                else:
                    self.fields["full_name"].initial = user.get_full_name().strip()
                    self.fields["email"].initial = user.email
                    if profile:
                        self.fields["full_name"].initial = f"{profile.first_name} {profile.last_name}".strip()
                        self.fields["phone"].initial = profile.phone

    def _set_address_initial(self, saved):
        for field in ["full_name", "phone", "province", "city", "address", "postal_code"]:
            self.fields[field].initial = getattr(saved, field)

    def clean_phone(self):
        value = normalize_digits(self.cleaned_data.get("phone"))
        if len(value) != 11 or not value.startswith("09"):
            raise forms.ValidationError("شماره تماس معتبر نیست.")
        return value

    def clean_postal_code(self):
        value = normalize_digits(self.cleaned_data.get("postal_code"))
        if len(value) != 10 or not value.isdigit():
            raise forms.ValidationError("کد پستی باید دقیقاً ۱۰ رقم باشد.")
        return value

    def clean(self):
        cleaned = super().clean()
        saved = cleaned.get("saved_address")
        if saved and saved.user_id == getattr(self.user, "id", None):
            cleaned["full_name"] = saved.full_name
            cleaned["phone"] = saved.phone
            cleaned["province"] = saved.province
            cleaned["city"] = saved.city
            parts = [saved.address]
            if saved.district:
                parts.append(f"محله {saved.district}")
            if saved.plaque:
                parts.append(f"پلاک {saved.plaque}")
            if saved.unit:
                parts.append(f"واحد {saved.unit}")
            cleaned["address"] = "، ".join(parts)
            cleaned["postal_code"] = saved.postal_code
        return cleaned
# END CUSTOMER PORTAL PHASE 3 CHECKOUT FORM
