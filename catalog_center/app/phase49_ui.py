from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class GalleryPage:
    page: int
    page_size: int
    total_items: int
    total_pages: int
    start: int
    end: int


def gallery_page(total_items: int, page: int, page_size: int = 40) -> GalleryPage:
    total_items = max(0, int(total_items or 0))
    page_size = max(8, min(int(page_size or 40), 100))
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    page = max(0, min(int(page or 0), total_pages - 1))
    start = page * page_size
    end = min(total_items, start + page_size)
    return GalleryPage(page, page_size, total_items, total_pages, start, end)


def first_site_images(urls, count: int = 5, primary: str = "") -> list[str]:
    clean = list(dict.fromkeys(str(x or "").strip() for x in urls if str(x or "").strip()))
    count = max(1, int(count or 1))
    if primary and primary in clean:
        clean = [primary] + [u for u in clean if u != primary]
    return clean[:count]


def remove_gallery_urls(urls, selected, primary: str, remove_urls) -> tuple[list[str], list[str], str]:
    remove = {str(x or "").strip() for x in remove_urls if str(x or "").strip()}
    clean_urls = [u for u in list(dict.fromkeys(urls)) if u and u not in remove]
    clean_selected = [u for u in list(dict.fromkeys(selected)) if u in clean_urls]
    primary = primary if primary in clean_urls else (clean_selected[0] if clean_selected else (clean_urls[0] if clean_urls else ""))
    if primary and primary not in clean_selected:
        clean_selected.insert(0, primary)
    return clean_urls, clean_selected, primary


def keep_only_gallery_urls(urls, selected, primary: str, keep_urls) -> tuple[list[str], list[str], str]:
    keep = {str(x or "").strip() for x in keep_urls if str(x or "").strip()}
    ordered = [u for u in list(dict.fromkeys(urls)) if u and u in keep]
    selected_ordered = [u for u in list(dict.fromkeys(selected)) if u in ordered]
    primary = primary if primary in ordered else (selected_ordered[0] if selected_ordered else (ordered[0] if ordered else ""))
    if primary and primary not in selected_ordered:
        selected_ordered.insert(0, primary)
    return ordered, selected_ordered, primary


def receipt_lines(row, receipts) -> str:
    parts = [
        f"Product ID: {row['id'] if row is not None else '—'}",
        f"Server ID: {(row['server_id'] if row is not None else '') or '—'}",
        f"Server status: {(row['server_status'] if row is not None else '') or '—'}",
        f"Last sync: {(row['last_synced_at'] if row is not None else '') or '—'}",
        f"Error: {(row['product_sync_error'] if row is not None else '') or '—'}",
        "",
        "=== Receipts ===",
    ]
    for receipt in receipts:
        try:
            payload = json.loads(receipt["payload_json"] or "{}")
        except Exception:
            payload = {"raw": receipt["payload_json"]}
        parts.extend([
            f"[{receipt['created_at']}] status={receipt['status']} batch={receipt['batch_uuid']} server={receipt['server_id'] or '-'}",
            json.dumps(payload, ensure_ascii=False, indent=2),
            "-" * 72,
        ])
    return "\n".join(parts)
