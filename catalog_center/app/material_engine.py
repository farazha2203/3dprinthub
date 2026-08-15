from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class MaterialProfile:
    code: str
    label: str
    heat: int
    uv: int
    strength: int
    wear: int
    flex: int
    chemical: int
    cost: int
    decor: int

MATERIALS = [
    MaterialProfile("pla","PLA",35,20,45,25,10,20,15,95),
    MaterialProfile("pla_ht","PLA-HT",65,35,55,30,10,30,28,88),
    MaterialProfile("petg","PETG",55,55,60,42,18,55,25,80),
    MaterialProfile("asa","ASA",85,95,68,45,10,65,40,60),
    MaterialProfile("abs","ABS",75,45,68,45,15,55,35,60),
    MaterialProfile("tpu","TPU",45,55,35,70,100,55,45,35),
    MaterialProfile("pa","PA/Nylon",75,45,82,90,35,55,55,30),
    MaterialProfile("pa_cf","PA-CF",85,50,92,92,10,60,70,22),
    MaterialProfile("ppa_cf","PPA-CF",95,55,98,95,8,80,88,10),
    MaterialProfile("pps_cf","PPS-CF",100,75,98,96,5,100,100,5),
]

def infer_use_case(title: str, description: str, categories: list[str] | None = None, specs: dict[str, Any] | None = None) -> str:
    text=" ".join([title or "",description or ""," ".join(categories or [])," ".join(f"{k} {v}" for k,v in (specs or {}).items())]).lower()
    buckets=[
        ("flexible",("flexible","gasket","seal","bumper","grip","انعطاف","واشر")),
        ("gear_wear",("gear","bearing","sprocket","pulley","wear","چرخ دنده","دنده","سایش")),
        ("automotive_outdoor",("automotive","car","dashboard","engine","vehicle","خودرو","ماشین","موتور")),
        ("outdoor",("outdoor","garden","sun","uv","weather","فضای باز","آفتاب")),
        ("industrial",("industrial","machine","fixture","jig","mechanical","صنعتی","مکانیکی","فیکسچر")),
        ("home_decor",("decor","lamp","vase","organizer","home","toy","figurine","چراغ","دکور","گلدان","فیگور","نظم")),
    ]
    for name,tokens in buckets:
        if any(t in text for t in tokens): return name
    return "general"

def recommend_materials(use_case: str, *, heat_required: bool=False, uv_required: bool=False, chemical_required: bool=False) -> list[dict[str, Any]]:
    out=[]
    for m in MATERIALS:
        score=50
        reasons=[]
        if use_case=="home_decor":
            score += (m.decor-50)//2 - max(0,m.cost-45)//2
            reasons.append("برای ظاهر و هزینه متعادل ارزیابی شد")
            if m.code in {"ppa_cf","pps_cf"}: score-=45; reasons.append("برای کاربرد معمول خانگی بیش‌ازحد مهندسی و پرهزینه است")
        elif use_case=="gear_wear":
            score += (m.strength+m.wear-100)//3
            if m.code in {"pa","pa_cf","ppa_cf","pps_cf"}: reasons.append("مقاومت مکانیکی/سایشی مناسب‌تر برای انتقال نیرو")
            if m.code=="pla": score-=35; reasons.append("برای سایش و بار مداوم انتخاب اول نیست")
        elif use_case=="flexible":
            score += (m.flex-50)//2
            if m.code=="tpu": score+=35; reasons.append("انعطاف بالا")
        elif use_case in {"automotive_outdoor","outdoor"}:
            score += (m.heat+m.uv-100)//3
            if m.code in {"asa","pa_cf","ppa_cf"}: reasons.append("مقاومت حرارتی/محیطی بهتر")
        elif use_case=="industrial":
            score += (m.strength+m.chemical+m.wear-150)//5
        else:
            score += (m.decor-50)//4 - max(0,m.cost-70)//4
        if heat_required: score += (m.heat-50)//3
        if uv_required: score += (m.uv-50)//3
        if chemical_required: score += (m.chemical-50)//3
        score=max(0,min(100,score))
        out.append({"material":m.label,"code":m.code,"score":score,"recommended":score>=65,"reason_fa":"؛ ".join(reasons) or "ارزیابی عمومی بر اساس کاربرد"})
    return sorted(out,key=lambda x:x["score"],reverse=True)
