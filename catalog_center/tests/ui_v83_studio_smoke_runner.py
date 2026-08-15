from __future__ import annotations

import json
import tempfile
from pathlib import Path

from PIL import Image

import app.main as m
from app.product_studio import ProductStudio


td = tempfile.TemporaryDirectory()
app = None
studio = None
try:
    root = Path(td.name)
    m.ROOT = root
    m.DATA = root / "data"
    m.DB_FILE = m.DATA / "catalog.sqlite3"
    m.CONFIG_FILE = m.DATA / "config.json"
    m.PROFILE_ROOT = m.DATA / "profiles"
    m.HOST_MIRROR = root / "mirror"
    m.BATCH_ROOT = m.HOST_MIRROR / "imports" / "desktop_catalog" / "pending"

    app = m.App()
    app.withdraw()
    app.update_idletasks()

    # Clipboard must still be usable for OpenAI project keys.
    app.clipboard_clear()
    app.clipboard_append("sk-proj-v83-smoke")
    app.update()
    app.paste_openai_key()
    assert app.openai_key.get() == "sk-proj-v83-smoke"
    print("V83_OPENAI_PASTE=OK")

    # Persistent custom category contract.
    app.db.set_setting("custom_categories_json", json.dumps([{"slug": "car-interior", "name": "خودرو - قطعات داخلی"}], ensure_ascii=False))
    app.refresh_category_maps()
    assert app.category_label_to_slug["خودرو - قطعات داخلی"] == "car-interior"
    print("V83_CUSTOM_CATEGORY=OK")

    # Product with 25 real local images.
    local_dir = m.DATA / "collected" / "example" / "p25"
    imgdir = local_dir / "images"
    imgdir.mkdir(parents=True, exist_ok=True)
    urls = []
    manifest = []
    for i in range(25):
        p = imgdir / f"{i+1:03d}.png"
        Image.new("RGB", (360, 260), (i * 9 % 255, 150, 210)).save(p)
        u = f"https://example.test/images/{i+1}.png"
        urls.append(u)
        manifest.append({"url": u, "local_file": str(p)})
    (local_dir / "page_extract.json").write_text(json.dumps({"images": manifest}), encoding="utf-8")
    app.db.upsert_product({
        "source_code": "example",
        "external_id": "p25",
        "source_url": "https://example.test/products/p25",
        "source_title": "English product title",
        "source_description": "English product description",
        "source_category": "Automotive",
        "source_categories_json": json.dumps(["Automotive", "Interior"]),
        "source_specs_json": json.dumps({"Material": "PETG", "Files": "STL"}),
        "images_json": json.dumps(urls),
        "selected_images_json": json.dumps(urls[:3]),
        "primary_image_url": urls[0],
        "local_dir": str(local_dir),
        "estimated_weight_grams": 125,
        "material_price_per_gram": 2500,
    })
    row = app.db.conn.execute("SELECT id FROM products WHERE external_id='p25'").fetchone()
    pid = int(row["id"])
    app.current_product = pid
    app.refresh_products()
    if app.product_tree.exists(str(pid)):
        app.product_tree.selection_set(str(pid))
        app.load_product()
    app.update_idletasks()
    assert len(app._preview_items) == 25
    assert len(app.inline_gallery.winfo_children()) >= 9
    print("V83_INLINE_THUMBNAILS=OK")

    studio = ProductStudio(app, pid)
    studio.withdraw()
    studio.update_idletasks()
    assert len(studio._gallery_cards) == 25
    assert studio.source_url.get() == "https://example.test/products/p25"
    print("V83_PRODUCT_STUDIO_25_IMAGE_GALLERY=OK")

    # Primary/select/remove state should persist without touching files.
    studio.set_primary(urls[5])
    updated = app.db.product(pid)
    assert updated["primary_image_url"] == urls[5]
    assert json.loads(updated["selected_images_json"])[0] == urls[5]
    studio.toggle_selected(urls[7])
    updated = app.db.product(pid)
    assert urls[7] in json.loads(updated["selected_images_json"])
    print("V83_IMAGE_EDITING_STATE=OK")

    # Persian editable fields save and custom category mapping work.
    studio.content_title_fa.set("عنوان فارسی تست")
    studio._text_set(studio.content_short_fa, "توضیح کوتاه فارسی")
    studio._text_set(studio.content_desc_fa, "توضیحات کامل فارسی")
    studio.category_var.set("خودرو - قطعات داخلی")
    studio.final_price_var.set("990000")
    assert studio.save(silent=True)
    updated = app.db.product(pid)
    assert updated["title_fa"] == "عنوان فارسی تست"
    assert updated["local_category_slug"] == "car-interior"
    assert updated["price_is_final"] == 1
    print("V83_FAST_EDITOR_SAVE=OK")
finally:
    try:
        if studio is not None:
            studio.destroy()
    finally:
        try:
            if app is not None:
                app.on_close()
        finally:
            td.cleanup()
print("V83_PRODUCT_STUDIO_UI_SMOKE=OK")
