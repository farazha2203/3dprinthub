from __future__ import annotations

import hashlib
import json
import os
import re
from io import BytesIO
from pathlib import Path, PurePosixPath
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from PIL import Image

from .site_connection import SiteConnection, _ensure_remote_dir, connect_ftp


MAX_WIDTH = 1440
MIN_WIDTH = 320
MIN_RATIO = 3 / 4
MAX_RATIO = 1.91


def _json_list(raw) -> list:
    if isinstance(raw, list):
        return raw
    try:
        parsed = json.loads(raw or "[]")
    except Exception:
        return []
    return parsed if isinstance(parsed, list) else []


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_local_product_media(row: dict, public_url: str) -> Path:
    """Resolve one public Site Product image to its exact finalized Local file.

    github_raw Social delivery must be independent from Site/WAF HTTP. Matching
    therefore uses the canonical public SEO basename plus the server SHA-prefix
    when present, and re-verifies the full finalized SHA before returning bytes.
    """
    public_url = str(public_url or "").strip()
    parsed = urllib_parse.urlparse(public_url)
    basename = urllib_parse.unquote(PurePosixPath(parsed.path).name)
    parts = [urllib_parse.unquote(value) for value in PurePosixPath(parsed.path).parts]
    sha_prefix = ""
    if len(parts) >= 2 and re.fullmatch(r"[0-9a-fA-F]{8,64}", parts[-2] or ""):
        sha_prefix = parts[-2].lower()

    matches: list[Path] = []
    for item in _json_list(row.get("image_metadata_json")):
        if not isinstance(item, dict):
            continue
        final_value = str(item.get("final_local_file") or "").strip()
        if not final_value:
            continue
        path = Path(final_value).expanduser().resolve()
        seo_name = str(item.get("seo_filename") or path.name or "").strip()
        if basename and seo_name and basename != seo_name:
            continue
        final_sha = str(item.get("final_sha256") or "").strip().lower()
        if sha_prefix and final_sha and not final_sha.startswith(sha_prefix):
            continue
        if not path.is_file():
            continue
        actual_sha = _sha256(path)
        if final_sha and actual_sha != final_sha:
            raise RuntimeError(
                f"Finalized Local Social media SHA drift for {path.name}: "
                f"expected={final_sha} actual={actual_sha}"
            )
        matches.append(path)

    unique = list(dict.fromkeys(matches))
    if len(unique) != 1:
        raise RuntimeError(
            "Exact finalized Local Social media could not be resolved for "
            f"{public_url}: matches={len(unique)}"
        )
    return unique[0]


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


MAX_INSTAGRAM_FEED_IMAGES = 10


def prepare_all_current_product_feed_assets(
    db,
    product_id: int,
    settings: SiteConnection,
    *,
    publish_to_site: bool = True,
) -> dict:
    """Prepare every current canonical Product image for one Instagram Feed post.

    This intentionally does not use ``selected_images_json``. The owner contract
    for Instagram Feed is all current Product images, while file safety remains
    the O2E rule: exact bytes must resolve inside the current Product local_dir.
    """
    row_obj = db.product(int(product_id))
    if row_obj is None:
        raise RuntimeError(f"Product {product_id} not found")
    row = dict(row_obj)
    from .phase50_a2w_media_sync import current_product_local_media
    from .social_content_policy import build_alt_texts

    current = current_product_local_media(row)
    if not current:
        raise RuntimeError("No current Product media is available for Instagram feed.")
    if len(current) > MAX_INSTAGRAM_FEED_IMAGES:
        raise RuntimeError(
            "Instagram/Buffer accepts at most 10 images in one Feed carousel; "
            f"this Product has {len(current)} current images. Nothing was published."
        )

    source_urls = [str(item["source_url"]) for item in current]
    alt_texts = build_alt_texts(row, source_urls)
    revision = _revision_key(row)
    local_root = Path(
        os.environ.get("LOCALAPPDATA")
        or (Path.home() / "AppData" / "Local")
    ) / "3DPrintHub" / "instagram" / "feed" / str(int(product_id)) / revision
    local_root.mkdir(parents=True, exist_ok=True)

    local_paths: list[str] = []
    dimensions: list[dict[str, int]] = []
    for index, item in enumerate(current, 1):
        local_source = Path(str(item["local_path"])).resolve()
        source_bytes = local_source.read_bytes()
        if len(source_bytes) > 12 * 1024 * 1024:
            raise RuntimeError(f"Instagram source image {index} is unexpectedly large.")
        with Image.open(BytesIO(source_bytes)) as opened:
            rendered = _instagram_canvas(opened)
        local_file = local_root / f"{index:02d}.png"
        rendered.save(local_file, format="PNG", optimize=True)
        local_paths.append(str(local_file))
        width, height = rendered.size
        dimensions.append({"width": int(width), "height": int(height)})

    public_urls: list[str] = []
    if publish_to_site:
        remote_root = str(
            db.setting(
                "instagram_feed_remote_root",
                "/public_html/media/instagram/feed/products",
            )
            or "/public_html/media/instagram/feed/products"
        ).strip()
        remote_dir = str(PurePosixPath(remote_root) / str(int(product_id)) / revision)
        ftp = connect_ftp(settings)
        try:
            _ensure_remote_dir(ftp, remote_dir)
            for local_value in local_paths:
                local_file = Path(local_value)
                remote_file = str(PurePosixPath(remote_dir) / local_file.name)
                with local_file.open("rb") as handle:
                    ftp.storbinary(
                        f"STOR {remote_file}",
                        handle,
                        blocksize=128 * 1024,
                    )
                public_url = (
                    settings.site_url.rstrip("/")
                    + f"/media/instagram/feed/products/{int(product_id)}/{revision}/{local_file.name}"
                )
                _verify_public_image(
                    public_url,
                    timeout=max(10, int(settings.timeout)),
                )
                public_urls.append(public_url)
        finally:
            try:
                ftp.quit()
            except Exception:
                ftp.close()

    return {
        "urls": public_urls,
        "local_paths": local_paths,
        "source_urls": source_urls,
        "alt_texts": alt_texts,
        "dimensions": dimensions,
        "format": "png",
        "revision": revision,
        "published_to_site": bool(publish_to_site),
        "media_authority": "all_current_product_images",
    }


def prepare_product_feed_assets(
    db,
    product_id: int,
    settings: SiteConnection,
    payload: dict,
    *,
    publish_to_site: bool = True,
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

    local_paths: list[str] = []
    dimensions: list[dict[str, int]] = []
    for index, source_url in enumerate(media_urls, 1):
        if not publish_to_site:
            local_source = resolve_local_product_media(row, source_url)
            source_bytes = local_source.read_bytes()
        else:
            request = urllib_request.Request(
                source_url,
                headers={"User-Agent": "3DPrintHub-Social/3.0"},
            )
            with urllib_request.urlopen(
                request,
                timeout=max(10, int(settings.timeout)),
            ) as response:
                source_bytes = response.read(12 * 1024 * 1024 + 1)
        if len(source_bytes) > 12 * 1024 * 1024:
            raise RuntimeError(f"Instagram source image {index} is unexpectedly large.")

        with Image.open(BytesIO(source_bytes)) as opened:
            rendered = _instagram_canvas(opened)
        local_file = local_root / f"{index:02d}.png"
        rendered.save(local_file, format="PNG", optimize=True)
        local_paths.append(str(local_file))
        width, height = rendered.size
        dimensions.append({"width": int(width), "height": int(height)})

    public_urls: list[str] = []
    if publish_to_site:
        remote_root = str(
            db.setting(
                "instagram_feed_remote_root",
                "/public_html/media/instagram/feed/products",
            )
            or "/public_html/media/instagram/feed/products"
        ).strip()
        remote_dir = str(PurePosixPath(remote_root) / str(int(product_id)) / revision)
        ftp = connect_ftp(settings)
        try:
            _ensure_remote_dir(ftp, remote_dir)
            for index, local_value in enumerate(local_paths, 1):
                local_file = Path(local_value)
                remote_file = str(PurePosixPath(remote_dir) / local_file.name)
                with local_file.open("rb") as handle:
                    ftp.storbinary(
                        f"STOR {remote_file}",
                        handle,
                        blocksize=128 * 1024,
                    )
                public_url = (
                    settings.site_url.rstrip("/")
                    + f"/media/instagram/feed/products/{int(product_id)}/{revision}/{local_file.name}"
                )
                _verify_public_image(
                    public_url,
                    timeout=max(10, int(settings.timeout)),
                )
                public_urls.append(public_url)
        finally:
            try:
                ftp.quit()
            except Exception:
                ftp.close()

    return {
        "urls": public_urls,
        "local_paths": local_paths,
        "source_urls": media_urls,
        "dimensions": dimensions,
        "format": "png",
        "revision": revision,
        "published_to_site": bool(publish_to_site),
    }
