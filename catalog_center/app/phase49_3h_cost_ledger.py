from __future__ import annotations

import json
import time
from typing import Any

from .ai_providers import AIProviderClient
from . import phase49_diagnostics as diagnostics

NON_BILLABLE_OPERATIONS = {
    "list_models",
    "connection_probe",
    "balance",
    "organization_costs",
    "cost_lookup",
}


def ensure_schema(db) -> None:
    diagnostics.ensure_schema(db)
    db.conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS ai_product_cost_receipts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            target TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'snapshot',
            request_from_id INTEGER NOT NULL DEFAULT 0,
            request_to_id INTEGER NOT NULL DEFAULT 0,
            summary_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS ix_ai_cost_receipt_product
            ON ai_product_cost_receipts(product_id, id DESC);
        """
    )
    db.conn.commit()


def max_request_id(db, product_id: int | None = None) -> int:
    diagnostics.ensure_schema(db)
    if product_id is None:
        row = db.conn.execute("SELECT COALESCE(MAX(id),0) AS value FROM ai_request_log").fetchone()
    else:
        row = db.conn.execute(
            "SELECT COALESCE(MAX(id),0) AS value FROM ai_request_log WHERE product_id=?",
            (int(product_id),),
        ).fetchone()
    return int((row["value"] if row is not None else 0) or 0)


def request_rows(db, product_id: int, *, after_id: int = 0, through_id: int | None = None) -> list[dict]:
    diagnostics.ensure_schema(db)
    sql = "SELECT * FROM ai_request_log WHERE product_id=? AND id>?"
    args: list[Any] = [int(product_id), int(after_id or 0)]
    if through_id is not None:
        sql += " AND id<=?"
        args.append(int(through_id))
    sql += " ORDER BY id"
    return [dict(row) for row in db.conn.execute(sql, args).fetchall()]


def is_billable_request(row: dict) -> bool:
    operation = str(row.get("operation") or "").strip().lower()
    return operation not in NON_BILLABLE_OPERATIONS


def aggregate_rows(rows: list[dict]) -> dict[str, Any]:
    known_usd = 0.0
    known_irt = 0.0
    unknown = 0
    billable = 0
    failed = 0
    prompt = completion = total = 0
    request_ids = []
    providers = set()
    models = set()
    for row in rows:
        providers.add(str(row.get("provider") or "").strip())
        models.add(str(row.get("model") or "").strip())
        rid = str(row.get("request_id") or "").strip()
        if rid:
            request_ids.append(rid)
        prompt += int(row.get("prompt_tokens") or 0)
        completion += int(row.get("completion_tokens") or 0)
        total += int(row.get("total_tokens") or 0)
        if str(row.get("status") or "").lower() != "ok":
            failed += 1
        if not is_billable_request(row):
            continue
        billable += 1
        usd = row.get("cost_usd")
        irt = row.get("cost_irt")
        if usd is not None:
            known_usd += float(usd)
        if irt is not None:
            known_irt += float(irt)
        if usd is None and irt is None and str(row.get("status") or "").lower() == "ok":
            unknown += 1
    return {
        "request_count": len(rows),
        "billable_request_count": billable,
        "failed_request_count": failed,
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": total,
        "known_cost_usd": round(known_usd, 8),
        "known_cost_irt": round(known_irt, 2),
        "unknown_cost_request_count": unknown,
        "providers": sorted(x for x in providers if x),
        "models": sorted(x for x in models if x),
        "request_ids": request_ids,
        "cost_contract": "Only provider-reported or verified lookup costs are counted; unknown cost is never fabricated.",
    }


def aggregate_product(db, product_id: int, *, after_id: int = 0, through_id: int | None = None) -> dict[str, Any]:
    return aggregate_rows(request_rows(db, product_id, after_id=after_id, through_id=through_id))


def _number(value):
    try:
        return float(value)
    except Exception:
        return None


def extract_verified_avalai_cost(transaction: dict) -> dict[str, float | str]:
    """Read only explicitly currency-labelled values; never infer a generic amount."""
    if not isinstance(transaction, dict):
        return {}
    for key in ("cost_irt", "amount_irt", "irt_amount", "price_irt"):
        value = _number(transaction.get(key))
        if value is not None:
            return {"cost_irt": abs(value), "cost_source": f"avalai_lookup:{key}"}
    for key in ("cost_usd", "amount_usd", "usd_amount", "price_usd"):
        value = _number(transaction.get(key))
        if value is not None:
            return {"cost_usd": abs(value), "cost_source": f"avalai_lookup:{key}"}
    amount = transaction.get("amount")
    if isinstance(amount, dict):
        value = _number(amount.get("value"))
        currency = str(amount.get("currency") or amount.get("unit") or "").strip().upper()
        if value is not None and currency in {"IRT", "TOMAN", "TOMANS"}:
            return {"cost_irt": abs(value), "cost_source": "avalai_lookup:amount_irt"}
        if value is not None and currency == "USD":
            return {"cost_usd": abs(value), "cost_source": "avalai_lookup:amount_usd"}
    return {}


def _update_row_cost(db, row_id: int, values: dict) -> None:
    if not values:
        return
    cost_usd = values.get("cost_usd")
    cost_irt = values.get("cost_irt")
    source = str(values.get("cost_source") or "")[:120]
    db.conn.execute(
        """
        UPDATE ai_request_log
           SET cost_usd=COALESCE(?,cost_usd),
               cost_irt=COALESCE(?,cost_irt),
               cost_source=CASE WHEN ?<>'' THEN ? ELSE cost_source END
         WHERE id=?
        """,
        (cost_usd, cost_irt, source, source, int(row_id)),
    )
    db.conn.commit()


def resolve_avalai_costs(db, product_id: int, api_key: str, model: str = "", *, after_id: int = 0) -> int:
    if not str(api_key or "").strip():
        return 0
    changed = 0
    client = AIProviderClient("avalai", api_key, model, product_id=int(product_id))
    for row in request_rows(db, product_id, after_id=after_id):
        if str(row.get("provider") or "").lower() != "avalai":
            continue
        if not is_billable_request(row) or str(row.get("status") or "").lower() != "ok":
            continue
        if row.get("cost_usd") is not None or row.get("cost_irt") is not None:
            continue
        request_id = str(row.get("request_id") or "").strip()
        if not request_id:
            continue
        try:
            transaction = client.lookup_avalai_cost(request_id)
            values = extract_verified_avalai_cost(transaction)
        except Exception:
            values = {}
        if values:
            _update_row_cost(db, int(row["id"]), values)
            changed += 1
    return changed


def freeze_receipt(db, product_id: int, target: str, *, status: str = "publish_requested") -> dict[str, Any]:
    ensure_schema(db)
    end_id = max_request_id(db, product_id)
    summary = aggregate_product(db, product_id, through_id=end_id)
    created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    cursor = db.conn.execute(
        """
        INSERT INTO ai_product_cost_receipts(
            product_id,target,status,request_from_id,request_to_id,summary_json,created_at
        ) VALUES(?,?,?,?,?,?,?)
        """,
        (
            int(product_id), str(target or "")[:80], str(status or "snapshot")[:80],
            0, end_id, json.dumps(summary, ensure_ascii=False, default=str), created_at,
        ),
    )
    db.conn.commit()
    receipt = {
        "receipt_id": int(cursor.lastrowid),
        "product_id": int(product_id),
        "target": str(target or ""),
        "status": str(status or "snapshot"),
        "request_to_id": end_id,
        "created_at": created_at,
        "summary": summary,
    }
    return receipt


def latest_receipt(db, product_id: int) -> dict[str, Any] | None:
    ensure_schema(db)
    row = db.conn.execute(
        "SELECT * FROM ai_product_cost_receipts WHERE product_id=? ORDER BY id DESC LIMIT 1",
        (int(product_id),),
    ).fetchone()
    if row is None:
        return None
    result = dict(row)
    try:
        result["summary"] = json.loads(result.pop("summary_json") or "{}")
    except Exception:
        result["summary"] = {}
    return result


def format_cost_summary(summary: dict[str, Any]) -> str:
    usd = float(summary.get("known_cost_usd") or 0)
    irt = float(summary.get("known_cost_irt") or 0)
    unknown = int(summary.get("unknown_cost_request_count") or 0)
    tokens = int(summary.get("total_tokens") or 0)
    requests = int(summary.get("billable_request_count") or 0)
    pieces = [f"{requests:,} درخواست AI", f"{tokens:,} توکن"]
    if irt:
        pieces.append(f"{irt:,.0f} تومان هزینه ثبت‌شده")
    if usd:
        pieces.append(f"${usd:,.6f} هزینه ثبت‌شده")
    if unknown:
        pieces.append(f"{unknown:,} درخواست با هزینه نامشخص")
    if not usd and not irt and not unknown:
        pieces.append("هزینه ثبت‌شده: صفر/بدون درخواست billable")
    return " • ".join(pieces)
