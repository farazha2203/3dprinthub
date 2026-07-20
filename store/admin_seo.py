from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ServicePage
SEO_FIELDS=("seo_focus_keyword","meta_title","meta_description","canonical_url","robots_index","robots_follow","og_title","og_description","og_image")
class SEOAdminMixin:
    _phase4_seo=True
    class Media:
        css={"all":("admin/seo-admin.css",)}
        js=("admin/seo-admin.js",)
    @admin.display(description="وضعیت سئو")
    def seo_status(self,obj):
        score=0
        title=(obj.meta_title or "").strip(); desc=(obj.meta_description or "").strip(); keyword=(obj.seo_focus_keyword or "").strip()
        score += 25 if 20 <= len(title) <= 70 else 10 if title else 0
        score += 25 if 70 <= len(desc) <= 180 else 10 if desc else 0
        score += 20 if keyword and keyword in f"{title} {desc}" else 5 if keyword else 0
        score += 15 if getattr(obj,"og_image",None) else 5
        score += 15 if obj.robots_index else 0
        color="#16a34a" if score>=80 else "#f59e0b" if score>=55 else "#dc2626"
        return format_html('<span style="background:{};color:white;padding:4px 9px;border-radius:999px;font-weight:700">{}٪</span>',color,score)
    @admin.display(description="پیش‌نمایش نتیجه گوگل")
    def seo_preview(self,obj):
        if not obj: return "پس از ذخیره نمایش داده می‌شود."
        title=obj.meta_title or str(obj)
        desc=obj.meta_description or "برای این صفحه توضیح متا ثبت نشده است."
        try: url=obj.canonical_url or obj.get_absolute_url()
        except Exception: url=obj.canonical_url or "/"
        return format_html('<div class="seo-preview"><div class="seo-preview__url">{}</div><div class="seo-preview__title">{}</div><div class="seo-preview__desc">{}</div></div>',url,title,desc)

def _register_enhanced(model, fieldsets):
    current=admin.site._registry.get(model)
    if current and getattr(current,"_phase4_seo",False): return
    base=current.__class__ if current else admin.ModelAdmin
    if current: admin.site.unregister(model)
    attrs={"fieldsets":fieldsets,"readonly_fields":tuple(getattr(base,"readonly_fields",()))+("seo_preview",),"list_display":tuple(getattr(base,"list_display",("__str__",)))+("seo_status",),"_phase4_seo":True,"__module__":__name__}
    cls=type(f"{model.__name__}SEOAdmin",(SEOAdminMixin,base),attrs)
    admin.site.register(model,cls)

_register_enhanced(Category,(("اطلاعات دسته",{"fields":("parent","section","name","slug","description","image","sort_order","is_active")}), ("سئو و شبکه‌های اجتماعی",{"fields":SEO_FIELDS+("seo_preview",)})))
_register_enhanced(Product,(("اطلاعات محصول",{"fields":("category","title","slug","sku","short_description","description","main_image","model_file","dimensions","technical_notes","installation_guide","is_featured","is_active","published_at")}), ("سئو و شبکه‌های اجتماعی",{"fields":SEO_FIELDS+("seo_preview",)}), ("آمار",{"fields":("view_count","created_at","updated_at")})))
_register_enhanced(ServicePage,(("اطلاعات خدمت",{"fields":("service_type","title","slug","short_description","content","hero_image","sort_order","is_active")}), ("سئو و شبکه‌های اجتماعی",{"fields":SEO_FIELDS+("seo_preview",)}), ("زمان‌ها",{"fields":("created_at","updated_at")})))
