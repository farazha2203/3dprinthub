from __future__ import annotations

"""Registry for site-specific print catalog parsers.

Each supported external site can provide a small adapter without changing the
core importer. Adapter modules should call ``register_adapter`` with the exact
``PrintCatalogSource.code`` value used in Django admin.

Example::

    from store.catalog_adapters import BaseCatalogAdapter, register_adapter

    @register_adapter("example-models")
    class ExampleModelsAdapter(BaseCatalogAdapter):
        def parse(self, html, page_url, source):
            ...

Site modules may be placed in ``store/catalog_site_adapters/``. The importer
will try to load ``store.catalog_site_adapters.<source_code>`` automatically,
with hyphens in the source code converted to underscores.
"""

from abc import ABC, abstractmethod
import importlib
from typing import Any


class BaseCatalogAdapter(ABC):
    """Interface for a site-specific page parser."""

    @abstractmethod
    def parse(self, html: str, page_url: str, source) -> dict[str, Any]:
        """Return data using the same keys as ``parse_print_page``."""
        raise NotImplementedError


_ADAPTERS: dict[str, type[BaseCatalogAdapter] | BaseCatalogAdapter] = {}


def register_adapter(source_code: str):
    """Decorator that registers an adapter for a source code."""
    normalized = str(source_code).strip().lower()
    if not normalized:
        raise ValueError("source_code is required")

    def decorator(adapter):
        _ADAPTERS[normalized] = adapter
        return adapter

    return decorator


def _load_site_module(source_code: str) -> None:
    module_name = source_code.strip().lower().replace("-", "_")
    if not module_name:
        return
    qualified = f"store.catalog_site_adapters.{module_name}"
    try:
        importlib.import_module(qualified)
    except ModuleNotFoundError as error:
        # Ignore only a genuinely missing site module. Errors raised from an
        # import *inside* an existing adapter must surface for diagnosis.
        if error.name != qualified:
            raise


def get_adapter(source_code: str) -> BaseCatalogAdapter | None:
    normalized = str(source_code).strip().lower()
    if not normalized:
        return None
    if normalized not in _ADAPTERS:
        _load_site_module(normalized)
    adapter = _ADAPTERS.get(normalized)
    if adapter is None:
        return None
    if isinstance(adapter, type):
        return adapter()
    return adapter
