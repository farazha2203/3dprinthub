from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .iran_locations import IRAN_LOCATIONS
from .models import IranCity, IranCounty, IranProvince


@require_GET
def iran_counties_view(request):
    province = request.GET.get("province", "").strip()
    counties = list(IranCounty.objects.filter(province__name=province, province__is_active=True, is_active=True).values_list("name", flat=True).distinct())
    if not counties:
        counties = sorted(set(IRAN_LOCATIONS.get(province, [])))
    return JsonResponse({"province": province, "counties": counties})


@require_GET
def iran_cities_v2_view(request):
    province = request.GET.get("province", "").strip()
    county = request.GET.get("county", "").strip()
    cities = list(IranCity.objects.filter(province__name=province, county__name=county, province__is_active=True, county__is_active=True, is_active=True).values_list("name", flat=True).distinct())
    if not cities and county in IRAN_LOCATIONS.get(province, []):
        cities = [county]
    return JsonResponse({"province": province, "county": county, "cities": cities})
