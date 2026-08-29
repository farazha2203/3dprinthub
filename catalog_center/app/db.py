from __future__ import annotations
import sqlite3
import time
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SCHEMA_VERSION = 7

def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def normalize_url(value: str) -> str:
    parsed = urlsplit((value or "").strip())
    clean_query = [
        (k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
        if k.lower() not in {
            "utm_source","utm_medium","utm_campaign","utm_term",
            "utm_content","ref","source","fbclid","gclid"
        }
    ]
    return urlunsplit((
        (parsed.scheme or "https").lower(),
        parsed.netloc.lower(),
        parsed.path.rstrip("/") or "/",
        urlencode(sorted(clean_query)),
        "",
    ))

class Database:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init()

    def _init(self):
        self.conn.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS sources(
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            methods_json TEXT NOT NULL DEFAULT '[]',
            listing_urls_json TEXT NOT NULL DEFAULT '[]',
            model_url_pattern TEXT NOT NULL DEFAULT '',
            requires_login INTEGER NOT NULL DEFAULT 0,
            reference_only INTEGER NOT NULL DEFAULT 0,
            schedule_enabled INTEGER NOT NULL DEFAULT 0,
            schedule_time TEXT NOT NULL DEFAULT '03:00',
            daily_limit INTEGER NOT NULL DEFAULT 20,
            min_delay INTEGER NOT NULL DEFAULT 45,
            max_delay INTEGER NOT NULL DEFAULT 90,
            cooldown_until INTEGER NOT NULL DEFAULT 0,
            last_scan_at TEXT NOT NULL DEFAULT '',
            last_error TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS discovered_urls(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_code TEXT NOT NULL,
            external_id TEXT NOT NULL DEFAULT '',
            url TEXT NOT NULL,
            normalized_url TEXT NOT NULL,
            discovered_from TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'new',
            attempts INTEGER NOT NULL DEFAULT 0,
            last_error TEXT NOT NULL DEFAULT '',
            discovered_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(source_code, normalized_url)
        );
        CREATE UNIQUE INDEX IF NOT EXISTS ux_discovered_external
        ON discovered_urls(source_code, external_id)
        WHERE external_id <> '';

        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_code TEXT NOT NULL,
            external_id TEXT NOT NULL,
            source_url TEXT NOT NULL,
            normalized_url TEXT NOT NULL,
            source_title TEXT NOT NULL DEFAULT '',
            source_short_description TEXT NOT NULL DEFAULT '',
            source_description TEXT NOT NULL DEFAULT '',
            title_fa TEXT NOT NULL DEFAULT '',
            short_description_fa TEXT NOT NULL DEFAULT '',
            description_fa TEXT NOT NULL DEFAULT '',
            author_name TEXT NOT NULL DEFAULT '',
            license_name TEXT NOT NULL DEFAULT '',
            license_url TEXT NOT NULL DEFAULT '',
            source_category TEXT NOT NULL DEFAULT '',
            local_category_slug TEXT NOT NULL DEFAULT 'external-other',
            tags_json TEXT NOT NULL DEFAULT '[]',
            images_json TEXT NOT NULL DEFAULT '[]',
            file_links_json TEXT NOT NULL DEFAULT '[]',
            selected_images_json TEXT NOT NULL DEFAULT '[]',
            selected_file_links_json TEXT NOT NULL DEFAULT '[]',
            source_specs_json TEXT NOT NULL DEFAULT '{}',
            source_price REAL,
            source_currency TEXT NOT NULL DEFAULT '',
            workflow_status TEXT NOT NULL DEFAULT 'review',
            upload_ready INTEGER NOT NULL DEFAULT 0,
            custom_notes TEXT NOT NULL DEFAULT '',
            primary_image_url TEXT NOT NULL DEFAULT '',
            local_dir TEXT NOT NULL DEFAULT '',
            estimated_weight_grams REAL,
            estimated_print_minutes REAL,
            material_price_per_gram INTEGER NOT NULL DEFAULT 0,
            suggested_price INTEGER NOT NULL DEFAULT 500000,
            final_price INTEGER NOT NULL DEFAULT 0,
            price_is_final INTEGER NOT NULL DEFAULT 0,
            approved_for_sale INTEGER NOT NULL DEFAULT 0,
            publish_as_product INTEGER NOT NULL DEFAULT 0,
            publish_as_portfolio INTEGER NOT NULL DEFAULT 0,
            translation_status TEXT NOT NULL DEFAULT 'pending',
            commercial_status TEXT NOT NULL DEFAULT 'review',
            reference_only INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(source_code, external_id),
            UNIQUE(source_code, normalized_url)
        );
        CREATE TABLE IF NOT EXISTS scan_runs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_code TEXT NOT NULL,
            mode TEXT NOT NULL,
            method TEXT NOT NULL,
            requested_limit INTEGER NOT NULL DEFAULT 0,
            discovered_count INTEGER NOT NULL DEFAULT 0,
            collected_count INTEGER NOT NULL DEFAULT 0,
            duplicate_count INTEGER NOT NULL DEFAULT 0,
            failed_count INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'running',
            started_at TEXT NOT NULL,
            finished_at TEXT NOT NULL DEFAULT '',
            message TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS product_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            before_json TEXT NOT NULL DEFAULT '{}',
            after_json TEXT NOT NULL DEFAULT '{}',
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS ix_product_history_product ON product_history(product_id, id DESC);
        CREATE TABLE IF NOT EXISTS sync_receipts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            batch_uuid TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT '',
            server_id TEXT NOT NULL DEFAULT '',
            payload_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS ix_sync_receipts_product ON sync_receipts(product_id, id DESC);
        CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """)
        self.conn.commit()
        existing_columns = {row["name"] for row in self.conn.execute("PRAGMA table_info(products)")}
        additions = {
            "file_links_json": "TEXT NOT NULL DEFAULT '[]'",
            "selected_images_json": "TEXT NOT NULL DEFAULT '[]'",
            "selected_file_links_json": "TEXT NOT NULL DEFAULT '[]'",
            "source_specs_json": "TEXT NOT NULL DEFAULT '{}'",
            "source_price": "REAL",
            "source_currency": "TEXT NOT NULL DEFAULT ''",
            "workflow_status": "TEXT NOT NULL DEFAULT 'review'",
            "upload_ready": "INTEGER NOT NULL DEFAULT 0",
            "custom_notes": "TEXT NOT NULL DEFAULT ''",
            "source_categories_json": "TEXT NOT NULL DEFAULT '[]'",
            "categories_fa_json": "TEXT NOT NULL DEFAULT '[]'",
            "specs_fa_json": "TEXT NOT NULL DEFAULT '{}'",
            "tags_fa_json": "TEXT NOT NULL DEFAULT '[]'",
            "seo_title_fa": "TEXT NOT NULL DEFAULT ''",
            "seo_description_fa": "TEXT NOT NULL DEFAULT ''",
            "sales_bullets_json": "TEXT NOT NULL DEFAULT '[]'",
            "social_caption_fa": "TEXT NOT NULL DEFAULT ''",
            "image_alt_texts_json": "TEXT NOT NULL DEFAULT '[]'",
            "ai_suggested_category_slug": "TEXT NOT NULL DEFAULT ''",
            "ai_confidence": "REAL",
            "content_pack_json": "TEXT NOT NULL DEFAULT '{}'",
            "source_snapshot_json": "TEXT NOT NULL DEFAULT '{}'",
            "fingerprint": "TEXT NOT NULL DEFAULT ''",
            "source_hash": "TEXT NOT NULL DEFAULT ''",
            "source_state": "TEXT NOT NULL DEFAULT 'active'",
            "last_refetched_at": "TEXT NOT NULL DEFAULT ''",
            "server_id": "TEXT NOT NULL DEFAULT ''",
            "server_status": "TEXT NOT NULL DEFAULT ''",
            "server_ack_json": "TEXT NOT NULL DEFAULT '{}'",
            "last_synced_at": "TEXT NOT NULL DEFAULT ''",
            "source_rating": "REAL",
            "source_rating_count": "INTEGER NOT NULL DEFAULT 0",
            "source_like_count": "INTEGER NOT NULL DEFAULT 0",
            "source_download_count": "INTEGER NOT NULL DEFAULT 0",
            "source_view_count": "INTEGER NOT NULL DEFAULT 0",
            "source_published_at": "TEXT NOT NULL DEFAULT ''",
            "source_updated_at": "TEXT NOT NULL DEFAULT ''",
            "last_ai_at": "TEXT NOT NULL DEFAULT ''",
            "content_status": "TEXT NOT NULL DEFAULT 'pending'",
            "last_synced_source_hash": "TEXT NOT NULL DEFAULT ''",
            "published_at": "TEXT NOT NULL DEFAULT ''",
            "needs_update": "INTEGER NOT NULL DEFAULT 0",
            "product_sync_error": "TEXT NOT NULL DEFAULT ''"
            ,"hashtags_fa_json": "TEXT NOT NULL DEFAULT '[]'"
            ,"material_recommendations_json": "TEXT NOT NULL DEFAULT '[]'"
            ,"use_case_class": "TEXT NOT NULL DEFAULT ''"
            ,"ai_provider": "TEXT NOT NULL DEFAULT ''"
            ,"ai_model": "TEXT NOT NULL DEFAULT ''"
            ,"product_type": "TEXT NOT NULL DEFAULT 'ready_product'"
            ,"use_description": "TEXT NOT NULL DEFAULT ''"
            ,"dimensions": "TEXT NOT NULL DEFAULT ''"
            ,"materials_json": "TEXT NOT NULL DEFAULT '[]'"
            ,"colors_json": "TEXT NOT NULL DEFAULT '[]'"
            ,"availability_status": "TEXT NOT NULL DEFAULT 'made_to_order'"
            ,"stock_quantity": "INTEGER NOT NULL DEFAULT 0"
            ,"lead_time_min_days": "INTEGER NOT NULL DEFAULT 1"
            ,"lead_time_max_days": "INTEGER NOT NULL DEFAULT 3"
            ,"has_3d_file": "INTEGER NOT NULL DEFAULT 0"
            ,"source_name": "TEXT NOT NULL DEFAULT ''"
            ,"technical_features_json": "TEXT NOT NULL DEFAULT '{}'"
            ,"technical_summary_fa": "TEXT NOT NULL DEFAULT ''"
            ,"keywords_json": "TEXT NOT NULL DEFAULT '[]'"
            ,"is_blocked": "INTEGER NOT NULL DEFAULT 0"
            ,"blocked_at": "TEXT NOT NULL DEFAULT ''"
            ,"blocked_reason": "TEXT NOT NULL DEFAULT ''"
        }
        changed = False
        for name, ddl in additions.items():
            if name not in existing_columns:
                self.conn.execute(f"ALTER TABLE products ADD COLUMN {name} {ddl}")
                changed = True
        if changed:
            self.conn.commit()

    def upsert_source(self, row: dict):
        self.conn.execute("""
        INSERT INTO sources(
            code,name,enabled,methods_json,listing_urls_json,
            model_url_pattern,requires_login,reference_only
        ) VALUES(?,?,?,?,?,?,?,?)
        ON CONFLICT(code) DO UPDATE SET
            name=excluded.name,
            methods_json=excluded.methods_json,
            listing_urls_json=excluded.listing_urls_json,
            model_url_pattern=excluded.model_url_pattern,
            requires_login=excluded.requires_login,
            reference_only=excluded.reference_only
        """, (
            row["code"],row["name"],int(row.get("enabled",1)),
            __import__("json").dumps(row.get("methods",[])),
            __import__("json").dumps(row.get("listing_urls",[])),
            row.get("model_url_pattern",""),
            int(row.get("requires_login",False)),
            int(row.get("reference_only",False)),
        ))
        self.conn.commit()

    def sources(self):
        return list(self.conn.execute("SELECT * FROM sources ORDER BY name"))

    def source(self, code):
        return self.conn.execute("SELECT * FROM sources WHERE code=?", (code,)).fetchone()

    def update_source_runtime(self, code, **values):
        if not values: return
        sql = ", ".join(f"{k}=?" for k in values)
        self.conn.execute(f"UPDATE sources SET {sql} WHERE code=?", (*values.values(), code))
        self.conn.commit()

    def add_discovered(self, source_code, external_id, url, discovered_from=""):
        normalized = normalize_url(url)
        blocked = self.conn.execute(
            """
            SELECT id FROM products
            WHERE is_blocked=1 AND source_code=?
              AND ((external_id<>'' AND external_id=?) OR normalized_url=?)
            LIMIT 1
            """,
            (source_code, external_id or "", normalized),
        ).fetchone()
        if blocked:
            return False
        now = utc_now()
        try:
            self.conn.execute("""
            INSERT INTO discovered_urls(
                source_code,external_id,url,normalized_url,discovered_from,
                status,discovered_at,updated_at
            ) VALUES(?,?,?,?,?,'new',?,?)
            """,(source_code,external_id or "",url,normalized,discovered_from,now,now))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def pending_urls(self, source_code, limit, include_failed=False):
        statuses = ("new", "failed") if include_failed else ("new",)
        placeholders = ",".join("?" for _ in statuses)
        return list(self.conn.execute(
            f"""
            SELECT * FROM discovered_urls
            WHERE source_code=? AND status IN ({placeholders})
            ORDER BY CASE status WHEN 'new' THEN 0 ELSE 1 END, id
            LIMIT ?
            """,
            (source_code, *statuses, limit),
        ))

    def reset_failed_urls(self, source_code=""):
        if source_code:
            cursor = self.conn.execute(
                """
                UPDATE discovered_urls
                SET status='new', last_error='', updated_at=?
                WHERE source_code=? AND status IN ('failed','running')
                """,
                (utc_now(), source_code),
            )
        else:
            cursor = self.conn.execute(
                """
                UPDATE discovered_urls
                SET status='new', last_error='', updated_at=?
                WHERE status IN ('failed','running')
                """,
                (utc_now(),),
            )
        self.conn.commit()
        return cursor.rowcount

    def queue_counts(self, source_code=""):
        if source_code:
            rows = self.conn.execute(
                """
                SELECT status, COUNT(*) total
                FROM discovered_urls
                WHERE source_code=?
                GROUP BY status
                ORDER BY status
                """,
                (source_code,),
            )
        else:
            rows = self.conn.execute(
                """
                SELECT status, COUNT(*) total
                FROM discovered_urls
                GROUP BY status
                ORDER BY status
                """
            )
        return {row["status"]: int(row["total"]) for row in rows}

    def mark_url(self, row_id, status, error=""):
        self.conn.execute("""
        UPDATE discovered_urls SET status=?,attempts=attempts+1,last_error=?,updated_at=?
        WHERE id=?
        """,(status,error[:4000],utc_now(),row_id))
        self.conn.commit()

    def upsert_product(self, row: dict):
        row = dict(row)
        row["normalized_url"] = normalize_url(row["source_url"])
        blocked = self.conn.execute(
            """
            SELECT id FROM products
            WHERE is_blocked=1 AND source_code=?
              AND ((external_id<>'' AND external_id=?) OR normalized_url=?)
            LIMIT 1
            """,
            (row.get("source_code", ""), row.get("external_id", ""), row["normalized_url"]),
        ).fetchone()
        if blocked:
            return int(blocked["id"])
        row.setdefault("created_at", utc_now())
        row["updated_at"] = utc_now()
        columns = list(row)
        placeholders = ",".join("?" for _ in columns)
        update = ",".join(
            f"{c}=excluded.{c}" for c in columns
            if c not in {"source_code","external_id","created_at"}
        )
        try:
            self.conn.execute(
                f"INSERT INTO products({','.join(columns)}) VALUES({placeholders}) "
                f"ON CONFLICT(source_code,external_id) DO UPDATE SET {update}",
                [row[c] for c in columns],
            )
        except sqlite3.IntegrityError:
            existing = self.conn.execute(
                "SELECT id FROM products WHERE source_code=? AND normalized_url=?",
                (row["source_code"],row["normalized_url"]),
            ).fetchone()
            if existing:
                update_cols = [c for c in columns if c not in {"source_code","external_id","created_at"}]
                self.conn.execute(
                    f"UPDATE products SET {','.join(f'{c}=?' for c in update_cols)} WHERE id=?",
                    [row[c] for c in update_cols] + [existing["id"]],
                )
            else:
                raise
        self.conn.commit()

    def products(self, filter_name="all", source_code="", search=""):
        clauses, args = [], []
        clauses.append("is_blocked=1" if filter_name == "blocked" else "is_blocked=0")
        if source_code:
            clauses.append("source_code=?"); args.append(source_code)
        if search:
            q=f"%{search.strip()}%"
            clauses.append("(source_title LIKE ? OR title_fa LIKE ? OR external_id LIKE ? OR source_url LIKE ?)")
            args += [q,q,q,q]
        filters = {
            "untranslated":"(title_fa='' OR description_fa='')",
            "unapproved":"approved_for_sale=0",
            "not_priced":"price_is_final=0",
            "ready":"approved_for_sale=1 AND publish_as_product=1 AND title_fa<>'' AND needs_update=0",
            "portfolio":"publish_as_portfolio=1",
            "reference":"reference_only=1",
            "upload_queue":"upload_ready=1",
            "review":"workflow_status='review'",
            "work_queue":"(server_id='' OR needs_update=1 OR upload_ready=1 OR workflow_status<>'uploaded')",
            "published":"(server_id<>'' AND workflow_status='uploaded' AND needs_update=0 AND server_status IN ('created','updated','review_required'))",
            "needs_update":"needs_update=1",
            "without_images":"(images_json='[]' OR images_json='' OR images_json IS NULL)",
            "without_content":"(title_fa='' OR description_fa='' OR content_status<>'ready')",
            "error":"(server_status='failed' OR product_sync_error<>'')",
            "new":"(server_id='' AND workflow_status='review')",
            "blocked":"is_blocked=1",
        }
        if filter_name in filters:
            clauses.append(filters[filter_name])
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        order = "ORDER BY needs_update DESC, upload_ready DESC, CASE WHEN server_id='' THEN 0 ELSE 1 END, updated_at DESC, id DESC"
        return list(self.conn.execute(
            f"SELECT * FROM products{where} {order}", args
        ))

    def status_counts(self):
        row=self.conn.execute("""
        SELECT
          SUM(CASE WHEN is_blocked=0 THEN 1 ELSE 0 END) total,
          SUM(CASE WHEN is_blocked=0 AND server_id='' AND workflow_status='review' THEN 1 ELSE 0 END) new_count,
          SUM(CASE WHEN is_blocked=0 AND needs_update=1 THEN 1 ELSE 0 END) update_count,
          SUM(CASE WHEN is_blocked=0 AND (images_json='[]' OR images_json='' OR images_json IS NULL) THEN 1 ELSE 0 END) no_image_count,
          SUM(CASE WHEN is_blocked=0 AND (title_fa='' OR description_fa='' OR content_status<>'ready') THEN 1 ELSE 0 END) no_content_count,
          SUM(CASE WHEN is_blocked=0 AND upload_ready=1 THEN 1 ELSE 0 END) queue_count,
          SUM(CASE WHEN is_blocked=0 AND server_id<>'' AND workflow_status='uploaded' AND needs_update=0 THEN 1 ELSE 0 END) published_count,
          SUM(CASE WHEN is_blocked=0 AND (server_status='failed' OR product_sync_error<>'') THEN 1 ELSE 0 END) error_count,
          SUM(CASE WHEN is_blocked=1 THEN 1 ELSE 0 END) blocked_count
        FROM products
        """).fetchone()
        return {k:int(row[k] or 0) for k in row.keys()}

    def product(self, product_id):
        return self.conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()

    def update_product(self, product_id, values):
        if not values: return
        values = dict(values); values["updated_at"] = utc_now()
        self.conn.execute(
            f"UPDATE products SET {','.join(f'{k}=?' for k in values)} WHERE id=?",
            [*values.values(),product_id],
        )
        self.conn.commit()

    def exportable(self):
        return list(self.conn.execute("""
        SELECT * FROM products
        WHERE upload_ready=1
          AND is_blocked=0
          AND commercial_status IN ('allowed','owned','public_domain')
          AND (publish_as_product=1 OR publish_as_portfolio=1)
          AND (publish_as_product=0 OR approved_for_sale=1)
        ORDER BY id
        """))

    def upload_queue(self):
        return list(self.conn.execute("""
        SELECT * FROM products
        WHERE upload_ready=1
          AND is_blocked=0
        ORDER BY updated_at DESC, id DESC
        """))

    def block_product(self, product_id: int, reason: str = "") -> None:
        before = self.product(product_id)
        if before is None:
            return
        self.update_product(product_id, {
            "is_blocked": 1,
            "blocked_at": utc_now(),
            "blocked_reason": str(reason or "")[:1000],
            "source_state": "blocked",
            "workflow_status": "blocked",
            "upload_ready": 0,
            "needs_update": 0,
            "publish_as_product": 0,
            "publish_as_portfolio": 0,
        })
        self.save_history(product_id, "blocked", dict(before), dict(self.product(product_id)), reason)

    def restore_product(self, product_id: int) -> None:
        before = self.product(product_id)
        if before is None:
            return
        self.update_product(product_id, {
            "is_blocked": 0,
            "blocked_at": "",
            "blocked_reason": "",
            "source_state": "active",
            "workflow_status": "review",
            "upload_ready": 0,
        })
        self.save_history(product_id, "restored", dict(before), dict(self.product(product_id)), "Restored from blocked products")

    def set_setting(self,key,value):
        self.conn.execute("""
        INSERT INTO settings(key,value) VALUES(?,?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """,(key,value)); self.conn.commit()

    def setting(self,key,default=""):
        row=self.conn.execute("SELECT value FROM settings WHERE key=?",(key,)).fetchone()
        return row["value"] if row else default

    def close(self):
        try:
            self.conn.commit()
        finally:
            self.conn.close()

    def save_history(self, product_id, event_type, before=None, after=None, note=""):
        import json
        self.conn.execute(
            "INSERT INTO product_history(product_id,event_type,before_json,after_json,note,created_at) VALUES(?,?,?,?,?,?)",
            (int(product_id), str(event_type), json.dumps(before or {}, ensure_ascii=False, default=str),
             json.dumps(after or {}, ensure_ascii=False, default=str), str(note or "")[:4000], utc_now()),
        )
        self.conn.commit()

    def history(self, product_id, limit=50):
        return list(self.conn.execute(
            "SELECT * FROM product_history WHERE product_id=? ORDER BY id DESC LIMIT ?",
            (int(product_id), int(limit)),
        ))

    def find_duplicate(self, source_code, external_id, normalized_url, fingerprint, exclude_id=None):
        clauses=[]; args=[]
        if source_code and external_id:
            clauses.append("(source_code=? AND external_id=?)"); args += [source_code, external_id]
        if source_code and normalized_url:
            clauses.append("(source_code=? AND normalized_url=?)"); args += [source_code, normalized_url]
        if fingerprint:
            clauses.append("fingerprint=?"); args.append(fingerprint)
        if not clauses:
            return None
        sql = "SELECT * FROM products WHERE (" + " OR ".join(clauses) + ")"
        if exclude_id is not None:
            sql += " AND id<>?"; args.append(int(exclude_id))
        sql += " ORDER BY id LIMIT 1"
        return self.conn.execute(sql, args).fetchone()

    def record_sync_receipt(self, product_id, batch_uuid, status, server_id="", payload=None):
        import json
        self.conn.execute(
            "INSERT INTO sync_receipts(product_id,batch_uuid,status,server_id,payload_json,created_at) VALUES(?,?,?,?,?,?)",
            (int(product_id) if product_id else None, str(batch_uuid or ""), str(status or ""), str(server_id or ""),
             json.dumps(payload or {}, ensure_ascii=False, default=str), utc_now()),
        )
        self.conn.commit()

    def sync_receipts(self, product_id=None, limit=100):
        if product_id is None:
            return list(self.conn.execute("SELECT * FROM sync_receipts ORDER BY id DESC LIMIT ?", (int(limit),)))
        return list(self.conn.execute(
            "SELECT * FROM sync_receipts WHERE product_id=? ORDER BY id DESC LIMIT ?",
            (int(product_id), int(limit)),
        ))

    def create_run(self, source_code, mode, method, requested_limit):
        cur=self.conn.execute("""
        INSERT INTO scan_runs(source_code,mode,method,requested_limit,started_at)
        VALUES(?,?,?,?,?)
        """,(source_code,mode,method,requested_limit,utc_now()))
        self.conn.commit(); return cur.lastrowid

    def finish_run(self, run_id, **values):
        values["finished_at"]=utc_now()
        sql=",".join(f"{k}=?" for k in values)
        self.conn.execute(f"UPDATE scan_runs SET {sql} WHERE id=?",(*values.values(),run_id))
        self.conn.commit()

    def runs(self, limit=100):
        return list(self.conn.execute("SELECT * FROM scan_runs ORDER BY id DESC LIMIT ?",(limit,)))
