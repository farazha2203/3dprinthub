from __future__ import annotations


PHASE = "49.3I.20"

IMAGE_PANEL_TITLE = "عملیات گروهی همه تصاویر منتخب سایت"
SOURCE_PANEL_TITLE = "هویت واقعی محصول در منبع — قبل از ترجمه و SEO"
EDITOR_PANEL_TITLE = "اصلاح نام محصول و بازسازی متن / SEO"


def _widget_text(widget) -> str:
    try:
        return str(widget.cget("text") or "")
    except Exception:
        return ""


def _packed_children(parent):
    output = []
    for child in parent.winfo_children():
        try:
            if child.winfo_manager() == "pack":
                output.append(child)
        except Exception:
            continue
    return output


def move_packed_panel_to_front(parent, title: str) -> bool:
    """Move an existing pack-managed LabelFrame ahead of expandable content.

    This is intentionally layout-only: the widget and all of its commands/state
    stay intact. It fixes the operator panels being mounted after fill/expand
    gallery/content panes where they could be pushed below the visible viewport.
    """

    children = _packed_children(parent)
    panel = next((child for child in children if _widget_text(child) == title), None)
    if panel is None:
        return False

    anchors = [child for child in children if child is not panel]
    if not anchors:
        return True

    try:
        panel.pack_forget()
        panel.pack(fill="x", pady=(0, 8), before=anchors[0])
        return True
    except Exception:
        return False


def normalize_operator_panel_order(workspace) -> dict[str, bool]:
    result = {
        "images": False,
        "editor": False,
        "source": False,
    }

    images_tab = getattr(workspace, "images_tab", None)
    if images_tab is not None:
        result["images"] = move_packed_panel_to_front(images_tab, IMAGE_PANEL_TITLE)

    content_tab = getattr(workspace, "content_tab", None)
    if content_tab is not None:
        # Move editor first, then source identity, so source identity ends up at
        # the absolute top and the manual/operator panel is directly beneath it.
        result["editor"] = move_packed_panel_to_front(content_tab, EDITOR_PANEL_TITLE)
        result["source"] = move_packed_panel_to_front(content_tab, SOURCE_PANEL_TITLE)

    return result


def install(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3i20_visible_operator_panels_installed", False):
        return

    original_init = workspace_class.__init__

    def __init__(self, app, product_id):
        original_init(self, app, product_id)
        self._phase49_3i20_panel_layout = normalize_operator_panel_order(self)

    workspace_class.__init__ = __init__
    workspace_class._phase49_3i20_visible_operator_panels_installed = True
