from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / "config" / "settings.py"

BLOCK = '''# BEGIN PHASE 26 REALTIME CHANNELS
# Keep Django's normal runserver and template/static resolution unchanged.
# Production ASGI is started explicitly with RUN_PHASE26_ASGI.ps1 or systemd.
if "channels" not in INSTALLED_APPS:
    INSTALLED_APPS.append("channels")

ASGI_APPLICATION = "config.asgi.application"
REALTIME_REDIS_URL = os.getenv("REALTIME_REDIS_URL", "").strip()
REALTIME_POLL_FALLBACK_SECONDS = max(int(os.getenv("REALTIME_POLL_FALLBACK_SECONDS", "5")), 2)
if REALTIME_REDIS_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REALTIME_REDIS_URL],
                "prefix": "3dprinthub",
                "capacity": 1000,
                "expiry": 60,
                "group_expiry": 86400,
            },
        }
    }
else:
    # Local fallback. Cross-process Worker events require Redis in production.
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
    }
# END PHASE 26 REALTIME CHANNELS'''


def main() -> None:
    source = SETTINGS.read_text(encoding="utf-8")
    pattern = re.compile(
        r"# BEGIN PHASE 26 REALTIME CHANNELS.*?# END PHASE 26 REALTIME CHANNELS",
        re.DOTALL,
    )
    updated, count = pattern.subn(BLOCK, source, count=1)
    if count != 1:
        raise RuntimeError("Phase 26 realtime settings block was not found exactly once.")
    compile(updated, str(SETTINGS), "exec")
    if updated != source:
        SETTINGS.write_text(updated, encoding="utf-8", newline="\n")
        print("Updated Phase 26 realtime settings without replacing other settings.")
    else:
        print("Phase 26 realtime settings were already safe.")


if __name__ == "__main__":
    main()
