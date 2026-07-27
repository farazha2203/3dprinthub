from django.conf import settings
from django.core.checks import Warning, register


@register()
def realtime_configuration_check(app_configs, **kwargs):
    if settings.DEBUG:
        return []
    backend = settings.CHANNEL_LAYERS.get("default", {}).get("BACKEND", "")
    if backend == "channels.layers.InMemoryChannelLayer":
        return [
            Warning(
                "Realtime events use an in-memory channel layer in production; Worker events cannot cross processes.",
                hint="Configure REALTIME_REDIS_URL, for example redis://127.0.0.1:6379/1.",
                id="store.W026",
            )
        ]
    return []
