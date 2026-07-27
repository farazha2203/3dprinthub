from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .common import CatalogCandidate, CatalogHTTPClient, allowed_domain


class MultiSourceCatalogAdapter(ABC):
    key = "base"
    allowed_domains: tuple[str, ...] = ()

    def __init__(self, source, policy) -> None:
        self.source = source
        self.policy = policy
        self.client = CatalogHTTPClient(
            headers=source.request_headers or {},
            timeout=source.request_timeout_seconds or 20,
            delay_ms=policy.request_delay_ms,
        )

    @abstractmethod
    def discover(self, *, limit: int, sort_mode: str) -> list[CatalogCandidate]:
        raise NotImplementedError

    @abstractmethod
    def fetch_record(self, candidate: CatalogCandidate, *, hydrate_files: bool = False) -> dict[str, Any]:
        raise NotImplementedError

    def source_domains(self) -> list[str]:
        from urllib.parse import urlparse

        configured = [part.strip() for part in (self.source.allowed_domains or "").split(",") if part.strip()]
        if configured:
            return configured
        hostname = urlparse(self.source.base_url).hostname or ""
        return [hostname] if hostname else []

    def assert_url_allowed(self, url: str) -> None:
        if not allowed_domain(url, self.source_domains()):
            raise ValueError("دامنه درخواست خارج از دامنه‌های مجاز منبع است.")

    def env_token(self) -> str:
        import os

        key = (self.policy.api_token_env or "").strip()
        return os.environ.get(key, "").strip() if key else ""
