from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class PrivateModelStorage(FileSystemStorage):
    """Storage with no public URL. Downloads must pass through a staff-only view."""

    def __init__(self, *args, **kwargs):
        location = kwargs.pop(
            "location",
            getattr(settings, "PRIVATE_MEDIA_ROOT", Path(settings.BASE_DIR) / "private_media"),
        )
        super().__init__(location=location, base_url=None, *args, **kwargs)

    def url(self, name):
        raise ValueError("Private model files do not have a public URL.")


private_model_storage = PrivateModelStorage()
