from __future__ import annotations

import asyncio
import hashlib
import io
import json
import re
import threading
import time
import unicodedata
from pathlib import Path
from typing import Any
from urllib import parse as urlparse
from urllib import request as urlrequest

import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

from .db import normalize_url, utc_now
from .classic_methods import launch_fresh_browser, makerworld_model_id
from .phase49_3h_image_limits import normalize_image_limit
from .v8_features import product_fingerprint, source_payload_hash


CANDIDATE_TABLE = "phase49_3i_discovery_candidates"
CANDIDATE_STATUSES = {"review", "approved", "imported", "blocked", "existing", "failed"}


def is_http_url(value: str) -> bool:
    try:
        parsed = urlparse.urlsplit(str(value or "").strip())
    except Exception:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def is_listing_or_search_url(value: str) -> bool:
    if not is_http_url(value):
        return False
    parsed = urlparse.urlsplit(str(value).strip())
    path = parsed.path.lower()
    query = parsed.query.lower()
    return (
        "/search" in path
        or "keyword=" in query
        or "orderby=" in query
        or path.rstrip("/").endswith(("/models", "/3d-models", "/model"))
    )


def resolve_discovery_targets(mode: str, seed: str, listing_urls: list[str], encoded_query: str) -> tuple[list[str], int]:
    """Resolve discovery targets without silently overriding an explicit URL.

    The Phase49.3I invariant is simple: a valid operator-supplied HTTP(S) seed
    wins for search/category/site crawl/automatic discovery. Configured listing
    URLs are only a fallback when no explicit URL was supplied.
    """
    mode = str(mode or "automatic").strip().lower()
    seed = str(seed or "").strip()
    listings = [str(item or "").strip() for item in listing_urls or [] if str(item or "").strip()]
    if is_http_url(seed) and mode in {"search", "category", "site_crawl", "automatic"}:
        return [seed], 1
    if mode in {"category", "site_crawl"}:
        return ([seed] if is_http_url(seed) else []), 1
    if mode == "search":
        return listings[:1], 8
    if is_http_url(seed):
        return [seed], 1
    return listings[:1], 10


def _latin_safe_char(char: str) -> str:
    if char in "\n\r\t":
        return " "
    code = ord(char)
    if code < 128:
        return char if code >= 32 else ""
    category = unicodedata.category(char)
    name = unicodedata.name(char, "")
    if category.startswith("L"):
        return char if "LATIN" in name else ""
    if category.startswith("N"):
        return char if "DIGIT" in name and code < 128 else ""
    if category.startswith("P") or category.startswith("Z"):
        return char
    # Keep a small technical-symbol allowlist; discard emoji and decorative glyphs.
    if char in {"°", "µ", "×", "±", "%", "€", "£", "$", "¥", "−"}:
        return char
    return ""


def sanitize_source_text(value: Any, max_length: int | None = None) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    cleaned = "".join(_latin_safe_char(char) for char in text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if max_length is not None:
        cleaned = cleaned[: max(0, int(max_length))]
    return cleaned


def _sanitize_source_value(value, key: str = ""):
    key_cf = str(key or "").casefold()
    if isinstance(value, dict):
        return {str(k): _sanitize_source_value(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_source_value(item, key) for item in value]
    if not isinstance(value, str):
        return value
    if "url" in key_cf or value.startswith(("http://", "https://", "local://")):
        return value
    return sanitize_source_text(value)


def _sanitize_json_text(value: Any, default):
    if isinstance(value, type(default)):
        parsed = value
    else:
        try:
            parsed = json.loads(value or json.dumps(default))
        except Exception:
            parsed = default
    cleaned = _sanitize_source_value(parsed)
    return json.dumps(cleaned, ensure_ascii=False)


def sanitize_source_payload(data: dict) -> dict:
    """Sanitize only scraped/source fields; Persian editorial fields are untouched."""
    output = dict(data or {})
    text_limits = {
        "source_title": 500,
        "source_short_description": 1000,
        "source_description": None,
        "author_name": 500,
        "license_name": 500,
        "source_category": 500,
        "source_currency": 50,
    }
    for key, limit in text_limits.items():
        if key in output:
            output[key] = sanitize_source_text(output.get(key), limit)
    for key, default in {
        "source_categories_json": [],
        "tags_json": [],
        "source_specs_json": {},
        "source_snapshot_json": {},
    }.items():
        if key in output:
            output[key] = _sanitize_json_text(output.get(key), default)
    # Explicitly never touch URLs, source identity, downloaded filenames, or Persian fields.
    return output


def ensure_schema(db) -> None:
    db.conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {CANDIDATE_TABLE}(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_code TEXT NOT NULL,
            external_id TEXT NOT NULL,
            source_url TEXT NOT NULL,
            normalized_url TEXT NOT NULL,
            source_title TEXT NOT NULL DEFAULT '',
            thumbnail_url TEXT NOT NULL DEFAULT '',
            discovered_from TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'review',
            product_id INTEGER,
            last_error TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(source_code, external_id)
        )
        """
    )
    db.conn.execute(
        f"CREATE INDEX IF NOT EXISTS ix_{CANDIDATE_TABLE}_status ON {CANDIDATE_TABLE}(status, id DESC)"
    )
    db.conn.commit()


def known_product(db, source_code: str, external_id: str, normalized: str):
    return db.conn.execute(
        """
        SELECT * FROM products
        WHERE source_code=?
          AND ((external_id<>'' AND external_id=?) OR normalized_url=?)
        ORDER BY is_blocked DESC, id
        LIMIT 1
        """,
        (str(source_code or ""), str(external_id or ""), str(normalized or "")),
    ).fetchone()


def candidate_status_for_known(row) -> str:
    if row is None:
        return "review"
    return "blocked" if int(row["is_blocked"] or 0) else "existing"


def upsert_candidate(db, candidate: dict) -> int:
    ensure_schema(db)
    source_code = str(candidate.get("source_code") or "").strip()
    external_id = str(candidate.get("external_id") or "").strip()
    source_url = str(candidate.get("source_url") or "").strip()
    if not source_code or not external_id or not is_http_url(source_url):
        raise ValueError("Candidate source identity is incomplete")
    normalized = normalize_url(source_url)
    known = known_product(db, source_code, external_id, normalized)
    incoming_status = candidate_status_for_known(known)
    now = utc_now()
    existing = db.conn.execute(
        f"SELECT * FROM {CANDIDATE_TABLE} WHERE source_code=? AND external_id=?",
        (source_code, external_id),
    ).fetchone()
    title = sanitize_source_text(candidate.get("source_title"), 500)
    thumb = str(candidate.get("thumbnail_url") or "").strip()
    if not is_http_url(thumb):
        thumb = ""
    if existing:
        preserved = str(existing["status"] or "review")
        if preserved in {"imported", "blocked", "existing"}:
            incoming_status = preserved
        db.conn.execute(
            f"""
            UPDATE {CANDIDATE_TABLE}
            SET source_url=?, normalized_url=?, source_title=?, thumbnail_url=?,
                discovered_from=?, status=?, product_id=?, last_error='', updated_at=?
            WHERE id=?
            """,
            (
                source_url,
                normalized,
                title or str(existing["source_title"] or ""),
                thumb or str(existing["thumbnail_url"] or ""),
                str(candidate.get("discovered_from") or existing["discovered_from"] or ""),
                incoming_status,
                int(known["id"]) if known else existing["product_id"],
                now,
                int(existing["id"]),
            ),
        )
        candidate_id = int(existing["id"])
    else:
        cursor = db.conn.execute(
            f"""
            INSERT INTO {CANDIDATE_TABLE}(
                source_code,external_id,source_url,normalized_url,source_title,
                thumbnail_url,discovered_from,status,product_id,created_at,updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                source_code,
                external_id,
                source_url,
                normalized,
                title,
                thumb,
                str(candidate.get("discovered_from") or ""),
                incoming_status,
                int(known["id"]) if known else None,
                now,
                now,
            ),
        )
        candidate_id = int(cursor.lastrowid)
    db.conn.commit()
    return candidate_id


def candidate_rows(db, limit: int = 300):
    ensure_schema(db)
    return list(
        db.conn.execute(
            f"SELECT * FROM {CANDIDATE_TABLE} ORDER BY id DESC LIMIT ?",
            (max(1, int(limit)),),
        )
    )


def candidate_row(db, candidate_id: int):
    ensure_schema(db)
    return db.conn.execute(f"SELECT * FROM {CANDIDATE_TABLE} WHERE id=?", (int(candidate_id),)).fetchone()


def candidate_by_identity(db, source_code: str, external_id: str):
    ensure_schema(db)
    return db.conn.execute(
        f"SELECT * FROM {CANDIDATE_TABLE} WHERE source_code=? AND external_id=?",
        (str(source_code or ""), str(external_id or "")),
    ).fetchone()


def candidate_preview_cache_path(source_code: str, external_id: str) -> Path:
    """Stable cache path shared by the legacy Preview UI and the Qt review gallery."""
    from .runtime_paths import data_root

    safe_source = re.sub(r"[^A-Za-z0-9._-]+", "-", str(source_code or "source")).strip(".-")
    safe_external = re.sub(r"[^A-Za-z0-9._-]+", "-", str(external_id or "candidate")).strip(".-")
    folder = data_root() / "discovery_previews" / (safe_source or "source")
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{(safe_external or 'candidate')[:160]}.jpg"


def set_candidate_status(db, candidate_id: int, status: str, *, product_id=None, error: str = "") -> None:
    status = str(status or "review")
    if status not in CANDIDATE_STATUSES:
        status = "failed"
    db.conn.execute(
        f"UPDATE {CANDIDATE_TABLE} SET status=?, product_id=?, last_error=?, updated_at=? WHERE id=?",
        (status, int(product_id) if product_id else None, str(error or "")[:2000], utc_now(), int(candidate_id)),
    )
    db.conn.commit()


def _candidate_title(text: str, external_id: str) -> str:
    lines = [sanitize_source_text(line, 300) for line in str(text or "").splitlines()]
    lines = [line for line in lines if line]
    for line in lines:
        if len(line) >= 3 and line != external_id:
            return line
    return f"MakerWorld model {external_id}" if external_id else "3D model"


def candidates_from_dom_rows(rows: list[dict], model_pattern: str, discovered_from: str, source_code: str, limit: int) -> list[dict]:
    regex = re.compile(model_pattern, re.I)
    output = []
    seen = set()
    for row in rows or []:
        href = str((row or {}).get("href") or "").strip()
        match = regex.search(href)
        if not match:
            continue
        matched_url = match.group(0)
        external_id = (
            match.groupdict().get("external_id")
            or makerworld_model_id(matched_url)
            or hashlib.sha1(normalize_url(matched_url).encode("utf-8")).hexdigest()[:16]
        )
        identity = (source_code, external_id)
        if identity in seen:
            continue
        seen.add(identity)
        image_url = str((row or {}).get("image") or "").strip()
        output.append({
            "source_code": source_code,
            "external_id": external_id,
            "source_url": matched_url,
            "source_title": _candidate_title(str((row or {}).get("text") or ""), external_id),
            "thumbnail_url": image_url if is_http_url(image_url) else "",
            "discovered_from": discovered_from,
        })
        if len(output) >= max(1, int(limit)):
            break
    return output


async def discover_preview_candidates(
    listing_url: str,
    *,
    source_code: str,
    model_pattern: str,
    requested: int,
    scroll_rounds: int = 8,
    headed: bool = False,
) -> list[dict]:
    """Read candidate cards from the listing page only; never open product pages."""
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser, _browser_label = await launch_fresh_browser(playwright, headed=headed)
        try:
            context = await browser.new_context(
                locale="en-US",
                viewport={"width": 1440, "height": 1100},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
                ),
            )
            page = await context.new_page()
            response = await page.goto(listing_url, wait_until="domcontentloaded", timeout=90_000)
            if response and response.status in {403, 429}:
                raise RuntimeError(f"Discovery page returned HTTP {response.status}")
            await page.wait_for_timeout(3500)
            previous_height = 0
            for _ in range(max(0, int(scroll_rounds))):
                height = await page.evaluate("() => document.documentElement.scrollHeight")
                await page.evaluate("() => window.scrollTo(0, document.documentElement.scrollHeight)")
                await page.wait_for_timeout(1200)
                if height == previous_height:
                    break
                previous_height = height
            rows = await page.locator("a[href]").evaluate_all(
                """els => els.map(a => {
                    const host = a.closest('article, li, [class*="card"], [class*="model"], [class*="item"]') || a.parentElement || a;
                    const img = (host && host.querySelector('img')) || a.querySelector('img');
                    return {
                        href: a.href || '',
                        text: ((a.innerText || '') + '\n' + ((host && host.innerText) || '')).trim().slice(0, 900),
                        image: img ? (img.currentSrc || img.src || img.getAttribute('data-src') || '') : ''
                    };
                })"""
            )
            return candidates_from_dom_rows(rows, model_pattern, page.url or listing_url, source_code, requested)
        finally:
            await browser.close()


def _source_defaults(source_cfg: dict | None, image_limit: int) -> dict:
    return {
        "reference_only": int(bool((source_cfg or {}).get("reference_only", False))),
        "suggested_price": 500000,
        "final_price": 0,
        "price_is_final": 0,
        "approved_for_sale": 0,
        "publish_as_product": 1,
        "publish_as_portfolio": 0,
        "translation_status": "pending",
        "commercial_status": "review",
        "local_category_slug": "external-other",
        "material_price_per_gram": 0,
        "workflow_status": "review",
        "upload_ready": 0,
        "custom_notes": "",
        "content_status": "pending",
        "needs_update": 0,
        "product_sync_error": "",
        "download_image_limit": normalize_image_limit(image_limit),
    }


def _resolve_product_id(db, source_code: str, external_id: str, normalized: str) -> int | None:
    row = known_product(db, source_code, external_id, normalized)
    return int(row["id"]) if row is not None else None


def archive_candidate(db, candidate_id: int, reason: str = "Discovery review: archive / not needed") -> int | None:
    row = candidate_row(db, candidate_id)
    if row is None:
        return None
    known = known_product(db, row["source_code"], row["external_id"], row["normalized_url"])
    if known is not None:
        if int(known["is_blocked"] or 0):
            set_candidate_status(db, candidate_id, "blocked", product_id=known["id"])
            return int(known["id"])
        # Never silently block an already curated live product merely because it
        # reappeared as a discovery candidate.
        set_candidate_status(db, candidate_id, "existing", product_id=known["id"])
        return int(known["id"])

    minimal = {
        "source_code": row["source_code"],
        "external_id": row["external_id"],
        "source_url": row["source_url"],
        "source_title": sanitize_source_text(row["source_title"], 500),
        "images_json": json.dumps([row["thumbnail_url"]] if row["thumbnail_url"] else [], ensure_ascii=False),
        "selected_images_json": "[]",
        "primary_image_url": row["thumbnail_url"] if is_http_url(row["thumbnail_url"]) else "",
        "reference_only": 1,
        "publish_as_product": 0,
        "publish_as_portfolio": 0,
        "approved_for_sale": 0,
        "upload_ready": 0,
        "workflow_status": "review",
        "commercial_status": "review",
        "local_category_slug": "external-other",
        "download_image_limit": 1,
    }
    db.upsert_product(minimal)
    product_id = _resolve_product_id(db, row["source_code"], row["external_id"], row["normalized_url"])
    if product_id:
        db.block_product(product_id, reason)
        set_candidate_status(db, candidate_id, "blocked", product_id=product_id)
    return product_id


def _walk(root):
    try:
        children = root.winfo_children()
    except Exception:
        children = []
    for child in children:
        yield child
        yield from _walk(child)


def install_app(app_class) -> None:
    if getattr(app_class, "_phase49_3i_discovery_review_installed", False):
        return

    original_scan_ui = app_class._scan_ui
    original_direct = app_class.start_direct_link_import

    def _scan_ui(self):
        original_scan_ui(self)
        ensure_schema(self.db)
        # Legacy one-click full scan is intentionally removed from the public
        # discovery UI. Its underlying code remains for compatibility/tests.
        for widget in _walk(getattr(self, "scan_tab", self)):
            try:
                text = str(widget.cget("text") or "")
            except Exception:
                continue
            if text in {"شروع اسکن", "🔎 کشف جدیدها"}:
                try:
                    widget.pack_forget()
                except Exception:
                    try:
                        widget.grid_remove()
                    except Exception:
                        pass

        frame = ttk.LabelFrame(
            self.scan_tab,
            text="بررسی اولیه محصولات — قبل از دریافت کامل",
            padding=10,
            style="Card.TLabelframe",
        )
        try:
            frame.pack(fill="both", expand=True, pady=(4, 8), before=self.scan_log)
        except Exception:
            frame.pack(fill="both", expand=True, pady=(4, 8))
        head = ttk.Frame(frame)
        head.pack(fill="x", pady=(0, 7))
        ttk.Button(
            head,
            text="1) کشف و پیش‌نمایش",
            command=self.start_candidate_discovery,
            style="Primary.TButton",
        ).pack(side="left", padx=3)
        ttk.Button(
            head,
            text="2) تأیید و دریافت کامل انتخاب‌شده‌ها",
            command=self.approve_discovery_candidates,
            style="Success.TButton",
        ).pack(side="left", padx=3)
        ttk.Button(
            head,
            text="آرشیو / لازم نیست",
            command=self.archive_discovery_candidates,
            style="Danger.TButton",
        ).pack(side="left", padx=3)
        ttk.Button(head, text="باز کردن لینک", command=self.open_discovery_candidate_url).pack(side="left", padx=3)
        ttk.Button(head, text="بروزرسانی لیست", command=self.refresh_discovery_candidates).pack(side="left", padx=3)
        ttk.Label(
            head,
            text="پیش‌نمایش فقط یک تصویر/عنوان می‌گیرد؛ دریافت کامل فقط بعد از تأیید انجام می‌شود.",
            style="SubHeader.TLabel",
        ).pack(side="right", padx=5)

        style = ttk.Style(self)
        style.configure("Phase493ICandidate.Treeview", rowheight=72)
        tree_shell = ttk.Frame(frame)
        tree_shell.pack(fill="both", expand=True)
        cols = ("status", "title", "source", "external", "url")
        self.discovery_candidate_tree = ttk.Treeview(
            tree_shell,
            columns=cols,
            show="tree headings",
            selectmode="extended",
            style="Phase493ICandidate.Treeview",
            height=7,
        )
        self.discovery_candidate_tree.heading("#0", text="تصویر")
        self.discovery_candidate_tree.column("#0", width=110, minwidth=90, anchor="center", stretch=False)
        for key, title, width in (
            ("status", "وضعیت", 110),
            ("title", "نام محصول", 360),
            ("source", "منبع", 90),
            ("external", "شناسه", 100),
            ("url", "لینک محصول", 520),
        ):
            self.discovery_candidate_tree.heading(key, text=title)
            self.discovery_candidate_tree.column(key, width=width, anchor="w" if key in {"title", "url"} else "center")
        ybar = ttk.Scrollbar(tree_shell, orient="vertical", command=self.discovery_candidate_tree.yview)
        xbar = ttk.Scrollbar(tree_shell, orient="horizontal", command=self.discovery_candidate_tree.xview)
        self.discovery_candidate_tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        self.discovery_candidate_tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        tree_shell.rowconfigure(0, weight=1)
        tree_shell.columnconfigure(0, weight=1)
        self._phase49_3i_candidate_photos = {}
        self._phase49_3i_thumb_loading = set()
        self.refresh_discovery_candidates()

    def _selected_candidate_ids(self):
        tree = getattr(self, "discovery_candidate_tree", None)
        if tree is None:
            return []
        output = []
        for iid in tree.selection():
            match = re.fullmatch(r"candidate-(\d+)", str(iid))
            if match:
                output.append(int(match.group(1)))
        return output

    def _candidate_cache_path(self, row):
        folder = Path(self.DATA) / "discovery_previews" / str(row["source_code"] or "unknown")
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{row['external_id']}.jpg"

    def _apply_candidate_thumb(self, candidate_id: int, raw: bytes):
        tree = getattr(self, "discovery_candidate_tree", None)
        if tree is None or not tree.winfo_exists():
            return
        iid = f"candidate-{candidate_id}"
        if not tree.exists(iid):
            return
        try:
            image = Image.open(io.BytesIO(raw)).convert("RGB")
            image.thumbnail((92, 62), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
        except Exception:
            return
        self._phase49_3i_candidate_photos[candidate_id] = photo
        tree.item(iid, image=photo)

    def _load_candidate_thumb(self, row):
        candidate_id = int(row["id"])
        if candidate_id in self._phase49_3i_thumb_loading:
            return
        cache = self._candidate_cache_path(row)
        if cache.is_file():
            try:
                self._apply_candidate_thumb(candidate_id, cache.read_bytes())
            except Exception:
                pass
            return
        url = str(row["thumbnail_url"] or "").strip()
        if not is_http_url(url):
            return
        self._phase49_3i_thumb_loading.add(candidate_id)

        def worker():
            raw = b""
            try:
                req = urlrequest.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0", "Referer": str(row["discovered_from"] or row["source_url"])},
                )
                with urlrequest.urlopen(req, timeout=20) as response:
                    content_type = str(response.headers.get("Content-Type") or "").lower()
                    if content_type and not content_type.startswith("image/"):
                        return
                    raw = response.read(5_000_001)
                    if not raw or len(raw) > 5_000_000:
                        return
                cache.write_bytes(raw)
            except Exception:
                return
            finally:
                self._phase49_3i_thumb_loading.discard(candidate_id)
            self.after(0, lambda: self._apply_candidate_thumb(candidate_id, raw))

        threading.Thread(target=worker, daemon=True).start()

    def refresh_discovery_candidates(self):
        tree = getattr(self, "discovery_candidate_tree", None)
        if tree is None:
            return
        for iid in tree.get_children():
            tree.delete(iid)
        labels = {
            "review": "نیازمند بررسی",
            "approved": "تأیید شده",
            "imported": "دریافت کامل شد",
            "blocked": "آرشیو / بلاک",
            "existing": "قبلاً موجود",
            "failed": "خطا",
        }
        rows = candidate_rows(self.db)
        for row in rows:
            iid = f"candidate-{row['id']}"
            tree.insert(
                "",
                "end",
                iid=iid,
                text="",
                values=(
                    labels.get(str(row["status"]), str(row["status"])),
                    row["source_title"] or f"Model {row['external_id']}",
                    row["source_code"],
                    row["external_id"],
                    row["source_url"],
                ),
            )
            self._load_candidate_thumb(row)

    def start_candidate_discovery(self):
        if getattr(self, "scan_running", False):
            return
        code = self.source_map.get(self.source_var.get(), "")
        src = self.db.source(code)
        if not src:
            messagebox.showwarning("3DPrintHub", "ابتدا منبع را انتخاب کن.", parent=self)
            return
        seed = self.seed_var.get().strip()
        mode = self.mode_var.get().strip().lower()
        query = self.query_var.get().strip()
        requested = max(1, int(self.limit_var.get() or 1))
        try:
            listings = json.loads(src["listing_urls_json"] or "[]")
        except Exception:
            listings = []
        encoded = urlparse.quote_plus(query or "3d print")
        targets, max_pages = resolve_discovery_targets(mode, seed, listings, encoded)
        if not targets:
            messagebox.showwarning("3DPrintHub", "لینک Search/Listing معتبر یا Listing پیش‌فرض پیدا نشد.", parent=self)
            return
        self.scan_running = True
        self.stop_requested = False
        run_id = self.db.create_run(code, "preview", "review_preview", requested)
        self.status.set("در حال ساخت پیش‌نمایش محصولات؛ هنوز دریافت کامل انجام نمی‌شود…")
        self.log(f"PHASE49_3I_PREVIEW_START source={code} requested={requested} seed={seed}")

        def worker():
            discovered = failed = 0
            try:
                async def execute():
                    nonlocal discovered, failed
                    enough = False
                    for page_no in range(1, max_pages + 1):
                        if enough or self.stop_requested:
                            break
                        for template in targets:
                            try:
                                target = template.format(query=encoded, page=page_no)
                            except Exception:
                                target = template
                            self.log(f"PHASE49_3I_PREVIEW_TARGET={target}")
                            try:
                                candidates = await discover_preview_candidates(
                                    target,
                                    source_code=code,
                                    model_pattern=src["model_url_pattern"],
                                    requested=max(1, requested - discovered),
                                    scroll_rounds=8,
                                    headed=False,
                                )
                                for candidate in candidates:
                                    upsert_candidate(self.db, candidate)
                                    discovered += 1
                                    if discovered >= requested:
                                        enough = True
                                        break
                            except Exception as exc:
                                failed += 1
                                self.log(f"PHASE49_3I_PREVIEW_FAILED {type(exc).__name__}: {exc}")
                            if enough:
                                break
                        if not enough and page_no < max_pages:
                            await asyncio.sleep(2)
                asyncio.run(execute())
                self.db.finish_run(
                    run_id,
                    status="completed" if not failed else "completed_with_errors",
                    discovered_count=discovered,
                    collected_count=0,
                    duplicate_count=0,
                    failed_count=failed,
                    message=f"Preview candidates={discovered}; full fetch=0",
                )
            except Exception as exc:
                self.db.finish_run(
                    run_id,
                    status="failed",
                    discovered_count=discovered,
                    collected_count=0,
                    duplicate_count=0,
                    failed_count=failed + 1,
                    message=str(exc),
                )
                self.events.put(("error", f"پیش‌نمایش کشف ناموفق بود: {type(exc).__name__}: {exc}"))
            finally:
                self.scan_running = False
                self.after(0, self.refresh_discovery_candidates)
                self.after(0, lambda: self.status.set(f"پیش‌نمایش آماده: {discovered} کاندیدا؛ دریافت کامل هنوز انجام نشده است"))
                self.log(f"PHASE49_3I_PREVIEW_END candidates={discovered} failed={failed} full_fetch=0")

        threading.Thread(target=worker, daemon=True).start()

    def approve_discovery_candidates(self):
        ids = self._selected_candidate_ids()
        if not ids:
            messagebox.showwarning("3DPrintHub", "حداقل یک کاندیدا را انتخاب کن.", parent=self)
            return
        image_limit = normalize_image_limit(self.direct_image_limit.get() if hasattr(self, "direct_image_limit") else 10)
        if not messagebox.askyesno(
            "3DPrintHub — دریافت کامل",
            f"{len(ids)} محصول انتخاب شده است.\nبرای هر محصول حداکثر {image_limit} تصویر دریافت شود؟\n\nفقط موارد تأییدشده Full Fetch می‌شوند.",
            parent=self,
        ):
            return
        self.scan_running = True
        self.status.set("در حال دریافت کامل موارد تأییدشده…")

        def worker():
            imported = existing = blocked = failed = 0
            from . import page_extractor as page_extractor_module
            from . import main as main_module

            for index, candidate_id in enumerate(ids, start=1):
                row = candidate_row(self.db, candidate_id)
                if row is None:
                    continue
                known = known_product(self.db, row["source_code"], row["external_id"], row["normalized_url"])
                if known is not None:
                    status = candidate_status_for_known(known)
                    set_candidate_status(self.db, candidate_id, status, product_id=known["id"])
                    if status == "blocked":
                        blocked += 1
                    else:
                        existing += 1
                    self.log(f"PHASE49_3I_FULL_SKIP candidate={candidate_id} product={known['id']} status={status}")
                    continue
                set_candidate_status(self.db, candidate_id, "approved")
                try:
                    local_dir = Path(self.DATA) / "collected" / row["source_code"] / row["external_id"]
                    self.log(f"PHASE49_3I_FULL_FETCH [{index}/{len(ids)}] {row['source_url']} images={image_limit}")
                    data = asyncio.run(
                        page_extractor_module.extract_direct_link(
                            row["source_url"],
                            local_dir,
                            main_module.PROFILE_ROOT / row["source_code"],
                            headed=bool((self.config.get("direct_link") or {}).get("headed", True)),
                            download_images=True,
                            image_limit=image_limit,
                        )
                    )
                    data = sanitize_source_payload(data)
                    data["source_code"] = row["source_code"]
                    data["external_id"] = row["external_id"]
                    data["source_url"] = str(data.get("source_url") or row["source_url"])
                    data["normalized_url"] = normalize_url(data["source_url"])
                    data["local_dir"] = str(data.get("local_dir") or local_dir)
                    data["fingerprint"] = product_fingerprint(data["source_code"], data["external_id"], data["source_url"])
                    data["source_hash"] = source_payload_hash(data)
                    data["last_refetched_at"] = utc_now()
                    data["source_state"] = "active"
                    source_cfg = next((x for x in self.config.get("sources", []) if x.get("code") == row["source_code"]), None)
                    for key, value in _source_defaults(source_cfg, image_limit).items():
                        data.setdefault(key, value)
                    self.db.upsert_product(data)
                    product_id = _resolve_product_id(self.db, row["source_code"], row["external_id"], data["normalized_url"])
                    if not product_id:
                        raise RuntimeError("Product row was not resolved after approved full fetch")
                    self.db.save_history(product_id, "phase49_3i_approved_full_fetch", {}, data, f"Approved discovery candidate #{candidate_id}; image_limit={image_limit}")
                    set_candidate_status(self.db, candidate_id, "imported", product_id=product_id)
                    imported += 1
                except Exception as exc:
                    failed += 1
                    set_candidate_status(self.db, candidate_id, "failed", error=f"{type(exc).__name__}: {exc}")
                    self.log(f"PHASE49_3I_FULL_FAILED candidate={candidate_id} {type(exc).__name__}: {exc}")
            self.scan_running = False
            self.after(0, self.refresh_discovery_candidates)
            self.after(0, self.refresh_products)
            self.after(0, lambda: self.status.set(f"دریافت کامل: {imported} جدید، {existing} قبلی، {blocked} بلاک، {failed} خطا"))

        threading.Thread(target=worker, daemon=True).start()

    def archive_discovery_candidates(self):
        ids = self._selected_candidate_ids()
        if not ids:
            messagebox.showwarning("3DPrintHub", "حداقل یک کاندیدا را انتخاب کن.", parent=self)
            return
        if not messagebox.askyesno(
            "آرشیو / لازم نیست",
            f"{len(ids)} کاندیدا بدون دریافت کامل به فهرست بلاک/لازم‌نیست منتقل شوند؟\nرکورد هویتی حذف نمی‌شود تا دوباره دریافت نشوند.",
            parent=self,
        ):
            return
        changed = 0
        for candidate_id in ids:
            try:
                archive_candidate(self.db, candidate_id)
                changed += 1
            except Exception as exc:
                set_candidate_status(self.db, candidate_id, "failed", error=str(exc))
        self.refresh_discovery_candidates()
        self.refresh_blocked()
        self.refresh_products()
        self.status.set(f"{changed} کاندیدا آرشیو/بلاک شد؛ Full Fetch انجام نشد")

    def open_discovery_candidate_url(self):
        import webbrowser
        ids = self._selected_candidate_ids()
        if not ids:
            return
        row = candidate_row(self.db, ids[0])
        if row and is_http_url(row["source_url"]):
            webbrowser.open(row["source_url"])

    def start_scan(self):
        return self.start_candidate_discovery()

    def start_direct_link_import(self):
        url = self.seed_var.get().strip() if hasattr(self, "seed_var") else ""
        if is_listing_or_search_url(url):
            return self.start_candidate_discovery()
        return original_direct(self)

    app_class._scan_ui = _scan_ui
    app_class._selected_candidate_ids = _selected_candidate_ids
    app_class._candidate_cache_path = _candidate_cache_path
    app_class._apply_candidate_thumb = _apply_candidate_thumb
    app_class._load_candidate_thumb = _load_candidate_thumb
    app_class.refresh_discovery_candidates = refresh_discovery_candidates
    app_class.start_candidate_discovery = start_candidate_discovery
    app_class.approve_discovery_candidates = approve_discovery_candidates
    app_class.archive_discovery_candidates = archive_discovery_candidates
    app_class.open_discovery_candidate_url = open_discovery_candidate_url
    app_class.start_scan = start_scan
    app_class.start_direct_link_import = start_direct_link_import
    app_class._phase49_3i_discovery_review_installed = True
