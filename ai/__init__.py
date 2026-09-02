"""Shared AI policy and project adapters.

This package is intentionally import-safe: importing it performs no network
request and never reads or persists API keys into the database.
"""

from .model_policy import RuntimeSelection, resolve_product_model, runtime_config_status

__all__ = [
    "RuntimeSelection",
    "resolve_product_model",
    "runtime_config_status",
]
