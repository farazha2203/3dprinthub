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
        password = self.cleaned_data["password"]

        user = User.objects.create_user(
            username=phone,
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
        label="شماره تماس",
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "شماره تماس",
        })
    )

    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "رمز عبور",
        })
    )


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