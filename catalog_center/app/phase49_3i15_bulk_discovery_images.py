from __future__ import annotations

import asyncio
import json
import re
import threading
from pathlib import Path
from typing import Any

import tkinter as tk
from tkinter import messagebox, ttk

from .classic_methods import (
    _dom_image_urls,
    _download_context_images,
    launch_fresh_browser,
)
from .db import normalize_url, utc_now
from .phase49_3h_image_limits import normalize_image_limit
from .phase49_3i12_discovery_image_recovery import classify_manual_url
from .phase49_3i_discovery_review import (
    _resolve_product_id,
    _source_defaults,
    candidate_row,
    candidate_rows,
    candidate_status_for_known,
    discover_preview_candidates,
    known_product,
    set_candidate_status,
    upsert_candidate,
)
from .v8_features import product_fingerprint, source_payload_hash


PRODUCT_LIMIT_MIN = 1
PRODUCT_LIMIT_MAX = 100
DEFAULT_PRODUCT_LIMIT = 30
DEFAULT_IMAGE_LIMIT = 10
BULK_IMAGE_WAIT_MS = 2800


def normalize_product_limit(value: Any, default: int = DEFAULT_PRODUCT_LIMIT) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = int(default)
    return max(PRODUCT_LIMIT_MIN, min(PRODUCT_LIMIT_MAX, number))


def _safe_segment(value: Any) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip())
    return text.strip("._") or "unknown"


def candidate_manifest_path(data_root: Path | str, source_code: str, external_id: str) -> Path:
    root = Path(data_root) / "discovery_manifests" / _safe_segment(source_code)
    return root / f"{_safe_segment(external_id)}.json"


def read_candidate_manifest(data_root: Path | str, source_code: str, external_id: str) -> dict:
    path = candidate_manifest_path(data_root, source_code, external_id)
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def write_candidate_manifest(
    data_root: Path | str,
    candidate: dict,
    *,
    requested_images: int,
    image_urls: list[str],
    downloaded_images: list[str],
    final_url: str = "",
    http_status: int | None = None,
    error: str = "",
) -> Path:
    path = candidate_manifest_path(
        data_root,
        str(candidate.get("source_code") or ""),
        str(candidate.get("external_id") or ""),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    requested = normalize_image_limit(requested_images)
    urls = [str(item).strip() for item in image_urls or [] if str(item).strip()][:requested]
    local_files = [str(item).strip() for item in downloaded_images or [] if str(item).strip()][:requested]
    payload = {
        "source_code": str(candidate.get("source_code") or ""),
        "external_id": str(candidate.get("external_id") or ""),
        "source_url": str(candidate.get("source_url") or ""),
        "source_title": str(candidate.get("source_title") or ""),
        "thumbnail_url": str(candidate.get("thumbnail_url") or ""),
        "requested_images": requested,
        "image_urls": urls,
        "image_count": len(urls),
        "downloaded_images": local_files,
        "downloaded_count": len(local_files),
        "final_url": str(final_url or candidate.get("source_url") or ""),
        "http_status": http_status,
        "error": str(error or "")[:2000],
        "updated_at": utc_now(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def manifest_image_text(payload: dict) -> str:
    if not payload:
        return "—"
    requested = int(payload.get("requested_images") or 0)
    saved = int(payload.get("downloaded_count") or 0)
    found = int(payload.get("image_count") or 0)
    if requested:
        return f"{saved}/{requested} ذخیره | {found} یافت"
    return f"{saved} ذخیره | {found} یافت"


def _candidate_dict(row) -> dict:
    return {
        "source_code": str(row["source_code"] or ""),
        "external_id": str(row["external_id"] or ""),
        "source_url": str(row["source_url"] or ""),
        "source_title": str(row["source_title"] or ""),
        "thumbnail_url": str(row["thumbnail_url"] or ""),
        "discovered_from": str(row["discovered_from"] or ""),
    }


def build_product_payload(candidate: dict, manifest: dict, source_cfg: dict | None, source_name: str) -> dict:
    image_limit = normalize_image_limit(manifest.get("requested_images") or DEFAULT_IMAGE_LIMIT)
    image_urls = [str(item).strip() for item in manifest.get("image_urls") or [] if str(item).strip()][:image_limit]
    if not image_urls:
        thumb = str(candidate.get("thumbnail_url") or "").strip()
        if thumb.startswith(("http://", "https://")):
            image_urls = [thumb]
    source_url = str(manifest.get("final_url") or candidate.get("source_url") or "").strip()
    normalized = normalize_url(source_url)
    local_dir = str(manifest.get("local_dir") or "")
    data = {
        "source_code": str(candidate.get("source_code") or ""),
        "external_id": str(candidate.get("external_id") or ""),
        "source_url": source_url,
        "normalized_url": normalized,
        "source_title": str(candidate.get("source_title") or ""),
        "source_name": str(source_name or candidate.get("source_code") or ""),
        "images_json": json.dumps(image_urls, ensure_ascii=False),
        "selected_images_json": json.dumps(image_urls, ensure_ascii=False),
        "primary_image_url": image_urls[0] if image_urls else "",
        "local_dir": local_dir,
        "source_state": "active",
        "last_refetched_at": utc_now(),
    }
    data.update(_source_defaults(source_cfg, image_limit))
    data["fingerprint"] = product_fingerprint(data["source_code"], data["external_id"], data["source_url"])
    data["source_hash"] = source_payload_hash(data)
    return data


async def collect_candidate_images(
    url: str,
    output_dir: Path,
    *,
    image_limit: int,
    referer: str = "",
    headed: bool = False,
) -> dict:
    """Collect only public product images using the mature Classic browser helpers.

    This is deliberately not Rich Direct / extract_direct_link. It reuses the
    same browser launcher, DOM image filter and browser-context downloader used
    by the mature Classic acquisition path.
    """
    from playwright.async_api import async_playwright

    requested = normalize_image_limit(image_limit)
    output_dir.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        browser, browser_label = await launch_fresh_browser(playwright, headed=headed)
        try:
            context = await browser.new_context(
                locale="en-US",
                viewport={"width": 1440, "height": 1100},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0.0.0 Safari/537.36"
                ),
            )
            page = await context.new_page()
            if referer:
                try:
                    await page.set_extra_http_headers({"Referer": referer})
                except Exception:
                    pass
            response = await page.goto(url, wait_until="domcontentloaded", timeout=90_000)
            status = response.status if response else None
            if status in {403, 429}:
                raise PermissionError(f"HTTP {status}")
            await page.wait_for_timeout(BULK_IMAGE_WAIT_MS)
            # A few bounded scrolls expose lazy gallery images without crawling
            # elsewhere or clicking download/authenticated resources.
            for _ in range(3):
                await page.evaluate("() => window.scrollBy(0, Math.max(700, window.innerHeight * 0.8))")
                await page.wait_for_timeout(650)
            image_urls = await _dom_image_urls(page)
            selected_urls = image_urls[:requested]
            downloaded = await _download_context_images(
                context,
                selected_urls,
                output_dir,
                page.url or url,
                limit=requested,
            )
            return {
                "browser": browser_label,
                "http_status": status,
                "final_url": page.url or url,
                "image_urls": selected_urls,
                "downloaded_images": downloaded[:requested],
            }
        finally:
            await browser.close()


def _walk(root):
    try:
        children = root.winfo_children()
    except Exception:
        children = []
    for child in children:
        yield child
        yield from _walk(child)


def _set_live_state(self, state: str, text: str, detail: str, percent: float | None = None) -> None:
    colors = {
        "idle": ("#64748b", "#ffffff"),
        "active": ("#2563eb", "#ffffff"),
        "stop": ("#d97706", "#ffffff"),
        "done": ("#15803d", "#ffffff"),
        "error": ("#b91c1c", "#ffffff"),
    }
    bg, fg = colors.get(state, colors["idle"])
    badge = getattr(self, "_phase49_3i12_badge", None)
    if badge is not None:
        try:
            badge.configure(text=text, bg=bg, fg=fg)
        except Exception:
            pass
    detail_var = getattr(self, "_phase49_3i12_detail", None)
    if detail_var is not None:
        try:
            detail_var.set(detail)
        except Exception:
            pass
    progress = getattr(self, "_phase49_3i12_progress", None)
    if progress is not None:
        try:
            progress.stop()
            progress.configure(mode="determinate", maximum=100)
            progress["value"] = max(0.0, min(100.0, float(percent or 0.0)))
        except Exception:
            pass


def install_app(app_class) -> None:
    if getattr(app_class, "_phase49_3i15_bulk_discovery_installed", False):
        return

    original_mount = app_class._mount_phase49_3i12_operator_ui
    original_refresh = app_class.refresh_discovery_candidates

    def refresh_discovery_candidates(self):
        result = original_refresh(self)
        tree = getattr(self, "discovery_candidate_tree", None)
        if tree is None:
            return result
        try:
            tree.configure(columns=("status", "images", "title", "source", "external", "url"), show="tree headings")
            tree.heading("#0", text="عکس")
            tree.column("#0", width=100, minwidth=90, stretch=False, anchor="center")
            for key, title, width in (
                ("status", "وضعیت", 120),
                ("images", "تعداد عکس", 145),
                ("title", "عنوان", 315),
                ("source", "منبع", 95),
                ("external", "ID", 105),
                ("url", "URL", 400),
            ):
                tree.heading(key, text=title)
                tree.column(
                    key,
                    width=width,
                    minwidth=90 if key not in {"title", "url"} else 210,
                    stretch=key in {"title", "url"},
                    anchor="w" if key in {"title", "url"} else "center",
                )
            labels = {
                "review": "نیازمند انتخاب",
                "approved": "تأیید شده",
                "imported": "به محصولات اضافه شد",
                "blocked": "آرشیو / بلاک",
                "existing": "قبلاً موجود",
                "failed": "خطا",
            }
            ready = 0
            for row in candidate_rows(self.db, limit=300):
                iid = f"candidate-{row['id']}"
                if not tree.exists(iid):
                    continue
                manifest = read_candidate_manifest(self.DATA, row["source_code"], row["external_id"])
                image_text = manifest_image_text(manifest)
                status = str(row["status"] or "review")
                label = labels.get(status, status)
                if status == "review" and int(manifest.get("downloaded_count") or 0) > 0:
                    label = "آماده انتخاب"
                    ready += 1
                tree.item(
                    iid,
                    values=(
                        label,
                        image_text,
                        row["source_title"] or f"Model {row['external_id']}",
                        row["source_code"],
                        row["external_id"],
                        row["source_url"],
                    ),
                )
            summary = getattr(self, "_phase49_3i12_candidate_summary", None)
            if summary is not None:
                summary.set(f"نمایش: {len(tree.get_children())} | آماده با عکس: {ready}")
        except Exception:
            pass
        return result

    def start_bulk_page_discovery(self):
        if bool(getattr(self, "scan_running", False)):
            _set_live_state(self, "active", "● عملیات دیگری در حال اجرا است", "ابتدا عملیات جاری را متوقف یا تمام کنید.", 0)
            return None
        code = self.source_map.get(self.source_var.get().strip(), self.source_var.get().strip())
        src = self.db.source(code)
        if src is None:
            messagebox.showwarning("3DPrintHub", "ابتدا منبع را انتخاب کنید.", parent=self)
            return None
        url = self.seed_var.get().strip()
        pattern = str(src["model_url_pattern"] or "")
        kind = classify_manual_url(url, pattern)
        if kind in {"invalid", "invalid_pattern"}:
            messagebox.showwarning("3DPrintHub", "یک Search/Listing/Category URL معتبر وارد کنید.", parent=self)
            return None
        if kind == "product":
            messagebox.showinfo(
                "3DPrintHub",
                "این عملیات برای صفحه لیست/Search است. لینک صفحه‌ای را بدهید که چند محصول داخل آن است.",
                parent=self,
            )
            return None
        product_limit = normalize_product_limit(getattr(self, "_phase49_3i15_product_limit", DEFAULT_PRODUCT_LIMIT).get())
        image_limit = normalize_image_limit(getattr(self, "_phase49_3i15_image_limit", DEFAULT_IMAGE_LIMIT).get())
        try:
            self.direct_image_limit.set(image_limit)
        except Exception:
            pass
        self.scan_running = True
        self.stop_requested = False
        self._phase49_3i12_stop_requested = False
        self._phase49_3i12_run_kind = "bulk_images"
        self._phase49_3i12_run_url = url
        run_id = self.db.create_run(code, "preview_images", "classic_bulk_images", product_limit)
        self.status.set(f"کشف حداکثر {product_limit} محصول و دریافت حداکثر {image_limit} عکس برای هر محصول…")
        _set_live_state(self, "active", "● کشف لینک‌ها", f"در حال خواندن همان صفحه | هدف: {product_limit} محصول × {image_limit} عکس", 2)
        self.log(f"PHASE49_3I15_BULK_START source={code} products={product_limit} images={image_limit} url={url}")

        def worker():
            discovered = ready = failed = existing = blocked = 0
            try:
                async def execute():
                    nonlocal discovered, ready, failed, existing, blocked
                    candidates = await discover_preview_candidates(
                        url,
                        source_code=code,
                        model_pattern=pattern,
                        requested=product_limit,
                        scroll_rounds=max(8, min(32, product_limit // 4 + 6)),
                        headed=False,
                    )
                    candidate_ids: list[int] = []
                    for candidate in candidates[:product_limit]:
                        cid = upsert_candidate(self.db, candidate)
                        candidate_ids.append(cid)
                    discovered = len(candidate_ids)
                    self.after(0, self.refresh_discovery_candidates)
                    if not candidate_ids:
                        return
                    for index, candidate_id in enumerate(candidate_ids, start=1):
                        if bool(getattr(self, "stop_requested", False)):
                            break
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
                            continue
                        percent = 5 + (90.0 * (index - 1) / max(1, discovered))
                        self.after(
                            0,
                            lambda i=index, total=discovered, title=str(row["source_title"] or row["external_id"]), p=percent: _set_live_state(
                                self,
                                "active",
                                f"● دریافت تصاویر {i}/{total}",
                                f"در حال خواندن محصول: {title}",
                                p,
                            ),
                        )
                        candidate = _candidate_dict(row)
                        output_dir = Path(self.DATA) / "collected" / row["source_code"] / row["external_id"]
                        try:
                            result = await collect_candidate_images(
                                row["source_url"],
                                output_dir,
                                image_limit=image_limit,
                                referer=str(row["discovered_from"] or url),
                                headed=False,
                            )
                            manifest = {
                                **candidate,
                                "local_dir": str(output_dir),
                            }
                            write_candidate_manifest(
                                self.DATA,
                                manifest,
                                requested_images=image_limit,
                                image_urls=result.get("image_urls") or [],
                                downloaded_images=result.get("downloaded_images") or [],
                                final_url=str(result.get("final_url") or row["source_url"]),
                                http_status=result.get("http_status"),
                            )
                            if result.get("image_urls"):
                                set_candidate_status(self.db, candidate_id, "review")
                                ready += 1
                            else:
                                set_candidate_status(self.db, candidate_id, "failed", error="No product images found")
                                failed += 1
                            self.log(
                                f"PHASE49_3I15_IMAGES [{index}/{discovered}] candidate={candidate_id} "
                                f"found={len(result.get('image_urls') or [])} saved={len(result.get('downloaded_images') or [])}"
                            )
                        except Exception as exc:
                            failed += 1
                            write_candidate_manifest(
                                self.DATA,
                                candidate,
                                requested_images=image_limit,
                                image_urls=[row["thumbnail_url"]] if row["thumbnail_url"] else [],
                                downloaded_images=[],
                                final_url=row["source_url"],
                                error=f"{type(exc).__name__}: {exc}",
                            )
                            set_candidate_status(self.db, candidate_id, "failed", error=f"{type(exc).__name__}: {exc}")
                            self.log(f"PHASE49_3I15_IMAGE_FAILED candidate={candidate_id} {type(exc).__name__}: {exc}")
                        self.after(0, self.refresh_discovery_candidates)
                        if index < discovered and not bool(getattr(self, "stop_requested", False)):
                            await asyncio.sleep(0.8)

                asyncio.run(execute())
                stopped = bool(getattr(self, "stop_requested", False))
                self.db.finish_run(
                    run_id,
                    status="stopped" if stopped else ("completed_with_errors" if failed else "completed"),
                    discovered_count=discovered,
                    collected_count=ready,
                    duplicate_count=existing + blocked,
                    failed_count=failed,
                    message=f"bulk images ready={ready}; failed={failed}; existing={existing}; blocked={blocked}",
                )
            except Exception as exc:
                failed += 1
                self.db.finish_run(
                    run_id,
                    status="failed",
                    discovered_count=discovered,
                    collected_count=ready,
                    duplicate_count=existing + blocked,
                    failed_count=failed,
                    message=str(exc),
                )
                self.events.put(("error", f"کشف/دریافت تصاویر ناموفق بود: {type(exc).__name__}: {exc}"))
            finally:
                self.scan_running = False
                self.after(0, self.refresh_discovery_candidates)
                stopped = bool(getattr(self, "stop_requested", False))
                state = "stop" if stopped else ("error" if failed and not ready else "done")
                text = "● عملیات متوقف شد" if stopped else "● کشف و تصاویر پایان یافت"
                detail = f"کشف: {discovered} | آماده با تصویر: {ready} | موجود: {existing} | بلاک: {blocked} | خطا: {failed}"
                self.after(0, lambda: _set_live_state(self, state, text, detail, 100 if not stopped else 0))
                self.after(0, lambda: self.status.set(detail))
                self.log(f"PHASE49_3I15_BULK_END discovered={discovered} ready={ready} existing={existing} blocked={blocked} failed={failed}")

        threading.Thread(target=worker, daemon=True).start()
        return None

    def add_selected_discovery_products(self):
        if bool(getattr(self, "scan_running", False)):
            messagebox.showwarning("3DPrintHub", "ابتدا عملیات کشف/تصاویر را تمام یا متوقف کنید.", parent=self)
            return None
        ids = self._selected_candidate_ids() if hasattr(self, "_selected_candidate_ids") else []
        if not ids:
            messagebox.showwarning("3DPrintHub", "حداقل یک مورد را انتخاب کنید.", parent=self)
            return None
        if not messagebox.askyesno(
            "3DPrintHub — اضافه کردن به محصولات",
            f"{len(ids)} مورد انتخاب شده است.\nبدون دریافت محصول تکی، همین اطلاعات و تصاویر جمع‌آوری‌شده به محصولات اضافه شوند؟",
            parent=self,
        ):
            return None
        added = existing = blocked = failed = 0
        for candidate_id in ids:
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
                continue
            manifest = read_candidate_manifest(self.DATA, row["source_code"], row["external_id"])
            image_urls = manifest.get("image_urls") or []
            if not image_urls:
                failed += 1
                set_candidate_status(self.db, candidate_id, "failed", error="No staged images; run bulk discovery/images first")
                continue
            local_dir = Path(self.DATA) / "collected" / row["source_code"] / row["external_id"]
            manifest = dict(manifest)
            manifest["local_dir"] = str(local_dir)
            source_cfg = next((item for item in self.config.get("sources", []) if item.get("code") == row["source_code"]), None)
            src = self.db.source(row["source_code"])
            source_name = str(src["name"] or row["source_code"]) if src is not None else str(row["source_code"])
            data = build_product_payload(_candidate_dict(row), manifest, source_cfg, source_name)
            try:
                self.db.upsert_product(data)
                product_id = _resolve_product_id(self.db, row["source_code"], row["external_id"], data["normalized_url"])
                if not product_id:
                    raise RuntimeError("Product row was not resolved after bulk add")
                self.db.save_history(
                    product_id,
                    "phase49_3i15_bulk_add_from_discovery",
                    {},
                    data,
                    f"Bulk exact-page discovery; images={len(image_urls)}",
                )
                set_candidate_status(self.db, candidate_id, "imported", product_id=product_id)
                added += 1
            except Exception as exc:
                failed += 1
                set_candidate_status(self.db, candidate_id, "failed", error=f"{type(exc).__name__}: {exc}")
        self.refresh_discovery_candidates()
        self.refresh_products()
        self.status.set(f"اضافه به محصولات: {added} جدید، {existing} قبلی، {blocked} بلاک، {failed} خطا")
        messagebox.showinfo(
            "3DPrintHub",
            f"پایان اضافه‌کردن\nجدید: {added}\nقبلاً موجود: {existing}\nبلاک: {blocked}\nخطا: {failed}",
            parent=self,
        )
        return None

    def _mount_phase49_3i12_operator_ui(self):
        result = original_mount(self)
        operator = getattr(self, "_phase49_3i12_operator_frame", None)
        if operator is None or getattr(self, "_phase49_3i15_controls_mounted", False):
            return result
        self._phase49_3i15_product_limit = tk.IntVar(value=DEFAULT_PRODUCT_LIMIT)
        current_image_limit = DEFAULT_IMAGE_LIMIT
        try:
            current_image_limit = normalize_image_limit(self.direct_image_limit.get())
        except Exception:
            pass
        self._phase49_3i15_image_limit = tk.IntVar(value=current_image_limit)
        options = ttk.Frame(operator)
        options.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(6, 0))
        ttk.Label(options, text="تعداد محصول").pack(side="left", padx=(0, 4))
        ttk.Combobox(
            options,
            textvariable=self._phase49_3i15_product_limit,
            values=(10, 20, 30, 50, 100),
            state="readonly",
            width=7,
        ).pack(side="left", padx=(0, 12))
        ttk.Label(options, text="عکس برای هر محصول").pack(side="left", padx=(0, 4))
        ttk.Combobox(
            options,
            textvariable=self._phase49_3i15_image_limit,
            values=(5, 10, 15, 20),
            state="readonly",
            width=7,
        ).pack(side="left", padx=(0, 12))
        ttk.Label(
            options,
            text="کشف صفحه → دریافت تصاویر → انتخاب → اضافه به محصولات / بلاک",
            style="SubHeader.TLabel",
        ).pack(side="left", padx=5)

        for widget in _walk(self.scan_tab):
            if not isinstance(widget, ttk.Button):
                continue
            try:
                text = str(widget.cget("text") or "")
            except Exception:
                continue
            if text == "کشف لینک‌های همین صفحه":
                widget.configure(text="کشف + دریافت تصاویر", command=self.start_bulk_page_discovery, style="Success.TButton")
            elif text == "دریافت کامل انتخاب‌شده‌ها":
                widget.configure(text="اضافه کردن انتخاب‌شده‌ها به محصولات", command=self.add_selected_discovery_products, style="Success.TButton")
            elif text == "دریافت محصول تکی":
                widget.configure(text="محصول تکی (اختیاری)")
        for widget in _walk(self.scan_tab):
            if isinstance(widget, ttk.LabelFrame):
                try:
                    text = str(widget.cget("text") or "")
                    if text.startswith("کاندیداهای همین صفحه"):
                        widget.configure(text="محصولات همین صفحه — تعداد تصاویر هر مورد قبل از انتخاب مشخص است")
                except Exception:
                    pass
        self._phase49_3i15_controls_mounted = True
        refresh_discovery_candidates(self)
        return result

    app_class.refresh_discovery_candidates = refresh_discovery_candidates
    app_class.start_bulk_page_discovery = start_bulk_page_discovery
    app_class.start_exact_page_discovery = start_bulk_page_discovery
    app_class.add_selected_discovery_products = add_selected_discovery_products
    app_class.approve_discovery_candidates = add_selected_discovery_products
    app_class._mount_phase49_3i12_operator_ui = _mount_phase49_3i12_operator_ui
    app_class._phase49_3i15_bulk_discovery_installed = True
