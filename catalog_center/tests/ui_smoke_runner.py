from __future__ import annotations
import json, tempfile
from pathlib import Path
import app.main as m

td=tempfile.TemporaryDirectory()
app=None
try:
    root=Path(td.name)
    m.ROOT=root
    m.DATA=root/'data'
    m.DB_FILE=m.DATA/'catalog.sqlite3'
    m.CONFIG_FILE=m.DATA/'config.json'
    m.PROFILE_ROOT=m.DATA/'profiles'
    m.HOST_MIRROR=root/'mirror'
    m.BATCH_ROOT=m.HOST_MIRROR/'imports'/'desktop_catalog'/'pending'
    app=m.App(); app.withdraw(); app.update_idletasks()
    assert hasattr(app,'published_tree')
    assert hasattr(app,'openai_key_entry')
    assert app.product_filter.get()=='work_queue'
    print('V83_UI_APP_INSTANTIATION=OK')
    app.on_close()
    app=None
    log_path=m.DATA/'logs'/'catalog-intelligence.log'
    probe=log_path.with_name('catalog-intelligence.release-check.log')
    log_path.replace(probe)
    print('V851_LOG_FILE_RELEASE=OK')
finally:
    if app is not None:
        app.on_close()
    td.cleanup()
