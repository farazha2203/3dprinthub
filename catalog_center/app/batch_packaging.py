from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit

IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif"})
MIN_PACKAGED_IMAGE_BYTES = 256

class BatchImagePackagingError(RuntimeError):
    """Raised when a publishable batch cannot carry its required local images."""


def _row_get(row: Any, key: str, default: Any = "") -> Any:
    if isinstance(row, dict):
        return row.get(key, default)
    try:
        return row[key]
    except Exception:
        return default


def _json_list(value: Any) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
        return list(parsed) if isinstance(parsed, list) else []
    except Exception:
        return []


def selected_image_urls(row: Any) -> tuple[list[str], list[str]]:
    all_urls=[str(x).strip() for x in _json_list(_row_get(row,"images_json","[]")) if str(x).strip()]
    selected=[str(x).strip() for x in _json_list(_row_get(row,"selected_images_json","[]")) if str(x).strip()]
    if not selected:
        selected=list(all_urls)
    selected=list(dict.fromkeys(selected))
    primary=str(_row_get(row,"primary_image_url","") or "").strip()
    if primary:
        if primary not in selected and primary in all_urls:
            selected.insert(0,primary)
        elif primary in selected:
            selected=[primary]+[url for url in selected if url!=primary]
    return all_urls,selected


def _cached_name(url: str) -> str:
    suffix=Path(urlsplit(url).path).suffix.lower()
    if suffix not in IMAGE_EXTENSIONS:
        suffix=".jpg"
    digest=hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
    return f"batch_{digest}{suffix}"


def _valid_local_image(path: Path | None) -> bool:
    try:
        return bool(path and Path(path).is_file() and Path(path).stat().st_size>=MIN_PACKAGED_IMAGE_BYTES)
    except OSError:
        return False


def existing_image_mapping(local_dir: Path, all_urls: list[str]) -> dict[str,Path]:
    local_dir=Path(local_dir)
    mapping={}
    extract_file=local_dir/"page_extract.json"
    if extract_file.is_file():
        try:
            payload=json.loads(extract_file.read_text(encoding="utf-8"))
            for item in payload.get("images",[]):
                if not isinstance(item,dict):
                    continue
                url=str(item.get("url") or "").strip(); local_file=str(item.get("local_file") or "").strip()
                if not url or not local_file:
                    continue
                path=Path(local_file)
                if not path.is_absolute():
                    path=(local_dir/path).resolve()
                if _valid_local_image(path):
                    mapping[url]=path
        except Exception:
            pass
    image_dir=local_dir/"images"
    for url in all_urls:
        if url.startswith("local://"):
            candidate=image_dir/url.split("local://",1)[1]
            if _valid_local_image(candidate):
                mapping[url]=candidate
    for url in all_urls:
        if url in mapping:
            continue
        candidate=image_dir/_cached_name(url)
        if _valid_local_image(candidate):
            mapping[url]=candidate
    if not mapping and image_dir.is_dir():
        local_files=sorted(path for path in image_dir.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS and _valid_local_image(path))
        for index,url in enumerate(all_urls):
            if index<len(local_files):
                mapping[url]=local_files[index]
    return mapping


def materialize_selected_images(row: Any, local_dir: Path, *, downloader: Callable[[str,Path,str],Path]) -> list[tuple[str,Path]]:
    local_dir=Path(local_dir)
    all_urls,selected=selected_image_urls(row)
    product_id=_row_get(row,"id","?")
    if not selected:
        raise BatchImagePackagingError(f"IMAGE_NOT_PACKAGED: product #{product_id} has no selected image.")
    mapping=existing_image_mapping(local_dir,all_urls)
    image_dir=local_dir/"images"
    referer=str(_row_get(row,"source_url","") or "").strip()
    resolved=[]
    for index,url in enumerate(selected,start=1):
        local_file=mapping.get(url)
        if not _valid_local_image(local_file):
            if url.startswith("local://"):
                raise BatchImagePackagingError(f"IMAGE_NOT_PACKAGED: local image is missing for product #{product_id}: {url}")
            if not url.startswith(("http://","https://")):
                raise BatchImagePackagingError(f"IMAGE_NOT_PACKAGED: unsupported image URL for product #{product_id}: {url}")
            image_dir.mkdir(parents=True,exist_ok=True)
            target=image_dir/_cached_name(url)
            try:
                local_file=Path(downloader(url,target,referer))
            except Exception as exc:
                raise BatchImagePackagingError(f"IMAGE_NOT_PACKAGED: download failed for product #{product_id} image {index}: {type(exc).__name__}: {exc}") from exc
            if not _valid_local_image(local_file):
                try: Path(local_file).unlink(missing_ok=True)
                except Exception: pass
                raise BatchImagePackagingError(f"IMAGE_NOT_PACKAGED: downloaded image is empty/invalid for product #{product_id} image {index}.")
            mapping[url]=local_file
        resolved.append((url,Path(local_file)))
    return resolved


def copy_images_into_model(selected_pairs: list[tuple[str,Path]], model_dir: Path) -> list[str]:
    image_target=Path(model_dir)/"images"
    local_names=[]
    for index,(_url,local_file) in enumerate(selected_pairs,start=1):
        local_file=Path(local_file)
        if not _valid_local_image(local_file):
            raise BatchImagePackagingError(f"IMAGE_NOT_PACKAGED: source image vanished before copy: {local_file}")
        suffix=local_file.suffix.lower()
        if suffix not in IMAGE_EXTENSIONS:
            suffix=".jpg"
        image_target.mkdir(parents=True,exist_ok=True)
        local_name=f"{index:03d}{suffix}"
        destination=image_target/local_name
        shutil.copy2(local_file,destination)
        if not _valid_local_image(destination):
            raise BatchImagePackagingError(f"IMAGE_NOT_PACKAGED: copied batch image is invalid: {destination}")
        local_names.append(local_name)
    return local_names


def validate_batch_package(batch: Path) -> dict[str,int]:
    batch=Path(batch).resolve(); manifest_path=batch/"batch_manifest.json"
    if not manifest_path.is_file():
        raise BatchImagePackagingError(f"Batch manifest not found: {manifest_path}")
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    if str(manifest.get("schema_version") or "")!="8.5":
        raise BatchImagePackagingError("Batch schema must be 8.5.")
    expected_name=batch.name[:-9] if batch.name.endswith(".building") else batch.name
    if str(manifest.get("batch_name") or "")!=expected_name:
        raise BatchImagePackagingError("Batch directory and manifest names do not match.")
    if not str(manifest.get("batch_uuid") or "").strip():
        raise BatchImagePackagingError("Batch UUID is missing.")
    models=manifest.get("models")
    if not isinstance(models,list) or not models:
        raise BatchImagePackagingError("Batch has no models.")
    checked_models=checked_images=0
    for item in models:
        if not isinstance(item,dict):
            raise BatchImagePackagingError("Batch manifest contains an invalid model row.")
        editorial_relative=str(item.get("editorial") or "").strip(); editorial_path=(batch/editorial_relative).resolve()
        try: editorial_path.relative_to(batch)
        except ValueError as exc: raise BatchImagePackagingError("Editorial path escapes the batch root.") from exc
        if not editorial_path.is_file():
            raise BatchImagePackagingError(f"Editorial file not found: {editorial_relative}")
        data=json.loads(editorial_path.read_text(encoding="utf-8"))
        selected=_json_list(data.get("images_json")); mapped=_json_list(data.get("local_image_files_json"))
        wants_publish=bool(data.get("publish_as_product") or data.get("publish_as_portfolio"))
        if wants_publish:
            if not selected:
                raise BatchImagePackagingError(f"IMAGE_NOT_PACKAGED: publishable product #{data.get('desktop_product_id')} has no image.")
            if len(mapped)!=len(selected):
                raise BatchImagePackagingError(f"IMAGE_NOT_PACKAGED: product #{data.get('desktop_product_id')} does not have one local mapping per selected image.")
            if any(not str(name or "").strip() for name in mapped):
                raise BatchImagePackagingError(f"IMAGE_NOT_PACKAGED: product #{data.get('desktop_product_id')} has an empty local-image mapping.")
        image_dir=editorial_path.parent/"images"
        for name in mapped:
            name=str(name or "").strip()
            if not name: continue
            candidate=(image_dir/Path(name).name).resolve()
            if candidate.parent!=image_dir.resolve():
                raise BatchImagePackagingError("Batch image path escapes its image directory.")
            if not _valid_local_image(candidate):
                raise BatchImagePackagingError(f"IMAGE_NOT_PACKAGED: batch image missing/empty: {candidate}")
            checked_images+=1
        if wants_publish and (not mapped or not str(mapped[0] or "").strip()):
            raise BatchImagePackagingError(f"IMAGE_NOT_PACKAGED: primary image mapping is empty for product #{data.get('desktop_product_id')}.")
        checked_models+=1
    return {"models":checked_models,"images":checked_images}
