from __future__ import annotations

from .phase49_3i12_discovery_image_recovery import (
    install_app as _install_operator_app,
    install_workspace,
)


def install_app(app_class, discovery_module=None) -> None:
    """Finalize the 49.3I.12 operator panel against the mature candidate Treeview contract."""
    _install_operator_app(app_class, discovery_module)
    if getattr(app_class, "_phase49_3i12_runtime_bridge_installed", False):
        return

    original_mount = app_class._mount_phase49_3i12_operator_ui
    original_refresh = app_class.refresh_discovery_candidates

    def refresh_discovery_candidates(self):
        result = original_refresh(self)
        summary = getattr(self, "_phase49_3i12_candidate_summary", None)
        tree = getattr(self, "discovery_candidate_tree", None)
        if summary is not None and tree is not None:
            try:
                summary.set(f"نمایش: {len(tree.get_children())}")
            except Exception:
                pass
        return result

    def _mount_phase49_3i12_operator_ui(self):
        result = original_mount(self)
        tree = getattr(self, "discovery_candidate_tree", None)
        if tree is None:
            return result
        try:
            # Mature 49.3I refresh code writes the thumbnail to #0 and exactly
            # five value columns. Keep that contract rather than inventing a
            # parallel row renderer.
            tree.configure(
                show="tree headings",
                columns=("status", "title", "source", "external", "url"),
            )
            tree.heading("#0", text="عکس")
            tree.column("#0", width=100, minwidth=90, stretch=False, anchor="center")
            for key, title, width in (
                ("status", "وضعیت", 115),
                ("title", "عنوان Preview", 330),
                ("source", "منبع", 100),
                ("external", "ID", 115),
                ("url", "URL", 430),
            ):
                tree.heading(key, text=title)
                tree.column(
                    key,
                    width=width,
                    minwidth=90 if key not in {"title", "url"} else 220,
                    stretch=key in {"title", "url"},
                    anchor="w" if key in {"title", "url"} else "center",
                )
            refresh_discovery_candidates(self)
        except Exception:
            pass
        return result

    app_class.refresh_discovery_candidates = refresh_discovery_candidates
    app_class._mount_phase49_3i12_operator_ui = _mount_phase49_3i12_operator_ui
    app_class._phase49_3i12_runtime_bridge_installed = True
