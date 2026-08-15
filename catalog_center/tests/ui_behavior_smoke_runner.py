from __future__ import annotations
import json,tempfile
from pathlib import Path
from PIL import Image
import app.main as m

td=tempfile.TemporaryDirectory();app=None
try:
    root=Path(td.name)
    m.ROOT=root;m.DATA=root/'data';m.DB_FILE=m.DATA/'catalog.sqlite3';m.CONFIG_FILE=m.DATA/'config.json';m.PROFILE_ROOT=m.DATA/'profiles';m.HOST_MIRROR=root/'mirror';m.BATCH_ROOT=m.HOST_MIRROR/'imports'/'desktop_catalog'/'pending'
    app=m.App();app.withdraw();app.update_idletasks()
    # Clipboard/Paste contract
    app.clipboard_clear();app.clipboard_append('test-key-v83-clipboard');app.update()
    app.paste_openai_key();assert app.openai_key.get()=='test-key-v83-clipboard'
    print('V83_OPENAI_PASTE=OK')
    # Bridge Token must support a copied .env assignment without persisting it in SQLite.
    app.clipboard_clear();app.clipboard_append('CATALOG_BRIDGE_TOKEN=unit-test-token-value\r\n');app.update()
    assert app.paste_bridge_token()=='break'
    assert app.bridge_token.get()=='unit-test-token-value'
    assert app.bridge_token_entry.bind('<Control-v>')
    assert app.bridge_token_entry.bind('<Control-V>')
    assert app.bridge_token_entry.bind('<Shift-Insert>')
    assert app.bridge_token_entry.bind('<Button-3>')
    assert app.bridge_token_entry.cget('show')=='•'
    app.toggle_bridge_token_visibility();assert app.bridge_token_entry.cget('show')==''
    app.toggle_bridge_token_visibility();assert app.bridge_token_entry.cget('show')=='•'
    assert app.db.setting('bridge_token','__not_stored__')=='__not_stored__'
    print('V854_BRIDGE_TOKEN_PASTE=OK')
    # 25-image gallery preparation contract
    local_dir=m.DATA/'collected'/'site_example'/'p25';imgdir=local_dir/'images';imgdir.mkdir(parents=True,exist_ok=True)
    urls=[];manifest=[]
    for i in range(25):
        p=imgdir/f'{i+1:03d}.png';Image.new('RGB',(320,240),(i*7%255,120,200)).save(p)
        u=f'https://example.test/images/{i+1}.png';urls.append(u);manifest.append({'url':u,'local_file':str(p)})
    (local_dir/'page_extract.json').write_text(json.dumps({'images':manifest}),encoding='utf-8')
    app.db.upsert_product({'source_code':'site_example','external_id':'p25','source_url':'https://example.test/p25','source_title':'25 images','images_json':json.dumps(urls),'selected_images_json':json.dumps(urls),'primary_image_url':urls[0],'local_dir':str(local_dir)})
    row=app.db.conn.execute("SELECT id FROM products WHERE external_id='p25'").fetchone();app.current_product=row['id'];app.prepare_product_gallery(app.db.product(row['id']))
    assert len(app._preview_items)==25
    print('V83_GALLERY_25_ITEMS=OK')
    # Gallery window itself must instantiate without error.
    app.open_image_manager();app.update_idletasks();tops=[w for w in app.winfo_children() if w.winfo_class()=='Toplevel'];assert tops
    print('V83_GALLERY_WINDOW=OK')
    for w in tops:w.destroy()
finally:
    if app is not None:
        app.on_close()
    td.cleanup()
