from __future__ import annotations


def variant_is_orderable(variant) -> bool:
    """Return the same customer-orderability decision across Store surfaces."""
    inventory_ok = (
        not bool(getattr(variant, "track_inventory", False))
        or bool(getattr(variant, "allow_backorder", False))
        or max(
            0,
            int(getattr(variant, "stock_quantity", 0) or 0)
            - int(getattr(variant, "reserved_quantity", 0) or 0),
        ) > 0
    )
    color_stock_ok = bool(getattr(variant, "color_stock_sufficient", True))
    return (
        str(getattr(variant, "stock_status", "") or "") != "out_of_stock"
        and inventory_ok
        and color_stock_ok
    )
