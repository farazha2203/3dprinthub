from __future__ import annotations

import hashlib
import html
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from urllib import request as urllib_request

from .site_connection import SiteConnection, _ensure_remote_dir, connect_ftp
from .social_content_policy import build_story_copy

STYLE_ID = "3dprinthub_instagram_gold_navy_v2"
STORY_WIDTH = 1080
STORY_HEIGHT = 1920


def _browser_path() -> str:
    candidates = (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    )
    for candidate in candidates:
        if Path(candidate).is_file():
            return candidate
    for name in ("chrome.exe", "msedge.exe"):
        found = shutil.which(name)
        if found:
            return found
    raise RuntimeError("Chrome/Edge برای رندر Story پیدا نشد.")


def _font_uri(name: str) -> str:
    path = Path(r"C:\Windows\Fonts") / name
    if not path.is_file():
        raise RuntimeError(f"فونت موردنیاز Story نصب نیست: {name}")
    return path.resolve().as_uri()


def _logo_uri() -> str:
    root = Path(__file__).resolve().parents[2]
    path = root / "assets" / "instagram" / "final" / "profile_logo_gold_navy.png"
    if not path.is_file():
        path = root / "static" / "img" / "brand" / "3dprinthublogo.png"
    if not path.is_file():
        raise RuntimeError("لوگوی 3DPrintHub برای Story پیدا نشد.")
    return path.resolve().as_uri()
def _render_html(*, image_url: str, product_url: str, copy: dict) -> str:
    bullets = "".join(
        f'<div class="feature"><span class="dot">◆</span><span>{html.escape(str(item))}</span></div>'
        for item in copy["bullets"]
    )
    title = html.escape(str(copy["title"]))
    subtitle = html.escape(str(copy["subtitle"]))
    url = html.escape(product_url.replace("https://", "").rstrip("/"))
    logo = _logo_uri()
    font_regular = _font_uri("IRANSansWeb(FaNum).ttf")
    font_medium = _font_uri("IRANSansWeb(FaNum)_Medium.ttf")
    font_bold = _font_uri("IRANSansWeb(FaNum)_Bold.ttf")
    return f"""<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8">
<style>
@font-face{{font-family:IRANSans;src:url('{font_regular}') format('truetype');font-weight:400}}
@font-face{{font-family:IRANSans;src:url('{font_medium}') format('truetype');font-weight:500}}
@font-face{{font-family:IRANSans;src:url('{font_bold}') format('truetype');font-weight:800}}
*{{box-sizing:border-box}}html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:#06131f}}
body{{font-family:IRANSans,Tahoma,sans-serif;color:#fff;position:relative}}
.bg{{position:absolute;inset:-80px;background:url('{html.escape(image_url)}') center/cover no-repeat;filter:blur(34px) brightness(.30) saturate(.9);transform:scale(1.12)}}
.overlay{{position:absolute;inset:0;background:linear-gradient(90deg,rgba(1,10,17,.96),rgba(4,14,23,.84) 42%,rgba(52,29,8,.28)),linear-gradient(180deg,rgba(0,10,18,.28),rgba(0,0,0,.08) 68%,rgba(0,0,0,.94))}}
.header{{position:absolute;top:60px;left:70px;right:70px;display:flex;direction:ltr;justify-content:space-between;align-items:flex-start}}
.brandbox{{display:flex;align-items:center;gap:18px}}.logo{{width:122px;height:122px;object-fit:cover;border-radius:50%;box-shadow:0 0 36px rgba(243,184,66,.34)}}
.brand{{font-family:'Segoe UI';font-size:38px;font-weight:800;color:#f7c75a}}.tag{{font-family:'Segoe UI';font-size:14px;letter-spacing:5px;color:#f7f1df;margin-top:6px}}
.micro{{font-family:'Segoe UI';font-size:15px;line-height:1.75;letter-spacing:4px;color:#f7e8c7;text-align:left;width:230px}}
.copy{{position:absolute;top:245px;left:70px;width:650px;text-align:right}}.kicker{{font-size:25px;color:#ffd477;margin-bottom:14px;font-weight:500}}
.title{{font-size:70px;line-height:1.3;font-weight:800;color:#f5c65a;text-shadow:0 5px 30px rgba(0,0,0,.55)}}.subtitle{{font-size:32px;line-height:1.65;color:#fff3df;margin-top:24px;font-weight:500}}
.glow{{position:absolute;left:68px;right:68px;top:586px;height:2px;background:linear-gradient(90deg,transparent,#f5bd48,#ffd979,#f5bd48,transparent);box-shadow:0 0 25px #f3a61d}}
.hero{{position:absolute;right:58px;top:650px;width:655px;height:690px;border-radius:42px;overflow:hidden;border:2px solid rgba(246,191,77,.8);box-shadow:0 38px 95px rgba(0,0,0,.58),0 0 52px rgba(247,177,43,.20)}}.hero img{{width:100%;height:100%;object-fit:cover}}
.features{{position:absolute;left:66px;top:680px;width:310px;display:flex;flex-direction:column;gap:26px}}.feature{{display:flex;direction:rtl;align-items:center;gap:14px;padding-bottom:20px;border-bottom:1px solid rgba(255,212,125,.24);font-size:22px;line-height:1.55;color:#fff0dc}}.dot{{font-size:19px;color:#f7c85d}}
.cta{{position:absolute;left:220px;right:220px;top:1435px;height:116px;border-radius:58px;border:3px solid #f3c25c;background:linear-gradient(180deg,rgba(122,68,15,.86),rgba(24,13,7,.92));display:flex;align-items:center;justify-content:center;font-size:41px;font-weight:800;color:#ffe29a;box-shadow:0 0 36px rgba(255,173,39,.3)}}
.url{{position:absolute;top:1575px;left:70px;right:70px;text-align:center;direction:ltr;font-family:'Segoe UI';font-size:21px;letter-spacing:2px;color:#f5eee1}}
.footer{{position:absolute;bottom:75px;left:70px;right:70px;display:flex;direction:ltr;justify-content:space-between;align-items:flex-end}}.signature{{font-family:'Segoe Script';font-size:44px;color:#efb848;transform:rotate(-4deg)}}.small{{font-family:'Segoe UI';font-size:13px;letter-spacing:5px;line-height:1.9;color:#f9e7c2;text-align:right}}
</style></head><body>
<div class="bg"></div><div class="overlay"></div><div class="glow"></div>
<div class="header"><div class="brandbox"><img class="logo" src="{logo}"><div><div class="brand">3DPRINTHUB</div><div class="tag">IDEAS INTO REALITY</div></div></div><div class="micro">ORIGINAL<br>PRODUCT<br>DESIGN</div></div>
<div class="copy"><div class="kicker">محصول 3DPrintHub</div><div class="title">{title}</div><div class="subtitle">{subtitle}</div></div>
<div class="features">{bullets}</div><div class="hero"><img src="{html.escape(image_url)}"></div>
<div class="cta">مشاهده محصول <span style="margin-right:18px;font-family:'Segoe UI';font-size:50px">›</span></div>
<div class="url">{url}</div>
<div class="footer"><div class="signature">Ideas into Reality</div><div class="small">3D PRINT<br>A BRIGHTER<br>TOMORROW</div></div>
</body></html>"""
def _revision_key(row: dict) -> str:
    raw = str(row.get("server_ack_json") or row.get("fingerprint") or row.get("updated_at") or "")
    return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()[:16]


def _render_story(row: dict, payload: dict) -> Path:
    copy = build_story_copy(row)
    revision = _revision_key(row)
    local_root = Path(
        os.environ.get("LOCALAPPDATA")
        or (Path.home() / "AppData" / "Local")
    )
    out_dir = (
        local_root
        / "3DPrintHub"
        / "CatalogCenter"
        / "social"
        / "stories"
        / str(int(row.get("id") or 0))
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / f"{revision}.png"
    if png.is_file() and png.stat().st_size > 50_000:
        return png
    html_text = _render_html(
        image_url=str(payload["media_urls"][0]),
        product_url=str(payload["product_url"]),
        copy=copy,
    )
    with tempfile.TemporaryDirectory(prefix="3dprinthub-story-") as tmp:
        html_path = Path(tmp) / "story.html"
        html_path.write_text(html_text, encoding="utf-8")
        subprocess.run(
            [
                _browser_path(),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--allow-file-access-from-files",
                "--force-device-scale-factor=1",
                f"--window-size={STORY_WIDTH},{STORY_HEIGHT}",
                f"--screenshot={png}",
                html_path.resolve().as_uri(),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=60,
        )
    if not png.is_file() or png.stat().st_size < 50_000:
        raise RuntimeError("رندر Story خروجی معتبر تولید نکرد.")
    return png


def _verify_public_image(url: str, timeout: int = 20) -> None:
    req = urllib_request.Request(url, method="HEAD", headers={"User-Agent": "3DPrintHub-Social/2.0"})
    with urllib_request.urlopen(req, timeout=timeout) as response:
        content_type = str(response.headers.get("Content-Type") or "").lower()
        if int(response.status) != 200 or not content_type.startswith("image/"):
            raise RuntimeError(f"Story public verification failed: HTTP {response.status} {content_type}")
def prepare_product_story_asset(db, product_id: int, settings: SiteConnection, payload: dict) -> dict:
    row_obj = db.product(int(product_id))
    if row_obj is None:
        raise RuntimeError(f"Product {product_id} not found")
    row = dict(row_obj)
    png = _render_story(row, payload)
    revision = _revision_key(row)
    remote_root = str(
        db.setting(
            "instagram_story_remote_root",
            "/public_html/media/instagram/stories/products",
        )
        or "/public_html/media/instagram/stories/products"
    ).strip()
    remote_dir = str(PurePosixPath(remote_root) / str(int(product_id)))
    remote_file = str(PurePosixPath(remote_dir) / f"{revision}.png")

    ftp = connect_ftp(settings)
    try:
        _ensure_remote_dir(ftp, remote_dir)
        with png.open("rb") as handle:
            ftp.storbinary(f"STOR {remote_file}", handle, blocksize=128 * 1024)
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()

    public_url = (
        settings.site_url.rstrip("/")
        + f"/media/instagram/stories/products/{int(product_id)}/{revision}.png"
    )
    _verify_public_image(public_url, timeout=max(10, int(settings.timeout)))
    return {
        "url": public_url,
        "local_path": str(png),
        "style_id": STYLE_ID,
        "font_family": "IRANSansWeb(FaNum)",
        "width": STORY_WIDTH,
        "height": STORY_HEIGHT,
        "revision": revision,
    }
