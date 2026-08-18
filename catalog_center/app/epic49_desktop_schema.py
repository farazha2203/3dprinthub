from __future__ import annotations

import json


PRODUCT_COLUMNS = {
    "download_image_limit": "INTEGER NOT NULL DEFAULT 10",
    "price_min": "INTEGER NOT NULL DEFAULT 0",
    "price_max": "INTEGER NOT NULL DEFAULT 0",
    # New independent selector contract. The legacy pair list remains as a
    # derived compatibility payload for older importers/releases.
    "material_options_json": "TEXT NOT NULL DEFAULT '[]'",
    "color_options_json": "TEXT NOT NULL DEFAULT '[]'",
    "material_color_options_json": "TEXT NOT NULL DEFAULT '[]'",
    "homepage_slider_enabled": "INTEGER NOT NULL DEFAULT 0",
    "homepage_slider_image_url": "TEXT NOT NULL DEFAULT ''",
    "homepage_slider_sort_order": "INTEGER NOT NULL DEFAULT 100",
    "homepage_slider_title_fa": "TEXT NOT NULL DEFAULT ''",
    "homepage_slider_description_fa": "TEXT NOT NULL DEFAULT ''",
    "homepage_slider_alt_text": "TEXT NOT NULL DEFAULT ''",
    "homepage_slider_button_text": "TEXT NOT NULL DEFAULT 'مشاهده محصول'",
    "homepage_slider_focus_keyword": "TEXT NOT NULL DEFAULT ''",
    "homepage_slider_transition_effect": "TEXT NOT NULL DEFAULT 'cinematic_fade'",
    "homepage_slider_transition_duration_ms": "INTEGER NOT NULL DEFAULT 1400",
    "homepage_slider_display_duration_ms": "INTEGER NOT NULL DEFAULT 7000",
    "server_product_id": "INTEGER NOT NULL DEFAULT 0",
    "server_product_revision": "INTEGER NOT NULL DEFAULT 0",
    "server_slider_id": "INTEGER NOT NULL DEFAULT 0",
    "server_slider_revision": "INTEGER NOT NULL DEFAULT 0",
    "server_updated_at": "TEXT NOT NULL DEFAULT ''",
    "last_sync_conflict": "TEXT NOT NULL DEFAULT ''",
}


COLOR_TYPES = (
    ("solid", "ساده"),
    ("transparent", "شفاف / شیشه‌ای"),
    ("translucent", "نیمه‌شفاف"),
    ("metallic", "متالیک"),
    ("silk", "Silk / ابریشمی"),
    ("dual", "دو رنگ"),
    ("multicolor", "چند رنگ"),
    ("gradient", "گرادیانی"),
)
COLOR_TYPE_CODES = {code for code, _label in COLOR_TYPES}


DEFAULT_MATERIALS = [
    "PLA", "PLA-CF", "HT-PLA-GF", "PETG", "PET-CF", "PETG-rCF08",
    "ABS", "ASA", "PC-FR", "TPU95", "PA6-CF20", "PA12-CF10", "PPS-CF10",
]


def _table_columns(db, table: str) -> set[str]:
    return {row["name"] for row in db.conn.execute(f"PRAGMA table_info({table})")}


def ensure_epic49_desktop_schema(db) -> None:
    """Add Epic49 desktop fields without deleting or rewriting runtime data."""
    existing = _table_columns(db, "products")
    for name, ddl in PRODUCT_COLUMNS.items():
        if name not in existing:
            db.conn.execute(f"ALTER TABLE products ADD COLUMN {name} {ddl}")

    db.conn.execute(
        """
        CREATE TABLE IF NOT EXISTS available_material_colors(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_name TEXT NOT NULL,
            color_name TEXT NOT NULL,
            hex_code TEXT NOT NULL DEFAULT '',
            color_type TEXT NOT NULL DEFAULT 'solid',
            secondary_hex TEXT NOT NULL DEFAULT '',
            tertiary_hex TEXT NOT NULL DEFAULT '',
            is_active INTEGER NOT NULL DEFAULT 1,
            sort_order INTEGER NOT NULL DEFAULT 100,
            UNIQUE(material_name, color_name)
        )
        """
    )
    color_columns = _table_columns(db, "available_material_colors")
    for name, ddl in {
        "color_type": "TEXT NOT NULL DEFAULT 'solid'",
        "secondary_hex": "TEXT NOT NULL DEFAULT ''",
        "tertiary_hex": "TEXT NOT NULL DEFAULT ''",
    }.items():
        if name not in color_columns:
            db.conn.execute(f"ALTER TABLE available_material_colors ADD COLUMN {name} {ddl}")
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
        SELECT id, material_name, color_name, hex_code, color_type,
               secondary_hex, tertiary_hex, is_active, sort_order
        FROM available_material_colors
        WHERE is_active=1
        ORDER BY material_name COLLATE NOCASE, sort_order, color_name COLLATE NOCASE, id
        """
    ).fetchall()
    return [dict(row) for row in rows]


def add_available_material_color(
    db,
    material_name: str,
    color_name: str,
    hex_code: str = "",
    color_type: str = "solid",
    secondary_hex: str = "",
    tertiary_hex: str = "",
) -> dict:
    ensure_epic49_desktop_schema(db)
    material = str(material_name or "").strip()
    color = str(color_name or "").strip()
    hex_value = str(hex_code or "").strip()
    kind = str(color_type or "solid").strip().lower()
    if kind not in COLOR_TYPE_CODES:
        kind = "solid"
    if not material:
        raise ValueError("نام متریال خالی است")
    if not color:
        raise ValueError("نام رنگ خالی است")
    db.conn.execute(
        """
        INSERT INTO available_material_colors(
            material_name,color_name,hex_code,color_type,secondary_hex,tertiary_hex,is_active
        ) VALUES(?,?,?,?,?,?,1)
        ON CONFLICT(material_name,color_name) DO UPDATE SET
            hex_code=excluded.hex_code,
            color_type=excluded.color_type,
            secondary_hex=excluded.secondary_hex,
            tertiary_hex=excluded.tertiary_hex,
            is_active=1
        """,
        (material, color, hex_value, kind, str(secondary_hex or "").strip(), str(tertiary_hex or "").strip()),
    )
    db.conn.commit()
    row = db.conn.execute(
        """
        SELECT id, material_name, color_name, hex_code, color_type,
               secondary_hex, tertiary_hex, is_active, sort_order
        FROM available_material_colors WHERE material_name=? AND color_name=?
        """,
        (material, color),
    ).fetchone()
    return dict(row)


def deactivate_available_material_color(db, row_id: int) -> None:
    ensure_epic49_desktop_schema(db)
    db.conn.execute("UPDATE available_material_colors SET is_active=0 WHERE id=?", (int(row_id),))
    db.conn.commit()


def normalize_material_options(value) -> list[str]:
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
        name = str(item.get("name") if isinstance(item, dict) else item or "").strip()
        if not name or name.casefold() in seen:
            continue
        seen.add(name.casefold())
        output.append(name)
    return output


def normalize_color_options(value) -> list[dict]:
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
        name = str(item.get("name") or item.get("color") or item.get("color_name") or "").strip()
        if not name:
            continue
        kind = str(item.get("color_type") or item.get("type") or "solid").strip().lower()
        if kind not in COLOR_TYPE_CODES:
            kind = "solid"
        key = (name.casefold(), kind)
        if key in seen:
            continue
        seen.add(key)
        output.append({
            "name": name,
            "hex": str(item.get("hex") or item.get("hex_code") or "").strip(),
            "color_type": kind,
            "secondary_hex": str(item.get("secondary_hex") or item.get("hex2") or "").strip(),
            "tertiary_hex": str(item.get("tertiary_hex") or item.get("hex3") or "").strip(),
        })
    return output


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
        kind = str(item.get("color_type") or item.get("type") or "solid").strip().lower()
        if kind not in COLOR_TYPE_CODES:
            kind = "solid"
        key = (material.casefold(), color.casefold(), kind)
        if key in seen:
            continue
        seen.add(key)
        output.append({
            "material": material,
            "color": color,
            "hex": str(item.get("hex") or item.get("hex_code") or "").strip(),
            "color_type": kind,
            "secondary_hex": str(item.get("secondary_hex") or item.get("hex2") or "").strip(),
            "tertiary_hex": str(item.get("tertiary_hex") or item.get("hex3") or "").strip(),
        })
    return output
