from __future__ import annotations

import ast
import unittest
from pathlib import Path

import app.main as main_module


class V8RuntimeContractTests(unittest.TestCase):
    def _app_class_ast(self):
        source_path = Path(main_module.__file__)
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        app_class = next(
            node for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "App"
        )
        return app_class

    def test_refresh_all_exists(self):
        self.assertTrue(hasattr(main_module.App, "refresh_all"))
        self.assertTrue(callable(getattr(main_module.App, "refresh_all")))

    def test_all_direct_self_method_calls_resolve(self):
        app_class = self._app_class_ast()
        methods = {
            node.name for node in app_class.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        inherited_tk_methods = {
            "after", "configure", "destroy", "geometry", "mainloop",
            "minsize", "protocol", "title", "clipboard_get",
        }
        missing = {}
        for node in ast.walk(app_class):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.value.id == "self"
            ):
                continue
            if func.attr not in methods and func.attr not in inherited_tk_methods:
                missing.setdefault(func.attr, []).append(node.lineno)
        self.assertEqual(missing, {}, f"Unresolved self method calls: {missing}")

    def test_source_map_is_initialized_before_runtime_use(self):
        app_class = self._app_class_ast()
        refresh = next(
            node for node in app_class.body
            if isinstance(node, ast.FunctionDef) and node.name == "refresh_all"
        )
        assigns_source_map = any(
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "self"
            and node.attr == "source_map"
            and isinstance(node.ctx, ast.Store)
            for node in ast.walk(refresh)
        )
        self.assertTrue(assigns_source_map)


if __name__ == "__main__":
    unittest.main(verbosity=2)
