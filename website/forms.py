from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


from .models import Order, Material, CustomerProfile, OrderReview


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "first_name",
            "last_name",
            "phone",
            "service_type",
            "material",
            "color",
            "quantity",
            "description",
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "نام",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "نام خانوادگی",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "مثلاً 09123456789",
            }),
            "service_type": forms.Select(attrs={
                "class": "form-input",
            }),
            "material": forms.Select(attrs={
                "class": "form-input",
            }),
            "color": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "مثلاً مشکی، سفید، خاکستری، نارنجی و...",
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-input",
                "min": "1",
                "placeholder": "تعداد",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-input min-h-36",
                "placeholder": "توضیحات قطعه، ابعاد، کاربرد، شرایط کاری، دما، فشار، تعداد و هر نکته مهم دیگر...",
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["material"].queryset = Material.objects.filter(is_active=True)
        self.fields["material"].empty_label = "متریال موردنظر را انتخاب کنید"

        if user and user.is_authenticated:
            profile = getattr(user, "customer_profile", None)

            if profile:
                self.fields["first_name"].initial = profile.first_name or user.first_name
                self.fields["last_name"].initial = profile.last_name or user.last_name
                self.fields["phone"].initial = profile.phone
            else:
                self.fields["first_name"].initial = user.first_name
                self.fields["last_name"].initial = user.last_name


class CustomerRegisterForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        label="نام",
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "نام",
        })
    )

    last_name = forms.CharField(
        max_length=100,
        label="نام خانوادگی",
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "نام خانوادگی",
        })
    )

    phone = forms.CharField(
        max_length=20,
        label="شماره تماس",
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "مثلاً 09123456789",
        })
    )

    email = forms.EmailField(
        label="ایمیل",
        widget=forms.EmailInput(attrs={
            "class": "form-input",
            "placeholder": "برای ورود و بازیابی رمز عبور",
            "autocomplete": "email",
        })
    )

    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "رمز عبور",
        })
    )

    password_confirm = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "تکرار رمز عبور",
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()

        if User.objects.filter(username=phone).exists():
            raise forms.ValidationError("با این شماره تماس قبلاً حساب کاربری ساخته شده است.")

        return phone

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("با این ایمیل قبلاً حساب کاربری ساخته شده است.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("رمز عبور و تکرار آن یکسان نیستند.")

        return cleaned_data

    def save(self):
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        phone = self.cleaned_data["phone"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]

        user = User.objects.create_user(
            username=phone,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        CustomerProfile.objects.create(
            user=user,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
        )

        Order.objects.filter(phone=phone, customer__isnull=True).update(customer=user)

        return user


class CustomerLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="شماره تماس یا ایمیل",
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "شماره تماس یا ایمیل",
            "autocomplete": "username",
        })
    )

    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "رمز عبور",
            "autocomplete": "current-password",
        })
    )

    def clean(self):
        identifier = (self.cleaned_data.get("username") or "").strip()
        if "@" in identifier:
            user = User.objects.filter(email__iexact=identifier).only("username").first()
            if user is not None:
                self.cleaned_data["username"] = user.username
        return super().clean()


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = [
            "first_name",
            "last_name",
            "phone",
            "company_name",
            "national_code",
            "address",
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-input",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-input",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-input",
            }),
            "company_name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "اختیاری",
            }),
            "national_code": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "اختیاری",
            }),
            "address": forms.Textarea(attrs={
                "class": "form-input min-h-32",
                "placeholder": "آدرس جهت ارسال سفارش",
            }),
        }

class OrderReviewForm(forms.ModelForm):
    class Meta:
        model = OrderReview
        fields = ["rating", "comment"]

        widgets = {
            "rating": forms.Select(attrs={
                "class": "form-input",
            }),
            "comment": forms.Textarea(attrs={
                "class": "form-input min-h-32",
                "placeholder": "تجربه خود از کیفیت ساخت، زمان تحویل، دقت قطعه و پشتیبانی را بنویسید...",
            }),
        }

# BEGIN CUSTOMER PORTAL PHASE 3 FORMS
import re

from store.models import StoreAddress


IRAN_PROVINCES = [
    ("", "انتخاب استان"),
    ("آذربایجان شرقی", "آذربایجان شرقی"), ("آذربایجان غربی", "آذربایجان غربی"),
    ("اردبیل", "اردبیل"), ("اصفهان", "اصفهان"), ("البرز", "البرز"),
    ("ایلام", "ایلام"), ("بوشهر", "بوشهر"), ("تهران", "تهران"),
    ("چهارمحال و بختیاری", "چهارمحال و بختیاری"), ("خراسان جنوبی", "خراسان جنوبی"),
    ("خراسان رضوی", "خراسان رضوی"), ("خراسان شمالی", "خراسان شمالی"),
    ("خوزستان", "خوزستان"), ("زنجان", "زنجان"), ("سمنان", "سمنان"),
    ("سیستان و بلوچستان", "سیستان و بلوچستان"), ("فارس", "فارس"),
    ("قزوین", "قزوین"), ("قم", "قم"), ("کردستان", "کردستان"),
    ("کرمان", "کرمان"), ("کرمانشاه", "کرمانشاه"),
    ("کهگیلویه و بویراحمد", "کهگیلویه و بویراحمد"), ("گلستان", "گلستان"),
    ("گیلان", "گیلان"), ("لرستان", "لرستان"), ("مازندران", "مازندران"),
    ("مرکزی", "مرکزی"), ("هرمزگان", "هرمزگان"), ("همدان", "همدان"), ("یزد", "یزد"),
]

_PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize_digits(value):
    return (value or "").translate(_PERSIAN_DIGITS).strip()


def validate_national_code_value(value):
    value = normalize_digits(value)
    if not value:
        return value
    if not re.fullmatch(r"\d{10}", value) or len(set(value)) == 1:
        raise forms.ValidationError("کد ملی باید ۱۰ رقم معتبر باشد.")
    check = int(value[-1])
    remainder = sum(int(value[i]) * (10 - i) for i in range(9)) % 11
    expected = remainder if remainder < 2 else 11 - remainder
    if check != expected:
        raise forms.ValidationError("کد ملی واردشده معتبر نیست.")
    return value


class CustomerProfileForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        label="ایمیل",
        widget=forms.EmailInput(attrs={"class": "form-input", "placeholder": "name@example.com"}),
    )

    class Meta:
        model = CustomerProfile
        fields = [
            "avatar", "first_name", "last_name", "father_name", "birth_date", "gender",
            "phone", "email", "national_code", "landline", "occupation", "company_name",
        ]
        widgets = {
            "avatar": forms.ClearableFileInput(attrs={"class": "form-input", "accept": "image/jpeg,image/png,image/webp"}),
            "first_name": forms.TextInput(attrs={"class": "form-input", "autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"class": "form-input", "autocomplete": "family-name"}),
            "father_name": forms.TextInput(attrs={"class": "form-input"}),
            "birth_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "gender": forms.Select(attrs={"class": "form-input"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "inputmode": "numeric", "placeholder": "09123456789"}),
            "national_code": forms.TextInput(attrs={"class": "form-input", "inputmode": "numeric", "maxlength": "10"}),
            "landline": forms.TextInput(attrs={"class": "form-input", "inputmode": "tel", "placeholder": "031..."}),
            "occupation": forms.TextInput(attrs={"class": "form-input", "placeholder": "شغل یا سمت"}),
            "company_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "اختیاری"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            self.fields["email"].initial = self.instance.user.email

    def clean_phone(self):
        phone = normalize_digits(self.cleaned_data.get("phone"))
        if not re.fullmatch(r"09\d{9}", phone):
            raise forms.ValidationError("شماره موبایل باید با 09 شروع شود و ۱۱ رقم باشد.")
        duplicate = CustomerProfile.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists()
        if duplicate:
            raise forms.ValidationError("این شماره موبایل قبلاً استفاده شده است.")
        return phone

    def clean_national_code(self):
        return validate_national_code_value(self.cleaned_data.get("national_code"))

    def clean_landline(self):
        return normalize_digits(self.cleaned_data.get("landline"))

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar and getattr(avatar, "size", 0) > 3 * 1024 * 1024:
            raise forms.ValidationError("حجم تصویر پروفایل نباید بیشتر از ۳ مگابایت باشد.")
        return avatar

    def save(self, commit=True):
        profile = super().save(commit=commit)
        user = profile.user
        user.first_name = profile.first_name
        user.last_name = profile.last_name
        user.username = profile.phone
        user.email = self.cleaned_data.get("email", "")
        user.save(update_fields=["first_name", "last_name", "username", "email"])
        return profile


class StoreAddressForm(forms.ModelForm):
    class Meta:
        model = StoreAddress
        fields = [
            "title", "full_name", "phone", "recipient_national_code", "province", "city",
            "district", "address", "plaque", "unit", "postal_code", "delivery_notes", "is_default",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-input", "placeholder": "مثلاً منزل یا محل کار"}),
            "full_name": forms.TextInput(attrs={"class": "form-input", "autocomplete": "name"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "inputmode": "numeric"}),
            "recipient_national_code": forms.TextInput(attrs={"class": "form-input", "inputmode": "numeric", "maxlength": "10"}),
            "province": forms.Select(choices=IRAN_PROVINCES, attrs={"class": "form-input"}),
            "city": forms.TextInput(attrs={"class": "form-input", "autocomplete": "address-level2"}),
            "district": forms.TextInput(attrs={"class": "form-input", "placeholder": "منطقه یا محله"}),
            "address": forms.Textarea(attrs={"class": "form-input min-h-28", "placeholder": "خیابان، کوچه و نشانی کامل"}),
            "plaque": forms.TextInput(attrs={"class": "form-input", "inputmode": "numeric"}),
            "unit": forms.TextInput(attrs={"class": "form-input", "inputmode": "numeric"}),
            "postal_code": forms.TextInput(attrs={"class": "form-input", "inputmode": "numeric", "maxlength": "10"}),
            "delivery_notes": forms.Textarea(attrs={"class": "form-input min-h-20", "placeholder": "توضیحات لازم برای تحویل"}),
            "is_default": forms.CheckboxInput(attrs={"class": "h-5 w-5 accent-orange-500"}),
        }

    def clean_phone(self):
        phone = normalize_digits(self.cleaned_data.get("phone"))
        if not re.fullmatch(r"09\d{9}", phone):
            raise forms.ValidationError("شماره تحویل‌گیرنده باید ۱۱ رقم و با 09 شروع شود.")
        return phone

    def clean_postal_code(self):
        value = normalize_digits(self.cleaned_data.get("postal_code"))
        if not re.fullmatch(r"\d{10}", value):
            raise forms.ValidationError("کد پستی باید دقیقاً ۱۰ رقم باشد.")
        return value

    def clean_recipient_national_code(self):
        value = self.cleaned_data.get("recipient_national_code")
        return validate_national_code_value(value) if value else ""
# END CUSTOMER PORTAL PHASE 3 FORMS

# BEGIN PHASE 4 FORM OVERRIDES
from .forms_phase4 import CustomerProfileForm, StoreAddressForm, AppearancePreferenceForm
# END PHASE 4 FORM OVERRIDES

# BEGIN PHASE 5 LOCATION FORM OVERRIDE
from .forms_phase5 import StoreAddressForm
# END PHASE 5 LOCATION FORM OVERRIDE

# BEGIN PHASE 10 ORDER FORM OVERRIDE
from .order_intake import Phase10OrderForm

OrderForm = Phase10OrderForm
# END PHASE 10 ORDER FORM OVERRIDE

# BEGIN PHASE 28 QUOTE DEPOSIT PAYMENT
class QuotePaymentForm(forms.Form):
    payment_kind = forms.ChoiceField(
        label="نوع پرداخت",
        choices=(),
        widget=forms.RadioSelect,
    )
    receipt_image = forms.ImageField(
        label="تصویر رسید واریز",
        widget=forms.ClearableFileInput(attrs={"class": "form-input", "accept": "image/*"}),
    )
    note = forms.CharField(
        label="توضیحات پرداخت",
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "چهار رقم آخر کارت یا توضیح اختیاری"}),
    )

    def __init__(self, *args, quote=None, **kwargs):
        from .payment_services import quote_payment_amounts
        self.quote = quote
        self.payment_amounts = quote_payment_amounts(quote) if quote else {}
        super().__init__(*args, **kwargs)
        choices = []
        for kind, amount in self.payment_amounts.items():
            label = {"deposit": "پرداخت بیعانه", "full": "پرداخت کامل", "balance": "تسویه مانده"}.get(kind, "پرداخت")
            choices.append((kind, f"{label} ({amount:,} تومان)"))
        self.fields["payment_kind"].choices = choices
        if not choices:
            self.fields["payment_kind"].required = False
            self.fields["payment_kind"].help_text = "در حال حاضر مبلغ قابل پرداخت جدیدی وجود ندارد یا رسید قبلی در انتظار بررسی است."

    def clean(self):
        cleaned = super().clean()
        if not self.quote or not self.quote.total_price:
            raise forms.ValidationError("مبلغ پیش‌فاکتور هنوز نهایی نشده است.")
        kind = cleaned.get("payment_kind")
        if not kind or kind not in self.payment_amounts:
            raise forms.ValidationError("مبلغ قابل پرداختی برای این گزینه وجود ندارد یا رسید قبلی در انتظار بررسی است.")
        cleaned["payment_amount"] = self.payment_amounts[kind]
        return cleaned
# END PHASE 28 QUOTE DEPOSIT PAYMENT


# BEGIN PHASE 30 ONLINE PAYMENT FORM
class QuoteGatewayPaymentForm(forms.Form):
    payment_kind = forms.ChoiceField(
        label="مبلغ پرداخت آنلاین",
        choices=(),
        widget=forms.RadioSelect,
    )

    def __init__(self, *args, quote=None, **kwargs):
        from .payment_services import quote_payment_amounts
        self.quote = quote
        self.payment_amounts = quote_payment_amounts(quote) if quote else {}
        super().__init__(*args, **kwargs)
        choices = []
        for kind, amount in self.payment_amounts.items():
            label = {"deposit": "بیعانه", "full": "کل مبلغ", "balance": "مانده حساب"}.get(kind, "پرداخت")
            choices.append((kind, f"{label} — {amount:,} تومان"))
        self.fields["payment_kind"].choices = choices
        if not choices:
            self.fields["payment_kind"].required = False

    def clean(self):
        cleaned = super().clean()
        kind = cleaned.get("payment_kind")
        if not self.quote or not self.quote.total_price:
            raise forms.ValidationError("مبلغ پیش‌فاکتور هنوز نهایی نشده است.")
        if not kind or kind not in self.payment_amounts:
            raise forms.ValidationError("این مبلغ دیگر قابل پرداخت نیست؛ صفحه را دوباره بارگذاری کنید.")
        cleaned["payment_amount"] = int(self.payment_amounts[kind])
        return cleaned
# END PHASE 30 ONLINE PAYMENT FORM
