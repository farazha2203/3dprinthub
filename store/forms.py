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

# BEGIN STORE OPERATIONS PHASE 6 FORMS
from .models import ReturnRequest
from website.iran_locations import IRAN_LOCATIONS
from website.models import IranCity, IranCounty, IranProvince


class CheckoutOperationsForm(forms.Form):
    saved_address = forms.ModelChoiceField(
        required=False,
        queryset=StoreAddress.objects.none(),
        label="آدرس ذخیره‌شده",
        empty_label="ورود آدرس جدید",
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    shipping_method = forms.ModelChoiceField(
        queryset=ShippingMethod.objects.none(),
        label="روش ارسال",
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    full_name = forms.CharField(label="نام تحویل‌گیرنده", max_length=150, widget=forms.TextInput(attrs={"class":"form-input"}))
    phone = forms.CharField(label="شماره تماس", max_length=20, widget=forms.TextInput(attrs={"class":"form-input","inputmode":"numeric","placeholder":"09123456789"}))
    email = forms.EmailField(required=False, label="ایمیل", widget=forms.EmailInput(attrs={"class":"form-input"}))
    province = forms.ChoiceField(required=False, label="استان", widget=forms.Select(attrs={"class":"form-input","data-iran-province":"1"}))
    county = forms.ChoiceField(required=False, label="شهرستان", widget=forms.Select(attrs={"class":"form-input","data-iran-county":"1","data-county-endpoint":"/customer/locations/counties/"}))
    city = forms.ChoiceField(required=False, label="شهر", widget=forms.Select(attrs={"class":"form-input","data-iran-city":"1","data-city-endpoint":"/customer/locations/cities-v2/"}))
    address = forms.CharField(required=False, label="نشانی کامل", widget=forms.Textarea(attrs={"class":"form-input min-h-28"}))
    postal_code = forms.CharField(required=False, label="کد پستی", max_length=10, widget=forms.TextInput(attrs={"class":"form-input","inputmode":"numeric","maxlength":"10"}))
    customer_note = forms.CharField(required=False, label="توضیحات سفارش", widget=forms.Textarea(attrs={"class":"form-input min-h-24"}))
    coupon_code = forms.CharField(required=False, label="کد تخفیف", max_length=50, widget=forms.TextInput(attrs={"class":"form-input","placeholder":"در صورت داشتن کد وارد کنید","autocomplete":"off"}))
    payment_method = forms.ChoiceField(choices=[("bank_transfer", "کارت به کارت / واریز بانکی")], widget=forms.RadioSelect, label="روش پرداخت")
    save_address = forms.BooleanField(required=False, initial=True, label="ذخیره این آدرس برای خریدهای بعدی")

    def __init__(self, *args, user=None, subtotal=0, **kwargs):
        self.user = user
        self.subtotal = subtotal
        super().__init__(*args, **kwargs)
        self.fields["shipping_method"].queryset = ShippingMethod.objects.filter(is_active=True)
        if user and user.is_authenticated:
            self.fields["saved_address"].queryset = StoreAddress.objects.filter(user=user)

        saved = None
        if user and user.is_authenticated:
            raw_saved = self.data.get("saved_address") if self.is_bound else None
            if raw_saved:
                saved = StoreAddress.objects.filter(user=user, pk=raw_saved).first()
            elif not self.is_bound:
                saved = StoreAddress.objects.filter(user=user, is_default=True).first()
                if saved:
                    self.fields["saved_address"].initial = saved

        province = (self.data.get("province") if self.is_bound else getattr(saved, "province", "")) or ""
        county = (self.data.get("county") if self.is_bound else getattr(saved, "county", "")) or ""
        city = (self.data.get("city") if self.is_bound else getattr(saved, "city", "")) or ""
        provinces = list(IranProvince.objects.filter(is_active=True).values_list("name", flat=True)) or list(IRAN_LOCATIONS.keys())
        self.fields["province"].choices = [("", "انتخاب استان")] + [(x, x) for x in sorted(set(provinces))]
        counties = list(IranCounty.objects.filter(province__name=province, is_active=True).values_list("name", flat=True)) if province else []
        if province and not counties:
            counties = IRAN_LOCATIONS.get(province, [])
        self.fields["county"].choices = [("", "ابتدا استان را انتخاب کنید" if not province else "انتخاب شهرستان")] + [(x, x) for x in sorted(set(counties))]
        cities = list(IranCity.objects.filter(province__name=province, county__name=county, is_active=True).values_list("name", flat=True)) if province and county else []
        if province and county and not cities and county in IRAN_LOCATIONS.get(province, []):
            cities = [county]
        self.fields["city"].choices = [("", "ابتدا شهرستان را انتخاب کنید" if not county else "انتخاب شهر")] + [(x, x) for x in sorted(set(cities))]
        for name, selected in (("province", province), ("county", county), ("city", city)):
            if selected and selected not in dict(self.fields[name].choices):
                self.fields[name].choices.append((selected, selected))

        if saved and not self.is_bound:
            for name in ("full_name", "phone", "province", "county", "city", "address", "postal_code"):
                self.fields[name].initial = getattr(saved, name, "")
        elif user and user.is_authenticated and not self.is_bound:
            profile = getattr(user, "customer_profile", None)
            self.fields["full_name"].initial = user.get_full_name().strip()
            self.fields["email"].initial = user.email
            if profile:
                self.fields["full_name"].initial = f"{profile.first_name} {profile.last_name}".strip()
                self.fields["phone"].initial = profile.phone

    def clean_phone(self):
        value = normalize_digits(self.cleaned_data.get("phone", ""))
        if len(value) != 11 or not value.startswith("09"):
            raise forms.ValidationError("شماره موبایل معتبر نیست.")
        return value

    def clean_postal_code(self):
        value = normalize_digits(self.cleaned_data.get("postal_code", ""))
        if self.cleaned_data.get("saved_address"):
            return value
        if len(value) != 10 or not value.isdigit() or value.startswith("0"):
            raise forms.ValidationError("کد پستی باید ۱۰ رقم و بدون صفر ابتدایی باشد.")
        return value

    def clean_coupon_code(self):
        return (self.cleaned_data.get("coupon_code") or "").strip().upper()

    def clean(self):
        cleaned = super().clean()
        saved = cleaned.get("saved_address")
        if saved:
            if saved.user_id != getattr(self.user, "id", None):
                raise forms.ValidationError("آدرس انتخاب‌شده متعلق به این حساب نیست.")
            return cleaned
        province, county, city = cleaned.get("province"), cleaned.get("county"), cleaned.get("city")
        if province and city and not county:
            if IranProvince.objects.exists():
                matches = list(IranCity.objects.filter(province__name=province, name=city, is_active=True).select_related("county")[:2])
                if len(matches) == 1:
                    county = matches[0].county.name
                    cleaned["county"] = county
            elif province in IRAN_LOCATIONS and city in IRAN_LOCATIONS.get(province, []):
                county = city
                cleaned["county"] = county
        required = ("full_name", "phone", "province", "county", "city", "address", "postal_code")
        for name in required:
            if not cleaned.get(name):
                self.add_error(name, "این فیلد الزامی است.")
        if IranProvince.objects.exists() and province and county and city:
            province_obj = IranProvince.objects.filter(name=province, is_active=True).first()
            county_obj = IranCounty.objects.filter(province=province_obj, name=county, is_active=True).first() if province_obj else None
            city_ok = IranCity.objects.filter(province=province_obj, county=county_obj, name=city, is_active=True).exists() if county_obj else False
            if not province_obj:
                self.add_error("province", "استان انتخاب‌شده معتبر نیست.")
            elif not county_obj:
                self.add_error("county", "شهرستان انتخاب‌شده مربوط به این استان نیست.")
            elif not city_ok:
                self.add_error("city", "شهر انتخاب‌شده مربوط به این شهرستان نیست.")
        return cleaned


CheckoutForm = CheckoutOperationsForm


class ReturnRequestForm(forms.ModelForm):
    class Meta:
        model = ReturnRequest
        fields = ["item", "reason", "description", "image"]
        widgets = {
            "item": forms.Select(attrs={"class":"form-input"}),
            "reason": forms.Select(attrs={"class":"form-input"}),
            "description": forms.Textarea(attrs={"class":"form-input min-h-36","placeholder":"شرح دقیق مشکل و شرایط کالا را بنویسید."}),
            "image": forms.ClearableFileInput(attrs={"class":"form-input","accept":"image/jpeg,image/png,image/webp"}),
        }

    def __init__(self, *args, order=None, **kwargs):
        self.order = order
        super().__init__(*args, **kwargs)
        self.fields["item"].queryset = order.items.all() if order else StoreOrder.objects.none()
        self.fields["item"].required = False
# END STORE OPERATIONS PHASE 6 FORMS

# BEGIN AFFILIATE PARTNER PROGRAM PHASE 7 FORMS
import re

from .models import AffiliateCampaign, AffiliatePartner, AffiliateTier, generate_affiliate_code


class AffiliatePartnerApplicationForm(forms.ModelForm):
    class Meta:
        model = AffiliatePartner
        fields = [
            "partner_type", "display_name", "company_name", "website", "channel",
            "description", "code", "sheba_number", "card_number", "account_holder", "terms_accepted",
        ]
        widgets = {
            "partner_type": forms.Select(attrs={"class": "form-input"}),
            "display_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "نام شخص، مجموعه یا رسانه"}),
            "company_name": forms.TextInput(attrs={"class": "form-input"}),
            "website": forms.URLInput(attrs={"class": "form-input", "placeholder": "https://example.com"}),
            "channel": forms.TextInput(attrs={"class": "form-input", "placeholder": "اینستاگرام، تلگرام، وب‌سایت یا شبکه فروش"}),
            "description": forms.Textarea(attrs={"class": "form-input min-h-28", "placeholder": "روش معرفی مشتری و زمینه همکاری را توضیح دهید."}),
            "code": forms.TextInput(attrs={"class": "form-input", "dir": "ltr", "placeholder": "مثلاً FARAZ3D"}),
            "sheba_number": forms.TextInput(attrs={"class": "form-input", "dir": "ltr", "placeholder": "IR000000000000000000000000"}),
            "card_number": forms.TextInput(attrs={"class": "form-input", "dir": "ltr", "placeholder": "شماره کارت ۱۶ رقمی"}),
            "account_holder": forms.TextInput(attrs={"class": "form-input"}),
            "terms_accepted": forms.CheckboxInput(),
        }
        labels = {"terms_accepted": "قوانین همکاری، محاسبه پورسانت و تسویه را می‌پذیرم"}

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["code"].required = False
        if not self.instance.pk and user:
            self.fields["display_name"].initial = user.get_full_name().strip() or user.username

    def clean_code(self):
        code = (self.cleaned_data.get("code") or "").strip().upper()
        if not code:
            return generate_affiliate_code()
        if not re.fullmatch(r"[A-Z0-9_-]{4,30}", code):
            raise forms.ValidationError("کد معرف باید ۴ تا ۳۰ کاراکتر انگلیسی، عدد، خط تیره یا زیرخط باشد.")
        qs = AffiliatePartner.objects.filter(code__iexact=code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("این کد معرف قبلاً استفاده شده است.")
        return code

    def clean_sheba_number(self):
        value = normalize_digits(self.cleaned_data.get("sheba_number", "")).replace(" ", "").upper()
        if value and not re.fullmatch(r"IR\d{24}", value):
            raise forms.ValidationError("شماره شبا باید با IR شروع شود و پس از آن ۲۴ رقم داشته باشد.")
        return value

    def clean_card_number(self):
        value = normalize_digits(self.cleaned_data.get("card_number", "")).replace("-", "").replace(" ", "")
        if value and not re.fullmatch(r"\d{16}", value):
            raise forms.ValidationError("شماره کارت باید ۱۶ رقمی باشد.")
        return value

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("terms_accepted"):
            self.add_error("terms_accepted", "پذیرش قوانین همکاری الزامی است.")
        if not cleaned.get("sheba_number") and not cleaned.get("card_number"):
            raise forms.ValidationError("برای تسویه حداقل شماره شبا یا شماره کارت را وارد کنید.")
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.user:
            obj.user = self.user
        if not obj.tier_id:
            tier = AffiliateTier.objects.filter(is_active=True).order_by("id").first()
            if not tier:
                tier = AffiliateTier.objects.create(name="همکار پایه", slug="default", commission_value=5)
            obj.tier = tier
        if obj.pk and obj.status == "rejected":
            obj.status = "pending"
        if commit:
            obj.save()
        return obj


class AffiliateCampaignForm(forms.ModelForm):
    class Meta:
        model = AffiliateCampaign
        fields = ["name", "slug", "target_path", "utm_source", "utm_medium", "utm_campaign", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "slug": forms.TextInput(attrs={"class": "form-input", "dir": "ltr"}),
            "target_path": forms.TextInput(attrs={"class": "form-input", "dir": "ltr", "placeholder": "/store/ یا /store/product/.../"}),
            "utm_source": forms.TextInput(attrs={"class": "form-input", "dir": "ltr"}),
            "utm_medium": forms.TextInput(attrs={"class": "form-input", "dir": "ltr"}),
            "utm_campaign": forms.TextInput(attrs={"class": "form-input", "dir": "ltr"}),
            "is_active": forms.CheckboxInput(),
        }

    def __init__(self, *args, partner=None, **kwargs):
        self.partner = partner
        super().__init__(*args, **kwargs)

    def clean_slug(self):
        slug = (self.cleaned_data.get("slug") or "").strip()
        qs = AffiliateCampaign.objects.filter(partner=self.partner, slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("این شناسه کمپین قبلاً استفاده شده است.")
        return slug

    def clean_target_path(self):
        path = (self.cleaned_data.get("target_path") or "/").strip()
        if not path.startswith("/") or path.startswith("//"):
            raise forms.ValidationError("مقصد باید یک مسیر داخلی سایت باشد و با / شروع شود.")
        return path

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.partner = self.partner
        if commit:
            obj.save()
        return obj


class AffiliatePayoutRequestForm(forms.Form):
    note = forms.CharField(required=False, label="توضیحات درخواست", widget=forms.Textarea(attrs={"class": "form-input min-h-24", "placeholder": "توضیح اختیاری برای واحد مالی"}))
# END AFFILIATE PARTNER PROGRAM PHASE 7 FORMS

# BEGIN PHASE 23 RESILIENT CATALOG AND LINK INTELLIGENCE FORMS
import re
from decimal import Decimal

from website.models import Material

from .link_intelligence import normalize_public_url


class ExternalLinkSubmitForm(forms.Form):
    source_url = forms.CharField(
        label="لینک محصول یا مدل",
        max_length=2000,
        widget=forms.URLInput(attrs={
            "class": "form-input",
            "placeholder": "https://example.com/model/...",
            "inputmode": "url",
            "autocomplete": "url",
        }),
        help_text="لینک عمومی محصول، مدل یا صفحه فایل را وارد کنید. نبود لینک مستقیم STL مانع تحلیل نیست.",
    )

    def clean_source_url(self):
        return normalize_public_url(self.cleaned_data["source_url"], resolve_dns=False)


class ExternalLinkEstimateForm(forms.Form):
    material = forms.ModelChoiceField(
        label="متریال پیشنهادی",
        queryset=Material.objects.none(),
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    estimated_weight_grams = forms.DecimalField(
        label="وزن تقریبی هر قطعه (گرم)",
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
        widget=forms.NumberInput(attrs={"class": "form-input", "min": "0.01", "step": "0.01"}),
    )
    estimated_print_minutes = forms.IntegerField(
        label="زمان تقریبی چاپ هر قطعه (دقیقه)",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-input", "min": "1"}),
    )
    quantity = forms.IntegerField(
        label="تعداد",
        min_value=1,
        max_value=1000,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-input", "min": "1", "max": "1000"}),
    )
    full_name = forms.CharField(
        label="نام و نام خانوادگی",
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "autocomplete": "name"}),
    )
    phone = forms.CharField(
        label="شماره تماس",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "inputmode": "tel", "autocomplete": "tel"}),
    )

    def __init__(self, *args, analysis=None, user=None, require_customer=False, **kwargs):
        self.analysis = analysis
        self.require_customer = bool(require_customer)
        super().__init__(*args, **kwargs)
        self.fields["material"].queryset = Material.objects.filter(is_active=True).order_by("sort_order", "name")
        self.fields["full_name"].required = self.require_customer
        self.fields["phone"].required = self.require_customer
        if analysis and not self.is_bound:
            self.initial.update({
                "material": analysis.material_id,
                "estimated_weight_grams": analysis.estimated_weight_grams,
                "estimated_print_minutes": analysis.estimated_print_minutes,
                "quantity": analysis.quantity or 1,
            })
        if analysis and analysis.has_authoritative_pricing_inputs:
            self.fields["estimated_weight_grams"].disabled = True
            self.fields["estimated_print_minutes"].disabled = True
            self.fields["estimated_weight_grams"].help_text = "وزن از منبع معتبر یا اپراتور دریافت شده و توسط مشتری قابل تغییر نیست."
            self.fields["estimated_print_minutes"].help_text = "زمان چاپ معتبر است؛ زمان قابل محاسبه طبق پله ساعتی رو به بالا گرد می‌شود."
        if analysis and analysis.pricing_locked:
            self.fields["material"].disabled = True
        if user and getattr(user, "is_authenticated", False) and not self.is_bound:
            profile = getattr(user, "customer_profile", None)
            full_name = user.get_full_name().strip()
            if profile:
                full_name = f"{profile.first_name} {profile.last_name}".strip() or full_name
                self.initial["phone"] = profile.phone
            self.initial.setdefault("full_name", full_name or user.username)
            self.initial.setdefault("phone", "")

    def clean_full_name(self):
        value = str(self.cleaned_data.get("full_name") or "").strip()
        if self.require_customer and len(value) < 3:
            raise forms.ValidationError("نام و نام خانوادگی را وارد کنید.")
        return value[:200]

    def clean_phone(self):
        value = str(self.cleaned_data.get("phone") or "").strip()
        if not value and not self.require_customer:
            return ""
        normalized = value.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
        normalized = re.sub(r"[^0-9+]", "", normalized)
        if len(re.sub(r"\D", "", normalized)) < 10:
            raise forms.ValidationError("شماره تماس معتبر وارد کنید.")
        return normalized[:20]


class CatalogRefreshRequestForm(forms.Form):
    customer_note = forms.CharField(
        required=False,
        max_length=500,
        label="چه چیزی بروزرسانی شود؟",
        widget=forms.Textarea(attrs={
            "class": "form-input",
            "rows": 3,
            "placeholder": "مثلاً وزن، فایل جدید، تصاویر یا مشخصات چاپ",
        }),
    )
# END PHASE 23 RESILIENT CATALOG AND LINK INTELLIGENCE FORMS

# BEGIN PHASE 28 AUTHENTICATED CONVERSION AND MANUAL QUOTE
class ExternalLinkManualQuoteForm(forms.Form):
    full_name = forms.CharField(
        label="نام و نام خانوادگی",
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-input", "autocomplete": "name"}),
    )
    phone = forms.CharField(
        label="شماره تماس",
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-input", "inputmode": "tel", "autocomplete": "tel"}),
    )
    quantity = forms.IntegerField(
        label="تعداد موردنیاز",
        min_value=1,
        max_value=1000,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-input", "min": "1", "max": "1000"}),
    )
    desired_material = forms.ModelChoiceField(
        label="متریال ترجیحی",
        queryset=Material.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    customer_note = forms.CharField(
        label="توضیحات برای قیمت‌گذاری",
        max_length=1500,
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-input",
            "rows": 4,
            "placeholder": "کاربرد قطعه، ابعاد، رنگ، استحکام، تعداد و زمان تحویل را بنویسید.",
        }),
    )

    def __init__(self, *args, analysis=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["desired_material"].queryset = Material.objects.filter(is_active=True).order_by("sort_order", "name")
        if analysis and not self.is_bound:
            self.initial["quantity"] = analysis.quantity or 1
            self.initial["desired_material"] = analysis.material_id
        if user and getattr(user, "is_authenticated", False) and not self.is_bound:
            profile = getattr(user, "customer_profile", None)
            name = user.get_full_name().strip()
            phone = ""
            if profile:
                name = f"{profile.first_name} {profile.last_name}".strip() or name
                phone = profile.phone or ""
            self.initial["full_name"] = name or user.username
            self.initial["phone"] = phone

    def clean_phone(self):
        value = str(self.cleaned_data.get("phone") or "").strip()
        normalized = value.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
        normalized = re.sub(r"[^0-9+]", "", normalized)
        if len(re.sub(r"\D", "", normalized)) < 10:
            raise forms.ValidationError("شماره تماس معتبر وارد کنید.")
        return normalized[:20]
# END PHASE 28 AUTHENTICATED CONVERSION AND MANUAL QUOTE
