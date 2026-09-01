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
    # Phase49.3I.48 owner workflow state. These are additive Catalog-local
    # facts; they do not change the Production Django schema.
    "rejected_thumbnail_path": "TEXT NOT NULL DEFAULT ''",
    "ai_completed_once": "INTEGER NOT NULL DEFAULT 0",
    "ai_completed_at": "TEXT NOT NULL DEFAULT ''",
    "ai_completed_source_mode": "TEXT NOT NULL DEFAULT ''",
    "ai_completed_provider": "TEXT NOT NULL DEFAULT ''",
    "ai_completed_model": "TEXT NOT NULL DEFAULT ''",
    # Explicit global owner policy: source/license review is allowed for every
    # Product. We preserve source license text/status separately instead of
    # inventing a license name.
    "source_license_owner_approved": "INTEGER NOT NULL DEFAULT 1",
}


# Historical COLOR_TYPES is kept for backward compatibility with the mature
# Tk/editor payloads. Phase49.3I.48 separates *color behaviour* from *finish*
# so the Store can render one/two/multi/gradient/color-shift independently
# from matte/glossy/metallic/transparent/silk appearance.
COLOR_TYPES = (
    ("solid", "ساده"),
    ("transparent", "شفاف / شیشه‌ای"),
    ("translucent", "نیمه‌شفاف"),
    ("metallic", "متالیک"),
    ("silk", "Silk / ابریشمی"),
    ("dual", "دو رنگ"),
    ("multicolor", "چند رنگ"),
    ("gradient", "گرادیانی"),
    ("color_shift", "تغییررنگ / Color Shift"),
)
COLOR_TYPE_CODES = {code for code, _label in COLOR_TYPES}

COLOR_BEHAVIORS = (
    ("solid", "تک‌رنگ"),
    ("dual", "دو‌رنگ"),
    ("multicolor", "چندرنگ"),
    ("gradient", "گرادیانی"),
    ("color_shift", "تغییررنگ"),
)
COLOR_BEHAVIOR_CODES = {code for code, _label in COLOR_BEHAVIORS}

COLOR_FINISHES = (
    ("matte", "مات"),
    ("glossy", "براق"),
    ("metallic", "متالیک"),
    ("transparent_matte", "شیشه‌ای مات"),
    ("transparent_glossy", "شیشه‌ای براق"),
    ("silk", "Silk / ابریشمی"),
)
COLOR_FINISH_CODES = {code for code, _label in COLOR_FINISHES}

_LEGACY_VISUAL_MAP = {
    "transparent": ("solid", "transparent_glossy"),
    "translucent": ("solid", "transparent_matte"),
    "metallic": ("solid", "metallic"),
    "silk": ("solid", "silk"),
    "triple": ("multicolor", "glossy"),
}


def normalize_color_visual(
    color_type: str,
    color_finish: str = "",
) -> tuple[str, str]:
    raw_type = str(color_type or "solid").strip().lower()
    raw_finish = str(color_finish or "").strip().lower()
    if raw_type in _LEGACY_VISUAL_MAP:
        behavior, legacy_finish = _LEGACY_VISUAL_MAP[raw_type]
        return behavior, raw_finish if raw_finish in COLOR_FINISH_CODES else legacy_finish
    behavior = raw_type if raw_type in COLOR_BEHAVIOR_CODES else "solid"
    finish = raw_finish if raw_finish in COLOR_FINISH_CODES else "matte"
    return behavior, finish


def normalize_palette_hexes(value, *fallbacks: str) -> list[str]:
    if isinstance(value, str):
        try:
            parsed = json.loads(value or "[]")
        except Exception:
            parsed = []
    else:
        parsed = value
    items = list(parsed) if isinstance(parsed, list) else []
    items.extend(fallbacks)
    output: list[str] = []
    seen: set[str] = set()
    for raw in items:
        text = str(raw or "").strip().upper()
        if not text:
            continue
        if not text.startswith("#"):
            text = "#" + text
        if len(text) not in {4, 7}:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        output.append(text)
        if len(output) >= 7:
            break
    return output


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
    db.conn.execute(
        """
        CREATE TABLE IF NOT EXISTS available_filament_offers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_name TEXT NOT NULL,
            brand_name TEXT NOT NULL DEFAULT '',
            manufacturer_name TEXT NOT NULL DEFAULT '',
            color_name TEXT NOT NULL,
            hex_code TEXT NOT NULL DEFAULT '',
            color_type TEXT NOT NULL DEFAULT 'solid',
            secondary_hex TEXT NOT NULL DEFAULT '',
            tertiary_hex TEXT NOT NULL DEFAULT '',
            roll_weight_grams INTEGER NOT NULL DEFAULT 1000,
            stock_roll_count REAL NOT NULL DEFAULT 0,
            purchase_price_per_roll INTEGER NOT NULL DEFAULT 0,
            sale_price_per_roll INTEGER NOT NULL DEFAULT 0,
            usd_price_per_roll REAL NOT NULL DEFAULT 0,
            usd_fx_rate_toman REAL NOT NULL DEFAULT 0,
            print_hourly_rate INTEGER NOT NULL DEFAULT 0,
            supervision_hourly_rate INTEGER NOT NULL DEFAULT 0,
            preheat_hours REAL NOT NULL DEFAULT 0,
            preheat_temperature_c REAL NOT NULL DEFAULT 0,
            preheat_hourly_rate INTEGER NOT NULL DEFAULT 0,
            filament_image_url TEXT NOT NULL DEFAULT '',
            filament_image_path TEXT NOT NULL DEFAULT '',
            color_finish TEXT NOT NULL DEFAULT 'matte',
            palette_hex_json TEXT NOT NULL DEFAULT '[]',
            is_active INTEGER NOT NULL DEFAULT 1,
            sort_order INTEGER NOT NULL DEFAULT 100,
            UNIQUE(material_name, brand_name, color_name)
        )
        """
    )
    offer_columns = _table_columns(db, "available_filament_offers")
    for name, ddl in {
        "print_hourly_rate": "INTEGER NOT NULL DEFAULT 0",
        "supervision_hourly_rate": "INTEGER NOT NULL DEFAULT 0",
        "preheat_hours": "REAL NOT NULL DEFAULT 0",
        "preheat_temperature_c": "REAL NOT NULL DEFAULT 0",
        "preheat_hourly_rate": "INTEGER NOT NULL DEFAULT 0",
        "filament_image_url": "TEXT NOT NULL DEFAULT ''",
        "filament_image_path": "TEXT NOT NULL DEFAULT ''",
        "color_finish": "TEXT NOT NULL DEFAULT 'matte'",
        "palette_hex_json": "TEXT NOT NULL DEFAULT '[]'",
    }.items():
        if name not in offer_columns:
            db.conn.execute(f"ALTER TABLE available_filament_offers ADD COLUMN {name} {ddl}")
    # One-time additive compatibility import. The mature color table is retained;
    # new engineering data lives in the brand-aware offer table.
    db.conn.execute(
        """
        INSERT OR IGNORE INTO available_filament_offers(
            material_name, color_name, hex_code, color_type,
            secondary_hex, tertiary_hex, is_active, sort_order
        )
        SELECT material_name, color_name, hex_code, color_type,
               secondary_hex, tertiary_hex, is_active, sort_order
        FROM available_material_colors
        """
    )
    db.conn.commit()


def effective_filament_offer_price_per_gram(item: dict) -> float:
    """Owner pricing rule: sale price per roll divided by roll weight."""
    try:
        roll = max(1.0, float(item.get("roll_weight_grams") or 1000))
    except Exception:
        roll = 1000.0
    try:
        sale_roll = max(0.0, float(item.get("sale_price_per_roll") or 0))
    except Exception:
        sale_roll = 0.0
    return (sale_roll / roll) if sale_roll > 0 else 0.0


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
        SELECT id, material_name, brand_name, manufacturer_name, color_name,
               hex_code, color_type, secondary_hex, tertiary_hex,
               roll_weight_grams, stock_roll_count, purchase_price_per_roll,
               sale_price_per_roll, usd_price_per_roll, usd_fx_rate_toman,
               print_hourly_rate, supervision_hourly_rate,
               preheat_hours, preheat_temperature_c, preheat_hourly_rate,
               filament_image_url, filament_image_path, color_finish,
               palette_hex_json, is_active, sort_order
        FROM available_filament_offers
        WHERE is_active=1
        ORDER BY material_name COLLATE NOCASE, brand_name COLLATE NOCASE,
                 sort_order, color_name COLLATE NOCASE, id
        """
    ).fetchall()
    output = []
    for row in rows:
        item = dict(row)
        item["effective_sale_price_per_gram"] = effective_filament_offer_price_per_gram(item)
        output.append(item)
    return output


def add_available_material_color(
    db,
    material_name: str,
    color_name: str,
    hex_code: str = "",
    color_type: str = "solid",
    secondary_hex: str = "",
    tertiary_hex: str = "",
    *,
    brand_name: str = "",
    manufacturer_name: str = "",
    roll_weight_grams: int = 1000,
    stock_roll_count: float = 0,
    purchase_price_per_roll: int = 0,
    sale_price_per_roll: int = 0,
    usd_price_per_roll: float = 0,
    usd_fx_rate_toman: float = 0,
    print_hourly_rate: int = 0,
    supervision_hourly_rate: int = 0,
    preheat_hours: float = 0,
    preheat_temperature_c: float = 0,
    preheat_hourly_rate: int = 0,
    filament_image_url: str = "",
    filament_image_path: str = "",
    color_finish: str = "matte",
    palette_hexes=None,
) -> dict:
    ensure_epic49_desktop_schema(db)
    material = str(material_name or "").strip()
    brand = str(brand_name or "").strip()
    manufacturer = str(manufacturer_name or "").strip()
    color = str(color_name or "").strip()
    hex_value = str(hex_code or "").strip()
    kind, finish = normalize_color_visual(color_type, color_finish)
    palette = normalize_palette_hexes(
        palette_hexes,
        hex_value,
        secondary_hex,
        tertiary_hex,
    )
    if palette:
        hex_value = palette[0]
    secondary_hex = palette[1] if len(palette) > 1 else ""
    tertiary_hex = palette[2] if len(palette) > 2 else ""
    if not material:
        raise ValueError("نام متریال خالی است")
    if not color:
        raise ValueError("نام رنگ خالی است")
    roll_weight = max(1, int(float(roll_weight_grams or 1000)))
    stock_rolls = max(0.0, float(stock_roll_count or 0))
    purchase = max(0, int(float(purchase_price_per_roll or 0)))
    sale = max(0, int(float(sale_price_per_roll or 0)))
    usd = max(0.0, float(usd_price_per_roll or 0))
    fx = max(0.0, float(usd_fx_rate_toman or 0))
    print_hourly = max(0, int(float(print_hourly_rate or 0)))
    supervision_hourly = max(0, int(float(supervision_hourly_rate or 0)))
    preheat_h = max(0.0, float(preheat_hours or 0))
    preheat_temp = max(0.0, float(preheat_temperature_c or 0))
    preheat_rate = max(0, int(float(preheat_hourly_rate or 0)))
    image_url = str(filament_image_url or "").strip()
    image_path = str(filament_image_path or "").strip()
    db.conn.execute(
        """
        INSERT INTO available_filament_offers(
            material_name,brand_name,manufacturer_name,color_name,hex_code,color_type,
            secondary_hex,tertiary_hex,roll_weight_grams,stock_roll_count,
            purchase_price_per_roll,sale_price_per_roll,usd_price_per_roll,
            usd_fx_rate_toman,print_hourly_rate,supervision_hourly_rate,
            preheat_hours,preheat_temperature_c,preheat_hourly_rate,
            filament_image_url,filament_image_path,color_finish,palette_hex_json,is_active
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)
        ON CONFLICT(material_name,brand_name,color_name) DO UPDATE SET
            manufacturer_name=excluded.manufacturer_name,
            hex_code=excluded.hex_code,
            color_type=excluded.color_type,
            secondary_hex=excluded.secondary_hex,
            tertiary_hex=excluded.tertiary_hex,
            roll_weight_grams=excluded.roll_weight_grams,
            stock_roll_count=excluded.stock_roll_count,
            purchase_price_per_roll=excluded.purchase_price_per_roll,
            sale_price_per_roll=excluded.sale_price_per_roll,
            usd_price_per_roll=excluded.usd_price_per_roll,
            usd_fx_rate_toman=excluded.usd_fx_rate_toman,
            print_hourly_rate=excluded.print_hourly_rate,
            supervision_hourly_rate=excluded.supervision_hourly_rate,
            preheat_hours=excluded.preheat_hours,
            preheat_temperature_c=excluded.preheat_temperature_c,
            preheat_hourly_rate=excluded.preheat_hourly_rate,
            filament_image_url=excluded.filament_image_url,
            filament_image_path=excluded.filament_image_path,
            color_finish=excluded.color_finish,
            palette_hex_json=excluded.palette_hex_json,
            is_active=1
        """,
        (
            material, brand, manufacturer, color, hex_value, kind,
            str(secondary_hex or "").strip(), str(tertiary_hex or "").strip(),
            roll_weight, stock_rolls, purchase, sale, usd, fx,
            print_hourly, supervision_hourly, preheat_h, preheat_temp,
            preheat_rate, image_url, image_path, finish,
            json.dumps(palette, ensure_ascii=False),
        ),
    )
    db.conn.commit()
    row = db.conn.execute(
        """
        SELECT id, material_name, brand_name, manufacturer_name, color_name,
               hex_code, color_type, secondary_hex, tertiary_hex,
               roll_weight_grams, stock_roll_count, purchase_price_per_roll,
               sale_price_per_roll, usd_price_per_roll, usd_fx_rate_toman,
               print_hourly_rate, supervision_hourly_rate,
               preheat_hours, preheat_temperature_c, preheat_hourly_rate,
               filament_image_url, filament_image_path, color_finish,
               palette_hex_json, is_active, sort_order
        FROM available_filament_offers
        WHERE material_name=? AND brand_name=? AND color_name=?
        """,
        (material, brand, color),
    ).fetchone()
    item = dict(row)
    item["effective_sale_price_per_gram"] = effective_filament_offer_price_per_gram(item)
    return item


def deactivate_available_material_color(db, row_id: int) -> None:
    ensure_epic49_desktop_schema(db)
    db.conn.execute("UPDATE available_filament_offers SET is_active=0 WHERE id=?", (int(row_id),))
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
        kind, finish = normalize_color_visual(
            item.get("color_type") or item.get("type") or "solid",
            item.get("color_finish") or item.get("finish") or "",
        )
        palette = normalize_palette_hexes(
            item.get("palette_hexes") or item.get("palette_hex_json") or [],
            item.get("hex") or item.get("hex_code") or "",
            item.get("secondary_hex") or item.get("hex2") or "",
            item.get("tertiary_hex") or item.get("hex3") or "",
        )
        key = (name.casefold(), kind, finish)
        if key in seen:
            continue
        seen.add(key)
        output.append({
            "name": name,
            "hex": palette[0] if palette else "",
            "color_type": kind,
            "color_finish": finish,
            "palette_hexes": palette,
            "secondary_hex": palette[1] if len(palette) > 1 else "",
            "tertiary_hex": palette[2] if len(palette) > 2 else "",
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
        kind, finish = normalize_color_visual(
            item.get("color_type") or item.get("type") or "solid",
            item.get("color_finish") or item.get("finish") or "",
        )
        palette = normalize_palette_hexes(
            item.get("palette_hexes") or item.get("palette_hex_json") or [],
            item.get("hex") or item.get("hex_code") or "",
            item.get("secondary_hex") or item.get("hex2") or "",
            item.get("tertiary_hex") or item.get("hex3") or "",
        )
        brand = str(item.get("brand") or item.get("brand_name") or "").strip()
        key = (material.casefold(), brand.casefold(), color.casefold(), kind, finish)
        if key in seen:
            continue
        seen.add(key)
        output.append({
            "material": material,
            "brand": brand,
            # Manufacturer is a hidden compatibility alias. Owner-facing UI
            # uses Brand as the single authority.
            "manufacturer": brand,
            "color": color,
            "hex": palette[0] if palette else "",
            "color_type": kind,
            "color_finish": finish,
            "palette_hexes": palette,
            "secondary_hex": palette[1] if len(palette) > 1 else "",
            "tertiary_hex": palette[2] if len(palette) > 2 else "",
            "roll_weight_grams": max(1, int(float(item.get("roll_weight_grams") or 1000))),
            "stock_roll_count": max(0.0, float(item.get("stock_roll_count") or 0)),
            "purchase_price_per_roll": max(0, int(float(item.get("purchase_price_per_roll") or 0))),
            "sale_price_per_roll": max(0, int(float(item.get("sale_price_per_roll") or 0))),
            "usd_price_per_roll": max(0.0, float(item.get("usd_price_per_roll") or 0)),
            "usd_fx_rate_toman": max(0.0, float(item.get("usd_fx_rate_toman") or 0)),
            "print_hourly_rate": max(0, int(float(item.get("print_hourly_rate") or 0))),
            "supervision_hourly_rate": max(0, int(float(item.get("supervision_hourly_rate") or 0))),
            "preheat_hours": max(0.0, float(item.get("preheat_hours") or 0)),
            "preheat_temperature_c": max(0.0, float(item.get("preheat_temperature_c") or 0)),
            "preheat_hourly_rate": max(0, int(float(item.get("preheat_hourly_rate") or 0))),
            "filament_image_url": str(item.get("filament_image_url") or item.get("image_url") or "").strip(),
            "filament_image_path": str(item.get("filament_image_path") or "").strip(),
            "fixed_product_price": max(0, int(float(item.get("fixed_product_price") or 0))),
        })
    return output
