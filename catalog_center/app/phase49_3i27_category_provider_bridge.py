from __future__ import annotations

from typing import Any

from .phase49_diagnostics import audit_event


PHASE = "49.3I.28"


def workspace_categories(workspace) -> list[dict[str, Any]]:
    """Return the canonical Catalog site-category rows from the App boundary."""
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
    if getattr(workspace_class, "_phase49_3i28_exact_link_contract_bridge", False):
        return

    original_link_refresh = getattr(workspace_class, "_phase49_3i21_link_refresh", None)
    if not callable(original_link_refresh):
        raise RuntimeError("49.3I.28 requires the 49.3I.26 exact-link workspace action")

    # 49.3I.26 accidentally called canonical_source_title using the wrong argument
    # order: source_url was passed as current_title and current_title was then
    # supplied again as a keyword, producing:
    #   got multiple values for argument 'current_title'
    # Keep the working 49.3I.19 source-identity implementation authoritative and
    # adapt only the final exact-link call boundary. No AI/image behavior changes.
    from . import phase49_3i26_operator_completion as phase26
    from .phase49_3i19_source_identity import canonical_source_title as canonical_source_title_v19

    def canonical_source_title_compat(
        source_url: str,
        external_id: str = "",
        *,
        candidates=(),
        current_title: str = "",
    ) -> str:
        return canonical_source_title_v19(
            current_title,
            source_url,
            external_id,
            candidates=candidates,
        )

    phase26.canonical_source_title = canonical_source_title_compat

    def link_refresh(self):
        db = getattr(self, "db", None)
        if db is None:
            return original_link_refresh(self)

        # Database intentionally does not own category lookup. Bridge the two
        # legacy-shaped calls in 49.3I.26 to the mature App category provider.
        if not callable(getattr(db, "categories", None)):
            def categories():
                return workspace_categories(self)
            db.categories = categories

        return original_link_refresh(self)

    workspace_class._phase49_3i21_link_refresh = link_refresh
    workspace_class._phase49_3i28_exact_link_contract_bridge = True
    workspace_class._phase49_3i27_category_provider_bridge = True
