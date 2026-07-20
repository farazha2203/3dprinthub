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
