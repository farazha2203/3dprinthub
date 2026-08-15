from __future__ import annotations

import hmac
import io
import json
import os
import re
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST


VERSION = "1.0.0"
BATCH_NAME = re.compile(r"^desktop_catalog_v85_[0-9]{8}_[0-9]{6}$")
ACK_MARKER = "CATALOG_ACK_JSON="


def _configured_token() -> str:
    return str(getattr(settings, "CATALOG_BRIDGE_TOKEN", "") or os.getenv("CATALOG_BRIDGE_TOKEN", "")).strip()


def _authorized(request) -> bool:
    configured = _configured_token()
    header = request.headers.get("Authorization", "")
    supplied = header[7:].strip() if header.startswith("Bearer ") else ""
    return bool(len(configured) >= 24 and supplied and hmac.compare_digest(configured, supplied))


def _unauthorized():
    response = JsonResponse({"status": "unauthorized", "detail": "A valid bearer token is required."}, status=401)
    response["WWW-Authenticate"] = "Bearer"
    return response


def _pending_root() -> Path:
    configured = getattr(settings, "CATALOG_BRIDGE_PENDING_ROOT", None)
    return Path(configured or (Path(settings.BASE_DIR) / "imports" / "desktop_catalog" / "pending")).resolve()


def _ack_from_output(output: str):
    for line in reversed((output or "").splitlines()):
        if line.startswith(ACK_MARKER):
            try:
                value = json.loads(line[len(ACK_MARKER):])
                return value if isinstance(value, dict) else None
            except Exception:
                return None
    return None


@require_GET
def health_view(request):
    if not _authorized(request):
        return _unauthorized()
    return JsonResponse({
        "status": "ok",
        "version": VERSION,
        "schema_version": "8.5",
        "pending_root_ready": _pending_root().is_dir(),
    })


@csrf_exempt
@require_POST
def import_view(request):
    if not _authorized(request):
        return _unauthorized()
    if int(request.headers.get("Content-Length") or 0) > 16_384:
        return JsonResponse({"status": "invalid_request", "detail": "Request body is too large."}, status=413)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"status": "invalid_request", "detail": "A valid JSON body is required."}, status=400)

    batch_name = str(payload.get("batch_name") or "").strip()
    requested_uuid = str(payload.get("batch_uuid") or "").strip()
    if not BATCH_NAME.fullmatch(batch_name):
        return JsonResponse({"status": "invalid_batch", "detail": "Batch name is invalid."}, status=400)
    if str(payload.get("schema_version") or "") != "8.5":
        return JsonResponse({"status": "invalid_schema", "detail": "Schema 8.5 is required."}, status=400)

    pending_root = _pending_root()
    batch_root = (pending_root / batch_name).resolve()
    try:
        batch_root.relative_to(pending_root)
    except ValueError:
        return JsonResponse({"status": "invalid_batch", "detail": "Batch path escapes the pending root."}, status=400)
    manifest_path = batch_root / "batch_manifest.json"
    if not manifest_path.is_file():
        return JsonResponse({"status": "not_found", "detail": "Uploaded batch manifest was not found."}, status=404)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return JsonResponse({"status": "invalid_batch", "detail": "Batch manifest is invalid JSON."}, status=400)
    if str(manifest.get("schema_version") or "") != "8.5":
        return JsonResponse({"status": "invalid_schema", "detail": "Uploaded batch is not schema 8.5."}, status=400)
    if not requested_uuid or not hmac.compare_digest(str(manifest.get("batch_uuid") or ""), requested_uuid):
        return JsonResponse({"status": "uuid_mismatch", "detail": "Batch UUID does not match the manifest."}, status=409)

    ack_path = batch_root / ".phase43-ack.json"
    if ack_path.is_file():
        try:
            cached = json.loads(ack_path.read_text(encoding="utf-8"))
            cached["bridge_status"] = "cached"
            return JsonResponse(cached)
        except Exception:
            pass

    lock_path = batch_root / ".phase43-import.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(descriptor)
    except FileExistsError:
        return JsonResponse({"status": "busy", "detail": "This batch is already being imported."}, status=409)

    stdout = io.StringIO()
    stderr = io.StringIO()
    command_error = ""
    try:
        try:
            call_command("phase37_import_catalog_center", str(batch_root), continue_on_error=True, stdout=stdout, stderr=stderr)
        except CommandError as exc:
            command_error = str(exc)
        ack = _ack_from_output(stdout.getvalue())
        if ack is None:
            return JsonResponse({
                "status": "import_failed",
                "detail": command_error or "Importer did not return a structured ACK.",
                "stderr_tail": stderr.getvalue()[-3000:],
            }, status=500)
        ack["bridge_status"] = "completed" if not ack.get("failed_count") else "completed_with_errors"
        if command_error:
            ack["command_error"] = command_error[:1000]
        if not ack.get("failed_count"):
            ack_path.write_text(json.dumps(ack, ensure_ascii=False, indent=2), encoding="utf-8")
        return JsonResponse(ack)
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
