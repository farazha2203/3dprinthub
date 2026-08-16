from __future__ import annotations

from urllib.parse import unquote


class UnicodeSlugConverter:
    """Resolve Store slugs reliably across Django, Apache and Passenger.

    Production WSGI stacks can expose an already-decoded Unicode segment, a
    percent-encoded segment, or UTF-8 bytes that were decoded as latin-1.  The
    database stores the real Unicode slug, so normalize all three forms before
    querying while still rejecting path separators.
    """

    regex = r"[^/]+"

    def to_python(self, value: str) -> str:
        text = unquote(str(value or ""))
        if "/" in text or "\\" in text:
            return text
        try:
            repaired = text.encode("latin-1").decode("utf-8")
            if repaired:
                text = repaired
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        return text

    def to_url(self, value: str) -> str:
        return str(value)
