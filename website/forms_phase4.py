from __future__ import annotations
import re
from django import forms
from .models import CustomerProfile
from store.models import StoreAddress
from .iran_locations import IRAN_LOCATIONS, PROVINCE_CHOICES
from .jalali import format_jalali, normalize_digits, parse_jalali_date

THEME_CHOICES = [
    ("original", "نارنجی، مشکی و نقره‌ای اصلی"),
    ("brand-gold", "طلایی و سرمه‌ای"),
    ("hybrid", "ترکیبی نارنجی و سرمه‌ای"),
]

def validate_national_code(value):
    value = normalize_digits(value)
    if not value:
        return ""
    if not re.fullmatch(r"\d{10}", value) or len(set(value)) == 1:
        raise forms.ValidationError("کد ملی باید ۱۰ رقم معتبر باشد.")
    check = int(value[-1])
    remainder = sum(int(value[i]) * (10 - i) for i in range(9)) % 11
    expected = remainder if remainder < 2 else 11 - remainder
    if check != expected:
        raise forms.ValidationError("کد ملی واردشده معتبر نیست.")
    return value

class CustomerProfileForm(forms.ModelForm):
    email = forms.EmailField(required=False, label="ایمیل", widget=forms.EmailInput(attrs={"class":"form-input","placeholder":"name@example.com"}))
    birth_date_jalali = forms.CharField(
        required=False,
        label="تاریخ تولد شمسی",
        widget=forms.TextInput(attrs={
            "class":"form-input", "data-jdp":"", "data-jdp-max-date":"today",
            "data-jdp-target-value-input":"#id_birth_date", "data-jdp-target-value-type":"gregorian",
            "placeholder":"مثلاً 1358/09/28", "autocomplete":"off",
        }),
    )
    birth_date = forms.DateField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = CustomerProfile
        fields = ["avatar","first_name","last_name","father_name","birth_date_jalali","birth_date","gender","phone","email","national_code","landline","occupation","company_name"]
        widgets = {
            "avatar": forms.ClearableFileInput(attrs={"class":"form-input","accept":"image/jpeg,image/png,image/webp"}),
            "first_name": forms.TextInput(attrs={"class":"form-input","autocomplete":"given-name"}),
            "last_name": forms.TextInput(attrs={"class":"form-input","autocomplete":"family-name"}),
            "father_name": forms.TextInput(attrs={"class":"form-input"}),
            "gender": forms.Select(attrs={"class":"form-input"}),
            "phone": forms.TextInput(attrs={"class":"form-input","inputmode":"numeric","placeholder":"09123456789"}),
            "national_code": forms.TextInput(attrs={"class":"form-input","inputmode":"numeric","maxlength":"10"}),
            "landline": forms.TextInput(attrs={"class":"form-input","inputmode":"tel","placeholder":"031..."}),
            "occupation": forms.TextInput(attrs={"class":"form-input","placeholder":"شغل یا سمت"}),
            "company_name": forms.TextInput(attrs={"class":"form-input","placeholder":"اختیاری"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["email"].initial = self.instance.user.email
            self.fields["birth_date_jalali"].initial = format_jalali(self.instance.birth_date, numeric=True)

    def clean_phone(self):
        phone = normalize_digits(self.cleaned_data.get("phone"))
        if not re.fullmatch(r"09\d{9}", phone):
            raise forms.ValidationError("شماره موبایل باید با 09 شروع شود و ۱۱ رقم باشد.")
        if CustomerProfile.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("این شماره موبایل قبلاً استفاده شده است.")
        return phone

    def clean_national_code(self):
        return validate_national_code(self.cleaned_data.get("national_code"))

    def clean_birth_date_jalali(self):
        raw = self.cleaned_data.get("birth_date_jalali")
        if not raw:
            return ""
        try:
            parse_jalali_date(raw)
        except ValueError as exc:
            raise forms.ValidationError(str(exc))
        return normalize_digits(raw)

    def clean(self):
        cleaned = super().clean()
        jalali_value = cleaned.get("birth_date_jalali")
        if jalali_value:
            cleaned["birth_date"] = parse_jalali_date(jalali_value)
        return cleaned

    def clean_landline(self):
        return normalize_digits(self.cleaned_data.get("landline"))

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar and getattr(avatar, "size", 0) > 3 * 1024 * 1024:
            raise forms.ValidationError("حجم تصویر پروفایل نباید بیشتر از ۳ مگابایت باشد.")
        return avatar

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.birth_date = self.cleaned_data.get("birth_date")
        if commit:
            profile.save()
            self.save_m2m()
        user = profile.user
        user.first_name, user.last_name = profile.first_name, profile.last_name
        user.username, user.email = profile.phone, self.cleaned_data.get("email", "")
        user.save(update_fields=["first_name","last_name","username","email"])
        return profile

class StoreAddressForm(forms.ModelForm):
    class Meta:
        model = StoreAddress
        fields = ["title","full_name","phone","recipient_national_code","province","city","district","address","plaque","unit","postal_code","delivery_notes","is_default"]
        widgets = {
            "title": forms.TextInput(attrs={"class":"form-input","placeholder":"مثلاً منزل یا محل کار"}),
            "full_name": forms.TextInput(attrs={"class":"form-input","autocomplete":"name"}),
            "phone": forms.TextInput(attrs={"class":"form-input","inputmode":"numeric"}),
            "recipient_national_code": forms.TextInput(attrs={"class":"form-input","inputmode":"numeric","maxlength":"10"}),
            "province": forms.Select(attrs={"class":"form-input","data-iran-province":"1"}),
            "city": forms.Select(attrs={"class":"form-input","data-iran-city":"1","data-city-endpoint":"/customer/locations/cities/"}),
            "district": forms.TextInput(attrs={"class":"form-input","placeholder":"منطقه یا محله"}),
            "address": forms.Textarea(attrs={"class":"form-input min-h-28","placeholder":"خیابان، کوچه و نشانی کامل"}),
            "plaque": forms.TextInput(attrs={"class":"form-input","inputmode":"numeric"}),
            "unit": forms.TextInput(attrs={"class":"form-input","inputmode":"numeric"}),
            "postal_code": forms.TextInput(attrs={"class":"form-input","inputmode":"numeric","maxlength":"10","required":"required","placeholder":"کد پستی ۱۰ رقمی"}),
            "delivery_notes": forms.Textarea(attrs={"class":"form-input min-h-20","placeholder":"توضیحات لازم برای تحویل"}),
            "is_default": forms.CheckboxInput(attrs={"class":"h-5 w-5 accent-orange-500"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["province"].choices = PROVINCE_CHOICES
        province = (self.data.get("province") if self.is_bound else getattr(self.instance, "province", "")) or ""
        selected_city = (self.data.get("city") if self.is_bound else getattr(self.instance, "city", "")) or ""
        city_choices = [("", "ابتدا استان را انتخاب کنید")]
        if province in IRAN_LOCATIONS:
            city_choices = [("", "انتخاب شهر")] + [(city, city) for city in IRAN_LOCATIONS[province]]
        if selected_city and selected_city not in dict(city_choices):
            city_choices.append((selected_city, selected_city))
        self.fields["city"].choices = city_choices
        self.fields["postal_code"].required = True

    def clean_phone(self):
        phone = normalize_digits(self.cleaned_data.get("phone"))
        if not re.fullmatch(r"09\d{9}", phone):
            raise forms.ValidationError("شماره تحویل‌گیرنده باید ۱۱ رقم و با 09 شروع شود.")
        return phone

    def clean_postal_code(self):
        value = normalize_digits(self.cleaned_data.get("postal_code"))
        if not re.fullmatch(r"\d{10}", value):
            raise forms.ValidationError("کد پستی الزامی است و باید دقیقاً ۱۰ رقم باشد.")
        if value.startswith("0"):
            raise forms.ValidationError("کد پستی معتبر نباید با صفر شروع شود.")
        return value

    def clean_recipient_national_code(self):
        value = self.cleaned_data.get("recipient_national_code")
        return validate_national_code(value) if value else ""

    def clean(self):
        cleaned = super().clean()
        province, city = cleaned.get("province"), cleaned.get("city")
        if province not in IRAN_LOCATIONS:
            self.add_error("province", "استان انتخاب‌شده معتبر نیست.")
        elif city not in IRAN_LOCATIONS[province]:
            self.add_error("city", "شهر انتخاب‌شده مربوط به این استان نیست.")
        return cleaned

class AppearancePreferenceForm(forms.ModelForm):
    theme_preference = forms.ChoiceField(choices=THEME_CHOICES, widget=forms.RadioSelect)
    class Meta:
        model = CustomerProfile
        fields = ["theme_preference"]
