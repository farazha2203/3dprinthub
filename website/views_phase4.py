from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib.sitemaps.views import sitemap as django_sitemap_view
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST
from .forms_phase4 import AppearancePreferenceForm, THEME_CHOICES
from .iran_locations import IRAN_LOCATIONS
from .models import CustomerProfile, SEOSettings, SiteSetting
from store.sitemaps import StaticViewSitemap, ProductSitemap, CategorySitemap, ServicePageSitemap

VALID_THEMES = {key for key, _ in THEME_CHOICES}

def _profile(user):
    profile, _ = CustomerProfile.objects.get_or_create(user=user, defaults={"phone":user.username,"first_name":user.first_name,"last_name":user.last_name})
    return profile

@require_GET
def iran_cities_view(request):
    province = request.GET.get("province", "").strip()
    return JsonResponse({"province": province, "cities": IRAN_LOCATIONS.get(province, [])})

@login_required
def customer_appearance_view(request):
    profile = _profile(request.user)
    if request.method == "POST":
        form = AppearancePreferenceForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.theme_prompt_seen = True
            profile.save(update_fields=["theme_preference","theme_prompt_seen"])
            messages.success(request, "رنگ‌بندی حساب شما ذخیره شد.")
            return redirect("website:customer_appearance")
    else:
        form = AppearancePreferenceForm(instance=profile)
    return render(request, "website/customer/appearance.html", {"settings":SiteSetting.objects.first(),"profile":profile,"profile_completion":100,"form":form})

@require_POST
def customer_theme_update_view(request):
    theme = request.POST.get("theme", "original")
    seen = request.POST.get("seen", "1") in {"1","true","yes","on"}
    if theme not in VALID_THEMES:
        return JsonResponse({"ok":False,"error":"invalid_theme"}, status=400)
    if request.user.is_authenticated:
        profile = _profile(request.user)
        profile.theme_preference = theme
        profile.theme_prompt_seen = seen
        profile.save(update_fields=["theme_preference","theme_prompt_seen"])
    return JsonResponse({"ok":True,"theme":theme,"seen":seen})

def robots_txt_response(request):
    seo = SEOSettings.objects.first()
    allow = True if seo is None else seo.allow_search_indexing
    domain = (seo.site_url.rstrip("/") if seo and seo.site_url else "https://3dprinthub.ir")
    lines = ["User-agent: *"]
    lines.append("Allow: /" if allow else "Disallow: /")
    if allow:
        lines.extend([
            "Disallow: /admin/", "Disallow: /customer/", "Disallow: /store/cart/",
            "Disallow: /store/checkout/", "Disallow: /store/account/", "Disallow: /store/order/",
            f"Sitemap: {domain}/sitemap.xml",
        ])
        if seo and seo.robots_extra:
            lines.append(seo.robots_extra.strip())
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")

def sitemap_xml_response(request):
    return django_sitemap_view(request, sitemaps={
        "static": StaticViewSitemap,
        "products": ProductSitemap,
        "categories": CategorySitemap,
        "services": ServicePageSitemap,
    })
