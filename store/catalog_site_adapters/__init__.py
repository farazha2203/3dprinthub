from __future__ import annotations

from .grabcad import GrabCADAdapter
from .makerworld import MakerWorldAdapter
from .printables import PrintablesAdapter
from .thingiverse import ThingiverseAdapter


ADAPTERS = {
    "makerworld": MakerWorldAdapter,
    "printables": PrintablesAdapter,
    "thingiverse": ThingiverseAdapter,
    "grabcad": GrabCADAdapter,
}


def get_source_adapter(source, policy):
    adapter_class = ADAPTERS.get(policy.source_kind)
    if adapter_class is None:
        raise ValueError(f"برای منبع {policy.source_kind!r} Adapter اختصاصی ثبت نشده است.")
    return adapter_class(source, policy)
