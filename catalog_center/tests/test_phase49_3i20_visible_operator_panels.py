from __future__ import annotations

import unittest

from app.phase49_3i20_visible_operator_panels import (
    EDITOR_PANEL_TITLE,
    IMAGE_PANEL_TITLE,
    SOURCE_PANEL_TITLE,
    move_packed_panel_to_front,
    normalize_operator_panel_order,
)


class FakeWidget:
    def __init__(self, parent, text="", manager="pack"):
        self.parent = parent
        self.text = text
        self.manager = manager
        self.last_pack = None
        parent.children.append(self)

    def cget(self, key):
        if key == "text":
            return self.text
        raise KeyError(key)

    def winfo_manager(self):
        return self.manager

    def pack_forget(self):
        if self in self.parent.children:
            self.parent.children.remove(self)
        self.manager = ""

    def pack(self, **kwargs):
        before = kwargs.get("before")
        self.last_pack = kwargs
        self.manager = "pack"
        if self in self.parent.children:
            self.parent.children.remove(self)
        if before in self.parent.children:
            self.parent.children.insert(self.parent.children.index(before), self)
        else:
            self.parent.children.append(self)


class FakeParent:
    def __init__(self):
        self.children = []

    def winfo_children(self):
        return list(self.children)


class FakeWorkspace:
    def __init__(self):
        self.images_tab = FakeParent()
        self.content_tab = FakeParent()


class Phase493I20VisibleOperatorPanelsTests(unittest.TestCase):
    def test_single_panel_moves_before_expandable_content(self):
        parent = FakeParent()
        toolbar = FakeWidget(parent, "toolbar")
        gallery = FakeWidget(parent, "gallery")
        panel = FakeWidget(parent, IMAGE_PANEL_TITLE)

        self.assertTrue(move_packed_panel_to_front(parent, IMAGE_PANEL_TITLE))
        self.assertEqual(parent.children, [panel, toolbar, gallery])
        self.assertIs(panel.last_pack["before"], toolbar)
        self.assertEqual(panel.last_pack["fill"], "x")

    def test_workspace_order_keeps_source_then_editor_before_content(self):
        workspace = FakeWorkspace()

        image_bar = FakeWidget(workspace.images_tab, "image bar")
        image_gallery = FakeWidget(workspace.images_tab, "image gallery")
        image_panel = FakeWidget(workspace.images_tab, IMAGE_PANEL_TITLE)

        toolbar = FakeWidget(workspace.content_tab, "toolbar")
        editor = FakeWidget(workspace.content_tab, "editor")
        correction = FakeWidget(workspace.content_tab, EDITOR_PANEL_TITLE)
        source = FakeWidget(workspace.content_tab, SOURCE_PANEL_TITLE)

        result = normalize_operator_panel_order(workspace)

        self.assertEqual(result, {"images": True, "editor": True, "source": True})
        self.assertEqual(workspace.images_tab.children, [image_panel, image_bar, image_gallery])
        self.assertEqual(
            workspace.content_tab.children,
            [source, correction, toolbar, editor],
        )

    def test_missing_panel_is_safe_noop(self):
        parent = FakeParent()
        child = FakeWidget(parent, "existing")
        self.assertFalse(move_packed_panel_to_front(parent, "missing"))
        self.assertEqual(parent.children, [child])


if __name__ == "__main__":
    unittest.main()
