from __future__ import annotations

from django import forms
from store.models import StoreAddress
from .forms_phase4 import StoreAddressForm as Phase4StoreAddressForm
from .iran_locations import IRAN_LOCATIONS
from .models import IranCity, IranCounty, IranProvince


def _unique(values):
    return sorted({value for value in values if value})


class StoreAddressForm(Phase4StoreAddressForm):
    province = forms.ChoiceField(
        required=True,
        label="استان",
        widget=forms.Select(attrs={
            "class": "form-input",
            "data-iran-province": "1",
        }),
    )
    county = forms.ChoiceField(
        required=True,
        label="شهرستان",
        widget=forms.Select(attrs={
            "class": "form-input",
            "data-iran-county": "1",
            "data-county-endpoint": "/customer/locations/counties/",
        }),
    )
    city = forms.ChoiceField(
        required=True,
        label="شهر",
        widget=forms.Select(attrs={
            "class": "form-input",
            "data-iran-city": "1",
            "data-city-endpoint": "/customer/locations/cities-v2/",
        }),
    )
    class Meta(Phase4StoreAddressForm.Meta):
        model = StoreAddress
        fields = [
            "title", "full_name", "phone", "recipient_national_code", "province", "county", "city",
            "district", "address", "plaque", "unit", "postal_code", "delivery_notes", "is_default",
        ]
        widgets = dict(Phase4StoreAddressForm.Meta.widgets)
        widgets.update({
            "province": forms.Select(attrs={"class":"form-input", "data-iran-province":"1"}),
            "county": forms.Select(attrs={"class":"form-input", "data-iran-county":"1", "data-county-endpoint":"/customer/locations/counties/"}),
            "city": forms.Select(attrs={"class":"form-input", "data-iran-city":"1", "data-city-endpoint":"/customer/locations/cities/"}),
        })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        province = (self.data.get("province") if self.is_bound else getattr(self.instance, "province", "")) or ""
        county = (self.data.get("county") if self.is_bound else getattr(self.instance, "county", "")) or ""
        city = (self.data.get("city") if self.is_bound else getattr(self.instance, "city", "")) or ""

        provinces = list(IranProvince.objects.filter(is_active=True).values_list("name", flat=True))
        if not provinces:
            provinces = list(IRAN_LOCATIONS.keys())
        self.fields["province"].choices = [("", "انتخاب استان")] + [(x, x) for x in _unique(provinces)]

        counties = []
        if province:
            counties = list(IranCounty.objects.filter(province__name=province, is_active=True).values_list("name", flat=True))
            if not counties:
                counties = IRAN_LOCATIONS.get(province, [])
        self.fields["county"].choices = [("", "ابتدا استان را انتخاب کنید" if not province else "انتخاب شهرستان")] + [(x, x) for x in _unique(counties)]

        cities = []
        if province and county:
            cities = list(IranCity.objects.filter(province__name=province, county__name=county, is_active=True).values_list("name", flat=True))
            if not cities and county in IRAN_LOCATIONS.get(province, []):
                cities = [county]
        self.fields["city"].choices = [("", "ابتدا شهرستان را انتخاب کنید" if not county else "انتخاب شهر")] + [(x, x) for x in _unique(cities)]

        for field_name, selected in (("province", province), ("county", county), ("city", city)):
            if selected and selected not in dict(self.fields[field_name].choices):
                self.fields[field_name].choices.append((selected, selected))
        for field in ("province", "county", "city", "postal_code"):
            self.fields[field].required = True

    def clean(self):
        cleaned = forms.ModelForm.clean(self)
        province = cleaned.get("province")
        county = cleaned.get("county")
        city = cleaned.get("city")
        db_has_locations = IranProvince.objects.exists()
        if db_has_locations:
            province_obj = IranProvince.objects.filter(name=province, is_active=True).first()
            if not province_obj:
                self.add_error("province", "استان انتخاب‌شده معتبر نیست.")
                return cleaned
            county_obj = IranCounty.objects.filter(province=province_obj, name=county, is_active=True).first()
            if not county_obj:
                self.add_error("county", "شهرستان انتخاب‌شده مربوط به این استان نیست.")
                return cleaned
            if not IranCity.objects.filter(province=province_obj, county=county_obj, name=city, is_active=True).exists():
                self.add_error("city", "شهر انتخاب‌شده مربوط به این شهرستان نیست.")
        else:
            if province not in IRAN_LOCATIONS:
                self.add_error("province", "استان انتخاب‌شده معتبر نیست.")
            elif county not in IRAN_LOCATIONS[province]:
                self.add_error("county", "شهرستان انتخاب‌شده معتبر نیست.")
            elif city != county:
                self.add_error("city", "برای تکمیل فهرست شهرها دستور seed_iran_locations را اجرا کنید.")
        return cleaned
