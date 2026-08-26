from __future__ import annotations

import json
from typing import Any

from .db import normalize_url
from .phase49_diagnostics import audit_event
from .v8_features import product_fingerprint


PHASE = "49.3I.32"


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _row_value(row, key: str, default=""):
    try:
        value = row.get(key, default) if isinstance(row, dict) else row[key]
    except Exception:
        value = default
    return default if value is None else value


def _valid_source_url(value: Any) -> str:
    value = _clean(value)
    return value if value.lower().startswith(("http://", "https://")) else ""


def resolve_source_url_for_save(existing: str, primary: str, secondary: str) -> str:
    """Resolve the Product source URL without allowing an unrelated save to erase it.

    Product Workspace historically exposes the same canonical URL in two editable
    controls. Both controls can be temporarily empty during layered UI actions.
    A generic Save/AI/close/publish action is not an explicit unlink operation, so
    an already persisted source identity must survive that transient state.

    Intent rules:
    - a non-empty changed primary/top source field wins;
    - otherwise a non-empty changed secondary/spec field wins;
    - otherwise either non-empty field wins;
    - if both controls are empty, preserve the existing database URL;
    - if no URL has ever existed, return empty rather than inventing one.
    """
    existing = _clean(existing)
    primary = _clean(primary)
    secondary = _clean(secondary)

    if primary and primary != existing:
        return primary
    if secondary and secondary != existing:
        return secondary
    return primary or secondary or existing


def recover_source_url_from_history(db, product_id: int, row=None) -> str:
    """Recover a previously persisted source URL without using the network.

    The accidental-delete bug wrote Product history immediately after the mature
    save, so the exact pre-delete URL normally remains in ``before_json``. As a
    secondary local source, the discovery queue can restore the exact discovered
    URL for the same source/external ID. No URL is guessed or reconstructed.
    """
    conn = getattr(db, "conn", None)
    if conn is None:
        return ""

    try:
        history = conn.execute(
            "SELECT before_json, after_json FROM product_history WHERE product_id=? ORDER BY id DESC LIMIT 80",
            (int(product_id),),
        ).fetchall()
    except Exception:
        history = []

    for item in history:
        for key in ("before_json", "after_json"):
            try:
                raw = item[key] if not isinstance(item, dict) else item.get(key)
                payload = json.loads(raw or "{}")
            except Exception:
                continue
            if isinstance(payload, dict):
                recovered = _valid_source_url(payload.get("source_url"))
                if recovered:
                    return recovered

    row = row if row is not None else db.product(int(product_id))
    source_code = _clean(_row_value(row, "source_code", ""))
    external_id = _clean(_row_value(row, "external_id", ""))
    if not source_code or not external_id:
        return ""
    try:
        candidates = conn.execute(
            "SELECT url FROM discovered_urls WHERE source_code=? AND external_id=? ORDER BY id DESC LIMIT 20",
            (source_code, external_id),
        ).fetchall()
    except Exception:
        candidates = []
    for item in candidates:
        try:
            raw = item["url"] if not isinstance(item, dict) else item.get("url")
        except Exception:
            raw = ""
        recovered = _valid_source_url(raw)
        if recovered:
            return recovered
    return ""


def _set_var(widget_var, value: str) -> None:
    try:
        widget_var.set(value)
    except Exception:
        pass


def _identity_values(row, source_url: str) -> dict[str, str]:
    source_code = _clean(_row_value(row, "source_code", ""))
    external_id = _clean(_row_value(row, "external_id", ""))
    return {
        "source_url": source_url,
        "normalized_url": normalize_url(source_url),
        "fingerprint": product_fingerprint(source_code, external_id, source_url),
    }


def install_workspace(workspace_class) -> None:
    """Install the final canonical-source invariant around every Workspace save."""
    if getattr(workspace_class, "_phase49_3i32_source_url_guard", False):
        return

    original_save = workspace_class.save

    def save(self, silent=False):
        before = self.db.product(self.product_id)
        existing = _clean(_row_value(before, "source_url", ""))
        primary_var = getattr(self, "source_url", None)
        secondary_var = getattr(self, "spec_source_url", None)
        try:
            primary = _clean(primary_var.get()) if primary_var is not None else ""
        except Exception:
            primary = ""
        try:
            secondary = _clean(secondary_var.get()) if secondary_var is not None else ""
        except Exception:
            secondary = ""

        # Repair products already damaged by the pre-49.3I.32 bug. Recovery is
        # local-only and exact: Product history first, discovery identity second.
        if not existing and not primary and not secondary:
            recovered = recover_source_url_from_history(self.db, self.product_id, before)
            if recovered:
                recovery_before = dict(before) if before is not None else {}
                self.db.update_product(self.product_id, _identity_values(before, recovered))
                recovered_row = self.db.product(self.product_id)
                try:
                    self.db.save_history(
                        self.product_id,
                        "source_url_recovered",
                        recovery_before,
                        dict(recovered_row) if recovered_row is not None else {},
                        "Phase49.3I.32 restored exact canonical source URL from local history/discovery",
                    )
                except Exception:
                    pass
                before = recovered_row
                existing = recovered
                try:
                    audit_event(
                        "source_identity",
                        "source_url_recovered",
                        status="ok",
                        product_id=int(self.product_id),
                        source_file=__file__,
                        message="canonical source URL recovered from local Product history/discovery",
                        detail={"phase": PHASE, "network_used": False},
                    )
                except Exception:
                    pass

        intended = resolve_source_url_for_save(existing, primary, secondary)

        # Feed the canonical value into the mature layered save chain. This
        # prevents ProductStudio.save() from ever seeing two accidental blanks.
        if intended:
            _set_var(primary_var, intended)
            _set_var(secondary_var, intended)
        if existing and not primary and not secondary:
            try:
                audit_event(
                    "source_identity",
                    "source_url_preserved_before_save",
                    status="ok",
                    product_id=int(self.product_id),
                    source_file=__file__,
                    message="canonical source URL preserved because both UI URL fields were blank",
                    detail={"phase": PHASE, "existing_source_present": True},
                )
            except Exception:
                pass

        result = original_save(self, silent=silent)
        if not result:
            return result

        after = self.db.product(self.product_id)
        after_url = _clean(_row_value(after, "source_url", ""))

        # Final defensive postcondition. The prefill above should make this path
        # unnecessary, but no later/legacy save layer is allowed to erase a known
        # canonical identity silently.
        if intended and not after_url:
            self.db.update_product(self.product_id, _identity_values(before, intended))
            after = self.db.product(self.product_id)
            after_url = _clean(_row_value(after, "source_url", ""))
            try:
                audit_event(
                    "source_identity",
                    "source_url_restored_after_save",
                    status="warning",
                    level="WARNING",
                    product_id=int(self.product_id),
                    source_file=__file__,
                    message="legacy save layer attempted to erase canonical source URL; value restored",
                    detail={"phase": PHASE, "restored": bool(after_url)},
                )
            except Exception:
                pass

        if after_url:
            _set_var(primary_var, after_url)
            _set_var(secondary_var, after_url)
        try:
            self.row = after
        except Exception:
            pass
        return result

    workspace_class.save = save
    workspace_class._phase49_3i32_source_url_guard = True
