from pathlib import Path
import html, subprocess, urllib.parse

ROOT = Path(r"D:\projects\3DprintHub")
OUT = ROOT / "assets" / "instagram" / "stories" / "2026-09-18"
OUT.mkdir(parents=True, exist_ok=True)
LOGO = ROOT / "assets" / "instagram" / "final" / "profile_logo_gold_navy.png"

stories = [
    {
        "key":"lamp",
        "image": ROOT/"assets"/"instagram"/"real_posts"/"lamp.jpg",
        "eyebrow":"آباژور چاپ سه‌بعدی",
        "title":"نور، به سبک شما",
        "sub":"آباژور رومیزی موج‌دار با طراحی پارامتریک",
        "features":["طراحی منحصربه‌فرد","نور گرم و دکوراتیو","رنگ‌بندی سفارشی","مناسب فضای مدرن"],
        "cta":"مشاهده محصول",
        "url":"3dprinthub.ir/store/product/driftbloom-table-lamp-organic-ambient-desk-lamp/",
    },
    {
        "key":"cake",
        "image": ROOT/"assets"/"instagram"/"real_posts"/"cake.jpg",
        "eyebrow":"پایه کیک چاپ سه‌بعدی",
        "title":"جزئیات، میز شما را خاص می‌کند",
        "sub":"استند کیک و شیرینی مینیمال با فرم شیاردار",
        "features":["فرم مدرن و مینیمال","قابل تولید در رنگ‌های مختلف","مناسب عکاسی و پذیرایی","سفارش ابعاد اختصاصی"],
        "cta":"مشاهده محصولات",
        "url":"3dprinthub.ir",
    },
    {
        "key":"christmas",
        "image": ROOT/"assets"/"instagram"/"real_posts"/"christmas.jpg",
        "eyebrow":"اکسسوری کریسمس",
        "title":"کریسمس، با طراحی متفاوت",
        "sub":"دکور مینیمال سه‌بعدی برای میز، شلف و هدیه",
        "features":["طراحی جمع‌وجور","رنگ و اندازه سفارشی","مناسب هدیه","چاپ سه‌بعدی دقیق"],
        "cta":"مشاهده محصول",
        "url":"3dprinthub.ir/store/product/christmas-tree-minimalistic-japandi-decor/",
    },
]

def uri(p: Path) -> str:
    return p.resolve().as_uri()

def make_html(s):
    feature_html = "".join(
        f'<div class="feature"><span class="dot">◆</span><span>{html.escape(x)}</span></div>'
        for x in s["features"]
    )
    return f"""<!doctype html>
<html lang="fa" dir="rtl"><head><meta charset="utf-8">
<style>
*{{box-sizing:border-box}} html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:#07131f}}
body{{font-family:"Segoe UI","Tahoma",sans-serif;color:#fff;position:relative}}
.bg{{position:absolute;inset:-80px;background:url('{uri(s["image"])}') center/cover no-repeat;filter:blur(28px) brightness(.38) saturate(.9);transform:scale(1.08)}}
.veil{{position:absolute;inset:0;background:
linear-gradient(180deg,rgba(3,14,25,.82) 0%,rgba(3,14,25,.68) 34%,rgba(14,8,3,.58) 72%,rgba(3,9,15,.94) 100%),
linear-gradient(90deg,rgba(2,14,25,.92) 0%,rgba(3,15,25,.72) 46%,rgba(72,37,10,.18) 100%)}}
.goldline{{position:absolute;left:66px;right:66px;top:515px;height:2px;background:linear-gradient(90deg,transparent,#f1b94d,#ffd77a,#f1b94d,transparent);box-shadow:0 0 20px #ffb52e}}
.header{{position:absolute;top:68px;left:70px;right:70px;display:flex;direction:ltr;align-items:flex-start;justify-content:space-between}}
.logo{{width:290px;display:flex;align-items:center;gap:18px}}
.logo img{{width:104px;height:104px;border-radius:50%;object-fit:cover;box-shadow:0 0 32px rgba(255,185,64,.38)}}
.logo .brand{{font-size:34px;font-weight:800;letter-spacing:1px;color:#f6c65d;line-height:1.1}}
.logo .tag{{font-size:14px;letter-spacing:5px;color:#f7f1df;margin-top:8px}}
.micro{{width:230px;color:#f6e6c5;font-size:16px;line-height:1.7;letter-spacing:4px;text-transform:uppercase}}
.copy{{position:absolute;top:215px;left:70px;width:650px;text-align:right}}
.eyebrow{{font-size:25px;color:#ffd373;margin-bottom:14px}}
.title{{font-size:72px;line-height:1.25;font-weight:900;color:#f5c85b;text-shadow:0 4px 28px rgba(0,0,0,.45)}}
.sub{{font-size:31px;line-height:1.6;color:#f5ead7;margin-top:20px;max-width:610px}}
.hero{{position:absolute;top:575px;left:305px;width:705px;height:760px;border-radius:42px;overflow:hidden;border:2px solid rgba(247,190,72,.72);box-shadow:0 35px 80px rgba(0,0,0,.55),0 0 42px rgba(244,170,35,.16)}}
.hero:after{{content:"";position:absolute;inset:0;box-shadow:inset 0 -110px 120px rgba(0,0,0,.42)}}
.hero img{{width:100%;height:100%;object-fit:cover;display:block}}
.features{{position:absolute;top:625px;left:64px;width:270px;display:flex;flex-direction:column;gap:28px}}
.feature{{direction:rtl;display:flex;align-items:center;gap:13px;padding-bottom:20px;border-bottom:1px solid rgba(255,210,117,.23);font-size:22px;line-height:1.45;color:#f7ecda}}
.dot{{color:#f7c85c;font-size:19px}}
.cta{{position:absolute;top:1400px;left:210px;right:210px;height:118px;border-radius:59px;border:3px solid #f4c258;background:linear-gradient(180deg,rgba(130,73,17,.82),rgba(31,18,9,.9));display:flex;align-items:center;justify-content:center;font-size:42px;font-weight:800;color:#ffe199;box-shadow:0 0 34px rgba(255,175,40,.28)}}
.url{{position:absolute;top:1540px;left:80px;right:80px;text-align:center;color:#f7efe0;font-size:23px;letter-spacing:3px;direction:ltr}}
.footer{{position:absolute;bottom:92px;left:70px;right:70px;display:flex;justify-content:space-between;align-items:flex-end;direction:ltr}}
.signature{{font-family:"Segoe Script","Segoe UI",sans-serif;font-size:47px;color:#f0b94c;transform:rotate(-4deg)}}
.small{{width:250px;text-align:right;color:#f6e2bc;font-size:14px;letter-spacing:5px;line-height:1.8}}
</style></head>
<body><div class="bg"></div><div class="veil"></div><div class="goldline"></div>
<div class="header"><div class="logo"><img src="{uri(LOGO)}"><div><div class="brand">3DPRINTHUB</div><div class="tag">IDEAS TO REALITY</div></div></div><div class="micro">MORE THAN PRINTS<br>A BETTER DAILY LIFE</div></div>
<div class="copy"><div class="eyebrow">{html.escape(s["eyebrow"])}</div><div class="title">{html.escape(s["title"])}</div><div class="sub">{html.escape(s["sub"])}</div></div>
<div class="features">{feature_html}</div>
<div class="hero"><img src="{uri(s["image"])}"></div>
<div class="cta">{html.escape(s["cta"])} <span style="margin-right:20px;font-size:50px">›</span></div>
<div class="url">{html.escape(s["url"])}</div>
<div class="footer"><div class="signature">Ideas into Reality</div><div class="small">3D PRINT<br>A BRIGHTER TOMORROW</div></div>
</body></html>"""

chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
for s in stories:
    html_path = OUT / f'{s["key"]}.html'
    png_path = OUT / f'{s["key"]}.png'
    html_path.write_text(make_html(s), encoding="utf-8")
    subprocess.run([
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        "--window-size=1080,1920",
        f"--screenshot={png_path}",
        html_path.resolve().as_uri(),
    ], check=True)
    print(f"RENDERED={s['key']}::{png_path}")
