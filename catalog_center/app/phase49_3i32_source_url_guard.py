from __future__ import annotations

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


def _set_var(widget_var, value: str) -> None:
    try:
        widget_var.set(value)
    except Exception:
        pass


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
            source_code = _clean(_row_value(before, "source_code", ""))
            external_id = _clean(_row_value(before, "external_id", ""))
            self.db.update_product(
                self.product_id,
                {
                    "source_url": intended,
                    "normalized_url": normalize_url(intended),
                    "fingerprint": product_fingerprint(source_code, external_id, intended),
                },
            )
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
