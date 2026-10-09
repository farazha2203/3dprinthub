"""Stable, conservative site-revision matching for Instagram receipt safety.

A new rendering/diagnostics key in the Site ACK should never by itself
trigger a duplicate post. Missing IDs or revisions cannot establish parity.
"""
from __future__ import annotations

import json


def same_site_revision(prior_ack: str, current_ack: str) -> bool:
    prior = str(prior_ack or "").strip()
    current = str(current_ack or "").strip()
    if not prior or not current:
        return False
    if prior == current:
        return True
    try:
        previous = json.loads(prior)
        present = json.loads(current)
    except (TypeError, ValueError):
        return False
    if not isinstance(previous, dict) or not isinstance(present, dict):
        return False

    def identity(ack: dict):
        try:
            product = int(ack.get("product_id") or ack.get("server_product_id") or 0)
            revision = int(ack.get("product_revision") or 0)
        except (TypeError, ValueError):
            return None
        return (product, revision) if product > 0 and revision > 0 else None

    old = identity(previous)
    new = identity(present)
    return bool(old and new and old[0] > 0 and old[1] > 0 and old == new)
