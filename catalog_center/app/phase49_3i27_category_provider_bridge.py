from __future__ import annotations

from typing import Any

from .phase49_diagnostics import audit_event


PHASE = "49.3I.27"


def workspace_categories(workspace) -> list[dict[str, Any]]:
    """Return the canonical Catalog site-category rows from the App boundary.

    ``Database`` intentionally owns product/source persistence and has never
    exposed a ``categories()`` API. ProductStudio already uses
    ``app.get_all_categories()`` for the visible category combobox and AI calls.
    Keep the exact-link completion on that same mature contract instead of
    inventing a second category repository on Database.
    """
    getter = getattr(getattr(workspace, "app", None), "get_all_categories", None)
    if not callable(getter):
        return []
    try:
        rows = getter() or []
    except Exception as exc:
        audit_event(
            "product",
            "category_provider_failed",
            status="warning",
            level="WARNING",
            product_id=getattr(workspace, "product_id", None),
            source_file=__file__,
            message=str(exc),
        )
        return []

    output: list[dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict):
            item = dict(row)
        else:
            try:
                item = dict(row)
            except Exception:
                continue
        slug = str(item.get("slug") or "").strip()
        name = str(item.get("name") or "").strip()
        if not slug or not name:
            continue
        output.append({**item, "slug": slug, "name": name})
    return output


def install_workspace(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3i27_category_provider_bridge", False):
        return

    original_link_refresh = getattr(workspace_class, "_phase49_3i21_link_refresh", None)
    if not callable(original_link_refresh):
        raise RuntimeError("49.3I.27 requires the 49.3I.26 exact-link workspace action")

    def link_refresh(self):
        db = getattr(self, "db", None)
        if db is None:
            return original_link_refresh(self)

        # 49.3I.26 calls db.categories() twice. Bridge that missing legacy-shaped
        # call to the existing App category provider for this live workspace DB
        # instance. This is additive, no schema change and no persistent mutation.
        if not callable(getattr(db, "categories", None)):
            def categories():
                return workspace_categories(self)
            db.categories = categories

        return original_link_refresh(self)

    workspace_class._phase49_3i21_link_refresh = link_refresh
    workspace_class._phase49_3i27_category_provider_bridge = True
