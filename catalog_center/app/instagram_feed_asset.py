from __future__ import annotations

import hashlib
import json
import os
from io import BytesIO
from pathlib import Path, PurePosixPath
from urllib import request as urllib_request

from PIL import Image

from .site_connection import SiteConnection, _ensure_remote_dir, connect_ftp


MAX_WIDTH = 1440
MIN_WIDTH = 320
MIN_RATIO = 3 / 4
MAX_RATIO = 1.91


def _revision_key(row: dict) -> str:
    raw = str(row.get("server_ack_json") or row.get("fingerprint") or row.get("updated_at") or "")
    return hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest()[:16]


def _verify_public_image(url: str, timeout: int = 20) -> None:
    req = urllib_request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "3DPrintHub-Social/3.0"},
    )
    with urllib_request.urlopen(req, timeout=timeout) as response:
        content_type = str(response.headers.get("Content-Type") or "").lower()
        if int(response.status) != 200 or not content_type.startswith("image/"):
            raise RuntimeError(
                f"Instagram feed asset verification failed: HTTP {response.status} {content_type}"
            )


def _instagram_canvas(image: Image.Image) -> Image.Image:
    source = image.convert("RGB")
    width, height = source.size
    if width <= 0 or height <= 0:
        raise RuntimeError("Invalid source image dimensions for Instagram feed.")

    ratio = width / height
    canvas_w, canvas_h = width, height
    if ratio < MIN_RATIO:
        canvas_w = max(width, int(round(height * MIN_RATIO)))
    elif ratio > MAX_RATIO:
        canvas_h = max(height, int(round(width / MAX_RATIO)))

    if (canvas_w, canvas_h) != (width, height):
        canvas = Image.new("RGB", (canvas_w, canvas_h), "#071827")
        canvas.paste(source, ((canvas_w - width) // 2, (canvas_h - height) // 2))
        source = canvas

    width, height = source.size
    target_width = min(MAX_WIDTH, max(MIN_WIDTH, width))
    if target_width != width:
        target_height = max(1, int(round(height * target_width / width)))
        source = source.resize((target_width, target_height), Image.Resampling.LANCZOS)
    return source


def prepare_product_feed_assets(
    db,
    product_id: int,
    settings: SiteConnection,
    payload: dict,
) -> dict:
    row_obj = db.product(int(product_id))
    if row_obj is None:
        raise RuntimeError(f"Product {product_id} not found")
    row = dict(row_obj)
    media_urls = [str(value or "").strip() for value in (payload.get("media_urls") or [])]
    media_urls = [value for value in media_urls if value.startswith("https://")][:10]
    if not media_urls:
        raise RuntimeError("No verified public Product media is available for Instagram feed.")

    revision = _revision_key(row)
    local_root = Path(
        os.environ.get("LOCALAPPDATA")
        or (Path.home() / "AppData" / "Local")
    ) / "3DPrintHub" / "instagram" / "feed" / str(int(product_id)) / revision
    local_root.mkdir(parents=True, exist_ok=True)

    remote_root = str(
        db.setting(
            "instagram_feed_remote_root",
            "/public_html/media/instagram/feed/products",
        )
        or "/public_html/media/instagram/feed/products"
    ).strip()
    remote_dir = str(PurePosixPath(remote_root) / str(int(product_id)) / revision)

    ftp = connect_ftp(settings)
    public_urls: list[str] = []
    dimensions: list[dict[str, int]] = []
    try:
        _ensure_remote_dir(ftp, remote_dir)
        for index, source_url in enumerate(media_urls, 1):
            request = urllib_request.Request(
                source_url,
                headers={"User-Agent": "3DPrintHub-Social/3.0"},
            )
            with urllib_request.urlopen(request, timeout=max(10, int(settings.timeout))) as response:
                source_bytes = response.read(12 * 1024 * 1024 + 1)
            if len(source_bytes) > 12 * 1024 * 1024:
                raise RuntimeError(f"Instagram source image {index} is unexpectedly large.")

            with Image.open(BytesIO(source_bytes)) as opened:
                rendered = _instagram_canvas(opened)
            local_file = local_root / f"{index:02d}.png"
            rendered.save(local_file, format="PNG", optimize=True)
            width, height = rendered.size
            dimensions.append({"width": int(width), "height": int(height)})

            remote_file = str(PurePosixPath(remote_dir) / local_file.name)
            with local_file.open("rb") as handle:
                ftp.storbinary(f"STOR {remote_file}", handle, blocksize=128 * 1024)

            public_url = (
                settings.site_url.rstrip("/")
                + f"/media/instagram/feed/products/{int(product_id)}/{revision}/{local_file.name}"
            )
            _verify_public_image(public_url, timeout=max(10, int(settings.timeout)))
            public_urls.append(public_url)
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()

    return {
        "urls": public_urls,
        "local_paths": [
            str(local_root / f"{index:02d}.png")
            for index in range(1, len(public_urls) + 1)
        ],
        "source_urls": media_urls,
        "dimensions": dimensions,
        "format": "png",
        "revision": revision,
    }
