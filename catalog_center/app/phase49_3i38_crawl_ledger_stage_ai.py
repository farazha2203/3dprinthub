from __future__ import annotations

import json
import shutil
import webbrowser
from pathlib import Path

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from .db import normalize_url, utc_now
from .phase49_diagnostics import audit_event, redact
from .phase49_3i36_stage_finalization import STAGE_LABELS, STAGE_ORDER, is_stage_locked
from .phase49_3i37_seven_stage_ai import (
    AI_SOURCE_MODES,
    run_resilient_orchestrator,
    source_mode,
)


PHASE = "49.3I.38"

TERMINAL_LEDGER_STATUSES = {"rejected", "blocked"}
LEDGER_STATUS_LABELS = {
    "new": "جدید / در صف",
    "running": "در حال دریافت",
    "collected": "دریافت‌شده",
    "failed": "خطا",
    "rejected": "رد دائمی + فایل پاک‌شده",
    "blocked": "بلاک‌شده",
}
STAGE_BY_LABEL = {label: stage for stage, label in STAGE_LABELS.items()}


def ensure_schema(db) -> None:
    """Add only the continuation cursor table; preserve the mature discovery ledger."""
    db.conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS crawl_listing_state(
            source_code TEXT NOT NULL,
            normalized_listing_url TEXT NOT NULL,
            listing_url TEXT NOT NULL,
            last_scroll_rounds INTEGER NOT NULL DEFAULT 0,
            last_found_count INTEGER NOT NULL DEFAULT 0,
            last_new_count INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL,
            PRIMARY KEY(source_code, normalized_listing_url)
        );
        CREATE INDEX IF NOT EXISTS ix_crawl_listing_state_updated
        ON crawl_listing_state(updated_at DESC);
        """
    )
    db.conn.commit()


def _row_value(row, key: str, default=""):
    if row is None:
        return default
    try:
        return row[key] if key in row.keys() else default
    except Exception:
        try:
            return row.get(key, default)
        except Exception:
            return default


def remember_ledger(
    db,
    source_code: str,
    external_id: str,
    url: str,
    *,
    status: str,
    discovered_from: str = "",
    error: str = "",
    increment_attempts: bool = False,
    force: bool = False,
):
    """Upsert one permanent source identity without losing a rejection tombstone."""
    ensure_schema(db)
    source_code = str(source_code or "").strip()
    external_id = str(external_id or "").strip()
    url = str(url or "").strip()
    if not source_code or not url:
        return None
    normalized = normalize_url(url)
    existing = db.conn.execute(
        """
        SELECT * FROM discovered_urls
        WHERE source_code=?
          AND ((?<>'' AND external_id=?) OR normalized_url=?)
        ORDER BY id
        LIMIT 1
        """,
        (source_code, external_id, external_id, normalized),
    ).fetchone()
    now = utc_now()
    if existing is not None:
        current_status = str(existing["status"] or "")
        if current_status in TERMINAL_LEDGER_STATUSES and status not in TERMINAL_LEDGER_STATUSES and not force:
            return existing
        attempts_sql = "attempts=attempts+1," if increment_attempts else ""
        db.conn.execute(
            f"""
            UPDATE discovered_urls
            SET external_id=CASE WHEN ?<>'' THEN ? ELSE external_id END,
                url=?,
                normalized_url=?,
                discovered_from=CASE WHEN ?<>'' THEN ? ELSE discovered_from END,
                status=?,
                {attempts_sql}
                last_error=?,
                updated_at=?
            WHERE id=?
            """,
            (
                external_id, external_id, url, normalized,
                discovered_from, discovered_from,
                str(status or "new"), str(error or "")[:4000], now, int(existing["id"]),
            ),
        )
        db.conn.commit()
        return db.conn.execute("SELECT * FROM discovered_urls WHERE id=?", (int(existing["id"]),)).fetchone()

    try:
        db.conn.execute(
            """
            INSERT INTO discovered_urls(
                source_code,external_id,url,normalized_url,discovered_from,
                status,attempts,last_error,discovered_at,updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                source_code, external_id, url, normalized, str(discovered_from or ""),
                str(status or "new"), 1 if increment_attempts else 0,
                str(error or "")[:4000], now, now,
            ),
        )
        db.conn.commit()
    except Exception:
        # A concurrent/alias identity may have won the UNIQUE external-id race.
        existing = db.conn.execute(
            """
            SELECT * FROM discovered_urls
            WHERE source_code=?
              AND ((?<>'' AND external_id=?) OR normalized_url=?)
            ORDER BY id
            LIMIT 1
            """,
            (source_code, external_id, external_id, normalized),
        ).fetchone()
        if existing is None:
            raise
        return remember_ledger(
            db, source_code, external_id, url, status=status,
            discovered_from=discovered_from, error=error,
            increment_attempts=increment_attempts, force=force,
        )
    return db.conn.execute("SELECT * FROM discovered_urls WHERE id=last_insert_rowid()").fetchone()


def terminal_identity_state(db, source_code: str, external_id: str, url: str) -> str:
    """Return a terminal state before Browser/HTTP/image acquisition starts."""
    source_code = str(source_code or "").strip()
    external_id = str(external_id or "").strip()
    normalized = normalize_url(url)
    ledger = db.conn.execute(
        """
        SELECT status FROM discovered_urls
        WHERE source_code=?
          AND ((?<>'' AND external_id=?) OR normalized_url=?)
        ORDER BY id
        LIMIT 1
        """,
        (source_code, external_id, external_id, normalized),
    ).fetchone()
    if ledger is not None and str(ledger["status"] or "") in TERMINAL_LEDGER_STATUSES:
        return str(ledger["status"])

    product = db.conn.execute(
        """
        SELECT is_blocked,source_state FROM products
        WHERE source_code=?
          AND ((?<>'' AND external_id=?) OR normalized_url=?)
        ORDER BY id
        LIMIT 1
        """,
        (source_code, external_id, external_id, normalized),
    ).fetchone()
    if product is not None and int(product["is_blocked"] or 0):
        state = str(product["source_state"] or "blocked")
        return "rejected" if state == "rejected" else "blocked"
    return ""


def next_scroll_rounds(
    db,
    source_code: str,
    listing_url: str,
    *,
    default_rounds: int = 8,
    step: int = 8,
    maximum: int = 96,
) -> int:
    """Continue deeper on the same listing instead of restarting at the old window."""
    ensure_schema(db)
    normalized = normalize_url(listing_url)
    row = db.conn.execute(
        """
        SELECT last_scroll_rounds
        FROM crawl_listing_state
        WHERE source_code=? AND normalized_listing_url=?
        """,
        (str(source_code or ""), normalized),
    ).fetchone()
    previous = int(row["last_scroll_rounds"] or 0) if row is not None else 0
    if previous <= 0:
        return max(1, int(default_rounds))
    return min(maximum, max(default_rounds, previous + max(1, int(step))))


def record_listing_progress(
    db,
    source_code: str,
    listing_url: str,
    *,
    scroll_rounds: int,
    found_count: int,
    new_count: int,
) -> None:
    ensure_schema(db)
    normalized = normalize_url(listing_url)
    db.conn.execute(
        """
        INSERT INTO crawl_listing_state(
            source_code,normalized_listing_url,listing_url,
            last_scroll_rounds,last_found_count,last_new_count,updated_at
        ) VALUES(?,?,?,?,?,?,?)
        ON CONFLICT(source_code,normalized_listing_url) DO UPDATE SET
            listing_url=excluded.listing_url,
            last_scroll_rounds=MAX(crawl_listing_state.last_scroll_rounds, excluded.last_scroll_rounds),
            last_found_count=excluded.last_found_count,
            last_new_count=excluded.last_new_count,
            updated_at=excluded.updated_at
        """,
        (
            str(source_code or ""), normalized, str(listing_url or ""),
            max(0, int(scroll_rounds)), max(0, int(found_count)),
            max(0, int(new_count)), utc_now(),
        ),
    )
    db.conn.commit()


def ledger_rows(db, *, source_code: str = "", status: str = "", search: str = "", limit: int = 2000):
    clauses = []
    args = []
    if source_code:
        clauses.append("source_code=?")
        args.append(str(source_code))
    if status:
        clauses.append("status=?")
        args.append(str(status))
    if search:
        q = f"%{str(search).strip()}%"
        clauses.append("(external_id LIKE ? OR url LIKE ? OR discovered_from LIKE ?)")
        args.extend([q, q, q])
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    return list(
        db.conn.execute(
            f"""
            SELECT * FROM discovered_urls
            {where}
            ORDER BY id DESC
            LIMIT ?
            """,
            (*args, max(1, min(int(limit), 10000))),
        )
    )


def ledger_counts(db, source_code: str = "") -> dict[str, int]:
    if source_code:
        rows = db.conn.execute(
            """
            SELECT status,COUNT(*) total
            FROM discovered_urls
            WHERE source_code=?
            GROUP BY status
            """,
            (source_code,),
        )
    else:
        rows = db.conn.execute(
            "SELECT status,COUNT(*) total FROM discovered_urls GROUP BY status"
        )
    return {str(row["status"]): int(row["total"] or 0) for row in rows}


def _safe_product_local_dir(app, row) -> Path | None:
    collected_root = (Path(app.DATA) / "collected").resolve()
    raw = str(_row_value(row, "local_dir", "") or "").strip()
    candidate = (
        Path(raw)
        if raw
        else collected_root
        / str(_row_value(row, "source_code", "") or "")
        / str(_row_value(row, "external_id", "") or "")
    )
    try:
        resolved = candidate.resolve()
    except Exception:
        return None
    if resolved == collected_root or collected_root not in resolved.parents:
        raise RuntimeError(
            f"مسیر فایل محصول خارج از محدوده امن collected است و پاک نشد: {resolved}"
        )
    return resolved


def _rejected_history_snapshot(row, thumbnail_path: str = "") -> dict:
    """Keep only the lightweight rejection evidence requested by the owner."""
    return {
        key: _row_value(row, key, "")
        for key in (
            "id",
            "source_code",
            "source_name",
            "external_id",
            "source_url",
            "normalized_url",
            "source_title",
            "title_fa",
            "blocked_at",
            "blocked_reason",
            "source_state",
            "workflow_status",
        )
    } | {"rejected_thumbnail_path": str(thumbnail_path or "")}


def _capture_rejected_thumbnail(app, row, product_id: int) -> str:
    """Persist one small preview outside collected/ before the heavy purge."""
    target_root = Path(app.DATA).resolve() / "rejected_thumbnails"
    target_root.mkdir(parents=True, exist_ok=True)
    target = target_root / f"rejected-{int(product_id)}.webp"

    candidates: list[str] = []
    primary = str(_row_value(row, "primary_image_url", "") or "").strip()
    if primary:
        candidates.append(primary)
    for field in ("selected_images_json", "images_json"):
        try:
            values = json.loads(str(_row_value(row, field, "[]") or "[]"))
        except Exception:
            values = []
        for value in values if isinstance(values, list) else []:
            text = str(value or "").strip()
            if text and text not in candidates:
                candidates.append(text)

    source_path = ""
    try:
        from .phase49_3c_image_pipeline import strict_local_image
        for url in candidates:
            source_path = strict_local_image(row, url)
            if source_path:
                break
    except Exception:
        source_path = ""

    if not source_path:
        local_dir = _safe_product_local_dir(app, row)
        if local_dir is not None:
            for folder in (local_dir / "seo_images", local_dir / "images"):
                if not folder.is_dir():
                    continue
                match = next(
                    (
                        item
                        for item in sorted(folder.iterdir())
                        if item.is_file()
                        and item.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
                    ),
                    None,
                )
                if match is not None:
                    source_path = str(match)
                    break

    if not source_path:
        return ""
    try:
        from PIL import Image
        with Image.open(source_path) as image:
            image.load()
            image.thumbnail((360, 360), Image.Resampling.LANCZOS)
            if image.mode not in {"RGB", "RGBA"}:
                image = image.convert("RGBA" if "transparency" in image.info else "RGB")
            image.save(target, "WEBP", quality=82, method=6)
    except Exception:
        return ""
    return str(target)


def reject_and_purge_product(app, product_id: int, reason: str = "") -> dict:
    """Terminal rejection: keep URL/title/one thumbnail, purge heavy data/files."""
    product_id = int(product_id)
    db = app.db
    ensure_schema(db)
    before = db.product(product_id)
    if before is None:
        raise RuntimeError(f"محصول #{product_id} پیدا نشد.")

    source_code = str(_row_value(before, "source_code", "") or "")
    external_id = str(_row_value(before, "external_id", "") or "")
    source_url = str(_row_value(before, "source_url", "") or "")
    if not source_code or not source_url:
        raise RuntimeError("هویت منبع محصول ناقص است؛ حذف دائمی انجام نشد.")

    target = _safe_product_local_dir(app, before)
    rejected_thumbnail = _capture_rejected_thumbnail(
        app,
        before,
        product_id,
    )
    remember_ledger(
        db,
        source_code,
        external_id,
        source_url,
        status="rejected",
        discovered_from="operator_reject_purge",
        error=str(reason or "")[:1000],
        force=True,
    )

    # This terminal operator action deliberately supersedes stage finalization.
    # The source identity/tombstone remains, while every locally acquired binary
    # pointer is cleared so rejected content cannot leak into a later Batch.
    columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
    values = {
        "is_blocked": 1,
        "blocked_at": utc_now(),
        "blocked_reason": ("رد دائمی + حذف داده/فایل سنگین" + (f": {reason}" if reason else ""))[:1000],
        "source_state": "rejected",
        "workflow_status": "blocked",
        "upload_ready": 0,
        "needs_update": 0,
        "approved_for_sale": 0,
        "publish_as_product": 0,
        "publish_as_portfolio": 0,
        "images_json": "[]",
        "selected_images_json": "[]",
        "primary_image_url": "",
        "file_links_json": "[]",
        "selected_file_links_json": "[]",
        "local_dir": "",
        "source_page_screenshot_path": "",
        "image_metadata_json": "[]",
        "rejected_thumbnail_path": rejected_thumbnail,
        "ai_completed_once": 0,
        "ai_completed_at": "",
        "ai_completed_source_mode": "",
        "ai_completed_provider": "",
        "ai_completed_model": "",
        "final_price": 0,
        "suggested_price": 0,
        "price_min": 0,
        "price_max": 0,
        "price_is_final": 0,
        "material_price_per_gram": 0,
    }
    for key in (
        "source_short_description",
        "source_description",
        "short_description_fa",
        "description_fa",
        "use_description",
        "seo_title_fa",
        "seo_description_fa",
        "technical_summary_fa",
        "custom_notes",
        "last_sync_conflict",
    ):
        if key in columns:
            values[key] = ""
    for key in (
        "source_tags_json",
        "tags_json",
        "categories_fa_json",
        "tags_fa_json",
        "hashtags_fa_json",
        "keywords_json",
        "sales_bullets_json",
        "materials_json",
        "colors_json",
        "material_options_json",
        "color_options_json",
        "material_color_options_json",
        "sales_profiles_json",
        "sales_profile_ledger_json",
        "source_print_profiles_json",
    ):
        if key in columns:
            values[key] = "[]"
    for key in (
        "source_specs_json",
        "specs_fa_json",
        "technical_features_json",
        "content_pack_json",
        "source_snapshot_json",
    ):
        if key in columns:
            values[key] = "{}"

    values = {key: value for key, value in values.items() if key in columns}
    values["updated_at"] = utc_now()
    db.conn.execute(
        f"UPDATE products SET {','.join(f'{key}=?' for key in values)} WHERE id=?",
        (*values.values(), product_id),
    )
    db.conn.commit()

    deleted = False
    if target is not None and target.exists():
        shutil.rmtree(target)
        deleted = True

    after = db.product(product_id)
    try:
        db.save_history(
            product_id,
            "rejected_purged",
            _rejected_history_snapshot(before, rejected_thumbnail),
            _rejected_history_snapshot(after, rejected_thumbnail)
            if after is not None else {},
            f"Heavy Catalog/local acquisition purged={deleted}; reason={reason}",
        )
    except Exception:
        pass
    audit_event(
        "crawl",
        "product_rejected_purged",
        product_id=product_id,
        source_file=__file__,
        message=f"purged={deleted}",
        detail={
            "phase": PHASE,
            "source_code": source_code,
            "external_id": external_id,
            "source_url": source_url,
            "local_dir_purged": bool(deleted),
        },
    )
    return {
        "product_id": product_id,
        "source_url": source_url,
        "external_id": external_id,
        "local_dir": str(target) if target is not None else "",
        "deleted": bool(deleted),
        "thumbnail_path": rejected_thumbnail,
        "ledger_status": "rejected",
    }


def restore_rejected_identity(db, product_id: int) -> None:
    row = db.product(int(product_id))
    if row is None:
        return
    if str(_row_value(row, "source_state", "") or "") != "rejected":
        return
    remember_ledger(
        db,
        str(_row_value(row, "source_code", "") or ""),
        str(_row_value(row, "external_id", "") or ""),
        str(_row_value(row, "source_url", "") or ""),
        status="new",
        discovered_from="operator_restore_rejected",
        force=True,
    )


def _selected_product_ids(app) -> list[int]:
    ids = set()
    tree = getattr(app, "product_tree", None)
    if tree is not None:
        for raw in tree.selection() or ():
            try:
                ids.add(int(raw))
            except Exception:
                pass
    for name in ("_phase49_3i26_product_selection", "_phase49_3i_selected_products"):
        for raw in getattr(app, name, set()) or set():
            try:
                ids.add(int(raw))
            except Exception:
                pass
    return sorted(ids)


def _open_ledger_window(app):
    ensure_schema(app.db)
    win = tk.Toplevel(app)
    win.title("دفتر لینک‌های کرال‌شده / دریافت‌شده")
    win.geometry("1420x760")
    win.minsize(1050, 600)

    toolbar = ttk.Frame(win, padding=8)
    toolbar.pack(fill="x")
    source_var = tk.StringVar(value="")
    status_var = tk.StringVar(value="")
    search_var = tk.StringVar(value="")
    count_var = tk.StringVar(value="")

    sources = [""] + [str(row["code"]) for row in app.db.sources()]
    ttk.Label(toolbar, text="منبع").pack(side="right", padx=4)
    ttk.Combobox(toolbar, textvariable=source_var, values=sources, state="readonly", width=18).pack(side="right", padx=4)
    ttk.Label(toolbar, text="وضعیت").pack(side="right", padx=(12, 4))
    status_labels = ["همه"] + [f"{key} — {label}" for key, label in LEDGER_STATUS_LABELS.items()]
    status_box = ttk.Combobox(toolbar, values=status_labels, state="readonly", width=30)
    status_box.set("همه")
    status_box.pack(side="right", padx=4)
    ttk.Label(toolbar, text="جستجو").pack(side="right", padx=(12, 4))
    ttk.Entry(toolbar, textvariable=search_var, width=38).pack(side="right", padx=4)
    ttk.Label(toolbar, textvariable=count_var, style="SubHeader.TLabel").pack(side="left", padx=8)

    columns = ("id", "status", "source", "external", "url", "from", "attempts", "updated")
    tree = ttk.Treeview(win, columns=columns, show="headings", selectmode="browse")
    for key, label, width in (
        ("id", "ID", 60),
        ("status", "وضعیت", 180),
        ("source", "منبع", 100),
        ("external", "شناسه", 130),
        ("url", "لینک محصول", 480),
        ("from", "کشف‌شده از", 300),
        ("attempts", "تلاش", 65),
        ("updated", "آخرین وضعیت", 155),
    ):
        tree.heading(key, text=label)
        tree.column(key, width=width, anchor="w" if key in {"url", "from"} else "center")
    tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def selected_status():
        text = str(status_box.get() or "")
        if text == "همه":
            return ""
        return text.split(" — ", 1)[0].strip()

    def refresh():
        for iid in tree.get_children():
            tree.delete(iid)
        rows = ledger_rows(
            app.db,
            source_code=source_var.get().strip(),
            status=selected_status(),
            search=search_var.get().strip(),
            limit=5000,
        )
        for row in rows:
            status = str(row["status"] or "")
            tree.insert(
                "", "end", iid=str(row["id"]),
                values=(
                    row["id"],
                    LEDGER_STATUS_LABELS.get(status, status),
                    row["source_code"],
                    row["external_id"],
                    row["url"],
                    row["discovered_from"],
                    row["attempts"],
                    row["updated_at"],
                ),
            )
        counts = ledger_counts(app.db, source_var.get().strip())
        total = sum(counts.values())
        rejected = counts.get("rejected", 0)
        collected = counts.get("collected", 0)
        count_var.set(f"کل: {total} • دریافت‌شده: {collected} • رد دائمی: {rejected}")

    def open_selected():
        sel = tree.selection()
        if not sel:
            return
        values = tree.item(sel[0], "values")
        if values and len(values) > 4 and str(values[4]).startswith(("http://", "https://")):
            webbrowser.open(str(values[4]))

    ttk.Button(toolbar, text="بروزرسانی", command=refresh).pack(side="left", padx=4)
    ttk.Button(toolbar, text="باز کردن لینک", command=open_selected).pack(side="left", padx=4)
    status_box.bind("<<ComboboxSelected>>", lambda _event: refresh())
    source_var.trace_add("write", lambda *_args: refresh())
    search_var.trace_add("write", lambda *_args: refresh())
    tree.bind("<Double-1>", lambda _event: open_selected())
    refresh()
    return win


def install_database(database_class) -> None:
    if getattr(database_class, "_phase49_3i38_ledger_guard", False):
        return
    original_restore = database_class.restore_product

    def restore_product(self, product_id: int) -> None:
        before = self.product(int(product_id))
        was_rejected = bool(
            before is not None
            and str(_row_value(before, "source_state", "") or "") == "rejected"
        )
        original_restore(self, int(product_id))
        if was_rejected:
            restored = self.product(int(product_id))
            remember_ledger(
                self,
                str(_row_value(restored, "source_code", "") or ""),
                str(_row_value(restored, "external_id", "") or ""),
                str(_row_value(restored, "source_url", "") or ""),
                status="new",
                discovered_from="operator_restore_rejected",
                force=True,
            )

    database_class.restore_product = restore_product
    database_class._phase49_3i38_ledger_guard = True


def install_app(app_class) -> None:
    if getattr(app_class, "_phase49_3i38_crawl_ledger", False):
        return
    original_init = app_class.__init__
    original_refresh_all = getattr(app_class, "refresh_all", None)

    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        ensure_schema(self.db)

        scan_toolbar = ttk.Frame(self.scan_tab)
        scan_toolbar.pack(fill="x", pady=(6, 0))
        ttk.Label(
            scan_toolbar,
            text=(
                "Ledger دائمی: لینک‌های دریافت‌شده/ردشده دوباره وارد صف نمی‌شوند. "
                "برای همان Listing، دریافت بعدی از عمق بیشتری ادامه می‌دهد."
            ),
            style="SubHeader.TLabel",
        ).pack(side="right", padx=4)
        ttk.Button(
            scan_toolbar,
            text="📚 دفتر لینک‌های کرال‌شده / دریافت‌شده",
            command=lambda: _open_ledger_window(self),
            style="Primary.TButton",
        ).pack(side="left", padx=4)

        children = list(self.products_tab.winfo_children())
        reject_bar = ttk.Frame(self.products_tab)
        try:
            reject_bar.pack(fill="x", pady=(0, 6), before=children[0] if children else None)
        except Exception:
            reject_bar.pack(fill="x", pady=(0, 6))
        ttk.Button(
            reject_bar,
            text="🗑 رد دائمی + حذف فایل‌ها و عکس‌های محلی",
            command=self._phase49_3i38_reject_selected,
            style="Danger.TButton",
        ).pack(side="left", padx=4)
        ttk.Label(
            reject_bar,
            text=(
                "Source URL/شناسه در Ledger می‌ماند و در Crawl/Direct بعدی Skip می‌شود. "
                "فقط پوشه همان محصول داخل collected پاک می‌شود."
            ),
            style="SubHeader.TLabel",
        ).pack(side="left", padx=8)

        # The final 3I.37 bulk panel remains the single AI boundary. Add a
        # stage-4 shortcut that calls the exact same orchestrator.
        for candidate in self.products_tab.winfo_children():
            try:
                if not isinstance(candidate, ttk.LabelFrame):
                    continue
                if "تکمیل هوشمند ۷ مرحله‌ای محصولات انتخاب‌شده" not in str(candidate.cget("text") or ""):
                    continue
                ttk.Button(
                    candidate,
                    text="✨ SEO/محتوا انتخابی — فقط مرحله ۴",
                    command=self._phase49_3i38_bulk_content_ai,
                    style="Success.TButton",
                ).pack(side="right", padx=5)
                break
            except Exception:
                continue

    def reject_selected(self):
        ids = _selected_product_ids(self)
        if not ids:
            messagebox.showwarning("3DPrintHub", "حداقل یک محصول را انتخاب کن.", parent=self)
            return
        reason = simpledialog.askstring(
            "رد دائمی محصول",
            "دلیل رد (اختیاری). فایل‌ها و عکس‌های محلی محصول پاک می‌شوند ولی لینک در Ledger می‌ماند:",
            parent=self,
        )
        if reason is None:
            return
        if not messagebox.askyesno(
            "3DPrintHub — تأیید حذف فایل",
            (
                f"{len(ids)} محصول رد دائمی شوند؟\n\n"
                "• پوشه محلی هر محصول فقط داخل collected حذف می‌شود\n"
                "• تصاویر/فایل‌های همان محصول از رکورد پاک می‌شوند\n"
                "• Source URL و شناسه در Ledger باقی می‌مانند\n"
                "• Crawl و Direct Link بعدی آنها را دوباره دریافت نمی‌کنند\n"
                "• برای دریافت دوباره باید محصول را عمداً از بخش بلاک‌شده بازگردانی"
            ),
            parent=self,
        ):
            return
        success = 0
        failures = []
        for product_id in ids:
            try:
                reject_and_purge_product(self, product_id, reason.strip())
                success += 1
            except Exception as exc:
                failures.append(f"#{product_id}: {redact(exc)}")
        self.current_product = None
        for name in ("refresh_products", "refresh_blocked", "refresh_upload_queue", "refresh_published"):
            callback = getattr(self, name, None)
            if callable(callback):
                callback()
        self.status.set(f"رد دائمی: {success} موفق • {len(failures)} خطا")
        if failures:
            messagebox.showwarning(
                "3DPrintHub",
                f"{success} محصول رد و پاک‌سازی شد.\nخطاها:\n" + "\n".join(failures[:8]),
                parent=self,
            )

    def bulk_content_ai(self):
        ids = _selected_product_ids(self)
        if not ids:
            messagebox.showwarning("3DPrintHub", "ابتدا محصولات را انتخاب کن.", parent=self)
            return
        if getattr(self, "_phase49_3i33_bulk_busy", False):
            self.status.set("یک عملیات AI گروهی در حال اجرا است.")
            return
        self._phase49_3i33_bulk_busy = True
        mode = source_mode(self)
        from .phase49_3i21_observable_ai_link_refresh import ObservableJobDialog
        dialog = ObservableJobDialog(
            self,
            f"SEO/محتوا مرحله ۴ • {AI_SOURCE_MODES[mode]} • {len(ids)} محصول",
        )
        dialog.event(
            "queue",
            "همان موتور AI مادر؛ فقط Stage 4 بازنویسی/پاکسازی می‌شود و Stageهای دیگر دست‌نخورده‌اند.",
        )

        def worker():
            success = 0
            failed = 0
            try:
                for index, product_id in enumerate(ids, 1):
                    if dialog.cancelled.is_set():
                        break
                    dialog.set_progress(
                        ((index - 1) / len(ids)) * 100,
                        f"مرحله ۴ • محصول {index}/{len(ids)} • #{product_id}",
                    )
                    try:
                        run_resilient_orchestrator(
                            self,
                            product_id,
                            dialog,
                            mode=mode,
                            target_stages={"content"},
                            refresh_existing=True,
                        )
                    except Exception as exc:
                        failed += 1
                        dialog.event("product_failed", f"محصول #{product_id}: {redact(exc)}")
                        continue
                    success += 1
                    updater = getattr(self, "_phase49_3i33_update_product_card", None)
                    if callable(updater):
                        self.after(0, lambda pid=product_id: updater(pid))
                dialog.set_progress(100, "پایان SEO/محتوای انتخاب‌شده‌ها")
                dialog.done(f"مرحله ۴ پایان یافت • {success} موفق • {failed} خطا")
            except Exception as exc:
                dialog.fail(exc)
            finally:
                self.after(0, lambda: setattr(self, "_phase49_3i33_bulk_busy", False))

        import threading
        threading.Thread(
            target=worker,
            daemon=True,
            name="catalog-3i38-bulk-content-ai",
        ).start()

    def refresh_all(self):
        if callable(original_refresh_all):
            result = original_refresh_all(self)
        else:
            result = None
        ensure_schema(self.db)
        return result

    app_class.__init__ = __init__
    app_class.refresh_all = refresh_all
    app_class._phase49_3i38_reject_selected = reject_selected
    app_class._phase49_3i38_bulk_content_ai = bulk_content_ai
    app_class._phase49_3i38_crawl_ledger = True


def install_workspace(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3i38_target_stage_ai", False):
        return
    original_init = workspace_class.__init__

    def __init__(self, app, product_id):
        original_init(self, app, product_id)
        panel = getattr(self, "_phase49_3i37_ai_panel", None)
        if panel is None:
            return
        self._phase49_3i38_stage_var = tk.StringVar(value=STAGE_LABELS["content"])
        ttk.Label(panel, text="اجرای محدود به Stage").pack(side="right", padx=(12, 3))
        ttk.Combobox(
            panel,
            textvariable=self._phase49_3i38_stage_var,
            values=[STAGE_LABELS[stage] for stage in STAGE_ORDER],
            state="readonly",
            width=28,
        ).pack(side="right", padx=3)
        ttk.Button(
            panel,
            text="✨ پاکسازی/تکمیل فقط همین Stage",
            command=self._phase49_3i38_run_target_stage,
            style="Primary.TButton",
        ).pack(side="right", padx=4)

    def run_target_stage(self):
        if getattr(self, "_phase49_3i33_ai_busy", False):
            self.footer_status.set("یک عملیات هوش مصنوعی در حال اجرا است.")
            return
        label = str(self._phase49_3i38_stage_var.get() or "")
        stage = STAGE_BY_LABEL.get(label, "content")
        row = self.db.product(self.product_id)
        if row is None:
            return
        if is_stage_locked(row, stage):
            messagebox.showwarning(
                "3DPrintHub",
                f"{STAGE_LABELS[stage]} نهایی/قفل است. برای تغییر ابتدا «اصلاح» را بزن.",
                parent=self,
            )
            return
        if stage in {"commerce", "publish"}:
            messagebox.showinfo(
                "3DPrintHub",
                f"{STAGE_LABELS[stage]} اپراتوری است و موتور AI اجازه بازنویسی آن را ندارد.",
                parent=self,
            )
            return

        from .phase49_3i21_observable_ai_link_refresh import ObservableJobDialog
        mode = source_mode(self.app)
        self._phase49_3i33_ai_busy = True
        dialog = ObservableJobDialog(
            self,
            f"{STAGE_LABELS[stage]} • {AI_SOURCE_MODES[mode]}",
        )
        dialog.event(
            "queue",
            f"فقط {STAGE_LABELS[stage]} پاکسازی/تکمیل می‌شود؛ Stageهای دیگر خارج از Scope هستند.",
        )

        def worker():
            try:
                run_resilient_orchestrator(
                    self.app,
                    int(self.product_id),
                    dialog,
                    mode=mode,
                    target_stages={stage},
                    refresh_existing=True,
                )
                dialog.done(f"{STAGE_LABELS[stage]} تکمیل شد؛ برای قفل نهایی «ثبت» را بزن.")
                self.after(0, self.reload)
            except Exception as exc:
                dialog.fail(exc)
            finally:
                self.after(0, lambda: setattr(self, "_phase49_3i33_ai_busy", False))

        import threading
        threading.Thread(
            target=worker,
            daemon=True,
            name=f"catalog-3i38-stage-{stage}-{self.product_id}",
        ).start()

    workspace_class.__init__ = __init__
    workspace_class._phase49_3i38_run_target_stage = run_target_stage
    workspace_class._phase49_3i38_target_stage_ai = True
