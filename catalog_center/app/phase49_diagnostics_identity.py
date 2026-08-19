from __future__ import annotations

import getpass
import os
import socket
import uuid


SESSION_ID = uuid.uuid4().hex


def _columns(db, table: str) -> set[str]:
    return {str(row["name"]) for row in db.conn.execute(f"PRAGMA table_info({table})")}


def _add_column(db, table: str, name: str, ddl: str) -> None:
    if name not in _columns(db, table):
        db.conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")


def _operator(db) -> str:
    configured = str(db.setting("operator_name", "") or "").strip()
    return (configured or os.getenv("CATALOG_OPERATOR_NAME", "").strip() or getpass.getuser() or "unknown")[:120]


def _workstation() -> str:
    return (os.getenv("COMPUTERNAME", "").strip() or socket.gethostname() or "unknown")[:160]


def _rate(db) -> float:
    try:
        return max(0.0, float(str(db.setting("ai_usd_to_toman", "") or "0").replace(",", "")))
    except Exception:
        return 0.0


def install(db) -> None:
    """Upgrade existing persistent logs without deleting historical rows."""
    for table in ("app_audit_log", "ai_request_log"):
        _add_column(db, table, "operator", "TEXT NOT NULL DEFAULT ''")
        _add_column(db, table, "workstation", "TEXT NOT NULL DEFAULT ''")
        _add_column(db, table, "session_id", "TEXT NOT NULL DEFAULT ''")

    db.conn.create_function("phase49_operator", 0, lambda: _operator(db))
    db.conn.create_function("phase49_workstation", 0, _workstation)
    db.conn.create_function("phase49_session_id", 0, lambda: SESSION_ID)
    db.conn.create_function("phase49_usd_to_toman", 0, lambda: _rate(db))

    db.conn.executescript(
        """
        CREATE TRIGGER IF NOT EXISTS trg_phase49_app_identity
        AFTER INSERT ON app_audit_log
        BEGIN
            UPDATE app_audit_log
               SET operator = phase49_operator(),
                   workstation = phase49_workstation(),
                   session_id = phase49_session_id()
             WHERE id = NEW.id;
        END;

        CREATE TRIGGER IF NOT EXISTS trg_phase49_ai_identity
        AFTER INSERT ON ai_request_log
        BEGIN
            UPDATE ai_request_log
               SET operator = phase49_operator(),
                   workstation = phase49_workstation(),
                   session_id = phase49_session_id()
             WHERE id = NEW.id;
        END;

        CREATE TRIGGER IF NOT EXISTS trg_phase49_ai_cost_toman
        AFTER INSERT ON ai_request_log
        WHEN NEW.cost_usd IS NOT NULL AND NEW.cost_irt IS NULL AND phase49_usd_to_toman() > 0
        BEGIN
            UPDATE ai_request_log
               SET cost_irt = NEW.cost_usd * phase49_usd_to_toman(),
                   cost_source = CASE
                       WHEN COALESCE(NEW.cost_source, '') = '' THEN 'usd_to_toman_rate'
                       ELSE NEW.cost_source || '+usd_to_toman_rate'
                   END
             WHERE id = NEW.id;
        END;
        """
    )

    rate = _rate(db)
    if rate > 0:
        db.conn.execute(
            """
            UPDATE ai_request_log
               SET cost_irt = cost_usd * ?,
                   cost_source = CASE
                       WHEN COALESCE(cost_source, '') = '' THEN 'usd_to_toman_rate'
                       WHEN instr(cost_source, 'usd_to_toman_rate') = 0 THEN cost_source || '+usd_to_toman_rate'
                       ELSE cost_source
                   END
             WHERE cost_usd IS NOT NULL AND cost_irt IS NULL
            """,
            (rate,),
        )
    db.conn.commit()


def session_snapshot(db) -> dict:
    return {
        "operator": _operator(db),
        "workstation": _workstation(),
        "session_id": SESSION_ID,
        "usd_to_toman": _rate(db),
    }
