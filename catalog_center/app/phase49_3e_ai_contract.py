from __future__ import annotations

import json


def _row_value(row, key: str, default=""):
    if row is None:
        return default
    if isinstance(row, dict):
        value = row.get(key, default)
    else:
        try:
            value = row[key]
        except Exception:
            value = default
    return default if value is None else value


def _json_list(value) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def _valid_material_recommendations(value) -> bool:
    items = _json_list(value)
    if not items:
        return False
    for item in items:
        if not isinstance(item, dict):
            return False
        if not str(item.get("material") or "").strip():
            return False
        if not str(item.get("reason_fa") or "").strip():
            return False
        try:
            score = int(item.get("score") or 0)
        except Exception:
            return False
        if score < 0 or score > 100:
            return False
    return True


def install(task_center_module) -> None:
    if getattr(task_center_module, "_phase49_3e_contract_installed", False):
        return

    original_updates = task_center_module.build_ai_updates
    original_tasks = task_center_module.evaluate_ai_tasks

    def build_ai_updates(row, pack: dict, *, scope: str = "all") -> dict:
        updates = dict(original_updates(row, pack, scope=scope))
        image_scope = str(scope or "all") == "images"
        if not image_scope:
            if not _json_list(_row_value(row, "specs_fa_json", "[]")):
                specs = pack.get("specs_fa")
                if isinstance(specs, list) and specs and all(isinstance(item, dict) for item in specs):
                    clean_specs = []
                    for item in specs:
                        key = str(item.get("key") or "").strip()
                        value = str(item.get("value") or "").strip()
                        if key and value:
                            clean_specs.append({"key": key, "value": value})
                    if clean_specs:
                        updates["specs_fa_json"] = json.dumps(clean_specs, ensure_ascii=False)

            if not _valid_material_recommendations(_row_value(row, "material_recommendations_json", "[]")):
                recs = pack.get("material_recommendations")
                if isinstance(recs, list):
                    clean_recs = []
                    for item in recs:
                        if not isinstance(item, dict):
                            continue
                        material = str(item.get("material") or "").strip()
                        reason = str(item.get("reason_fa") or "").strip()
                        if not material or not reason:
                            continue
                        try:
                            score = max(0, min(100, int(item.get("score") or 0)))
                        except Exception:
                            score = 0
                        clean_recs.append({
                            "material": material,
                            "score": score,
                            "recommended": bool(item.get("recommended")),
                            "reason_fa": reason,
                        })
                    if clean_recs:
                        updates["material_recommendations_json"] = json.dumps(clean_recs, ensure_ascii=False)
        return updates

    def evaluate_ai_tasks(row):
        tasks = original_tasks(row)
        valid = _valid_material_recommendations(_row_value(row, "material_recommendations_json", "[]"))
        for task in tasks:
            if task.get("key") == "materials":
                task["status"] = "done" if valid else "missing"
                task["missing"] = [] if valid else ["پیشنهاد متریال AI معتبر"]
        return tasks

    task_center_module.build_ai_updates = build_ai_updates
    task_center_module.evaluate_ai_tasks = evaluate_ai_tasks
    task_center_module._phase49_3e_contract_installed = True
