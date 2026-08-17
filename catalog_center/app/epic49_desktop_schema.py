from __future__ import annotations

import json


PRODUCT_COLUMNS = {
    "download_image_limit": "INTEGER NOT NULL DEFAULT 10",
    "price_min": "INTEGER NOT NULL DEFAULT 0",
    "price_max": "INTEGER NOT NULL DEFAULT 0",
    "material_color_options_json": "TEXT NOT NULL DEFAULT '[]'",
    "homepage_slider_enabled": "INTEGER NOT NULL DEFAULT 0",
    "homepage_slider_image_url": "TEXT NOT NULL DEFAULT ''",
    "homepage_slider_sort_order": "INTEGER NOT NULL DEFAULT 100",
    "homepage_slider_title_fa": "TEXT NOT NULL DEFAULT ''",
    "homepage_slider_description_fa": "TEXT NOT NULL DEFAULT ''",
    "homepage_slider_alt_text": "TEXT NOT NULL DEFAULT ''",
    "homepage_slider_button_text": "TEXT NOT NULL DEFAULT 'مشاهده محصول'",
    "homepage_slider_focus_keyword": "TEXT NOT NULL DEFAULT ''",
}


def ensure_epic49_desktop_schema(db) -> None:
    """Add Epic49 final desktop fields without deleting or rewriting runtime data."""
    existing = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
    changed = False
    for name, ddl in PRODUCT_COLUMNS.items():
        if name not in existing:
            db.conn.execute(f"ALTER TABLE products ADD COLUMN {name} {ddl}")
            changed = True

    db.conn.execute(
        """
        CREATE TABLE IF NOT EXISTS available_material_colors(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_name TEXT NOT NULL,
            color_name TEXT NOT NULL,
            hex_code TEXT NOT NULL DEFAULT '',
            is_active INTEGER NOT NULL DEFAULT 1,
            sort_order INTEGER NOT NULL DEFAULT 100,
            UNIQUE(material_name, color_name)
        )
        """
    )
    if changed:
        db.conn.commit()
    else:
        db.conn.commit()


def install(app_module) -> None:
    """Ensure the additive desktop schema immediately after the main App creates its DB."""
    app_cls = app_module.App
    if getattr(app_cls, "_epic49_schema_installed", False):
        return
    original_init = app_cls.__init__

    def wrapped_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        ensure_epic49_desktop_schema(self.db)

    app_cls.__init__ = wrapped_init
    app_cls._epic49_schema_installed = True


def list_available_material_colors(db) -> list[dict]:
    ensure_epic49_desktop_schema(db)
    rows = db.conn.execute(
        """
        SELECT id, material_name, color_name, hex_code, is_active, sort_order
        FROM available_material_colors
        WHERE is_active=1
        ORDER BY material_name COLLATE NOCASE, sort_order, color_name COLLATE NOCASE, id
        """
    ).fetchall()
    return [dict(row) for row in rows]


def add_available_material_color(db, material_name: str, color_name: str, hex_code: str = "") -> dict:
    ensure_epic49_desktop_schema(db)
    material = str(material_name or "").strip()
    color = str(color_name or "").strip()
    hex_value = str(hex_code or "").strip()
    if not material:
        raise ValueError("نام متریال خالی است")
    if not color:
        raise ValueError("نام رنگ خالی است")
    db.conn.execute(
        """
        INSERT INTO available_material_colors(material_name,color_name,hex_code,is_active)
        VALUES(?,?,?,1)
        ON CONFLICT(material_name,color_name) DO UPDATE SET
            hex_code=excluded.hex_code,
            is_active=1
        """,
        (material, color, hex_value),
    )
    db.conn.commit()
    row = db.conn.execute(
        """
        SELECT id, material_name, color_name, hex_code, is_active, sort_order
        FROM available_material_colors WHERE material_name=? AND color_name=?
        """,
        (material, color),
    ).fetchone()
    return dict(row)


def deactivate_available_material_color(db, row_id: int) -> None:
    ensure_epic49_desktop_schema(db)
    db.conn.execute("UPDATE available_material_colors SET is_active=0 WHERE id=?", (int(row_id),))
    db.conn.commit()


def normalize_material_color_options(value) -> list[dict]:
    if isinstance(value, str):
        try:
            value = json.loads(value or "[]")
        except Exception:
            value = []
    if not isinstance(value, list):
        return []
    output = []
    seen = set()
    for item in value:
        if not isinstance(item, dict):
            continue
        material = str(item.get("material") or item.get("material_name") or "").strip()
        color = str(item.get("color") or item.get("color_name") or "").strip()
        if not material or not color:
            continue
        key = (material.casefold(), color.casefold())
        if key in seen:
            continue
        seen.add(key)
        output.append({
            "material": material,
            "color": color,
            "hex": str(item.get("hex") or item.get("hex_code") or "").strip(),
        })
    return output
