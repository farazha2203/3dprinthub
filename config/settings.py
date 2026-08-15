from pathlib import Path
import os

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DEBUG = os.getenv("DJANGO_DEBUG", "0").strip().lower() in {"1", "true", "yes", "on"}
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "unsafe-development-key-change-me"
    else:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY must be configured in the environment.")


def csv_env(name, default=""):
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


ALLOWED_HOSTS = csv_env(
    "DJANGO_ALLOWED_HOSTS",
    "3dprinthub.ir,www.3dprinthub.ir,127.0.0.1,localhost",
)
CSRF_TRUSTED_ORIGINS = csv_env(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "https://3dprinthub.ir,https://www.3dprinthub.ir",
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "website.apps.WebsiteConfig",
    "store.apps.StoreConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "website.middleware.AdminAccessGuardMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "website.context_processors.customer_ui",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DB_NAME = os.getenv("DB_NAME", "").strip()
if DB_NAME:
    DATABASES = {
        "default": {
            "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.mysql"),
            "NAME": DB_NAME,
            "USER": os.getenv("DB_USER", ""),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": (
                    "SET SESSION default_storage_engine='InnoDB', "
                    "SESSION sql_mode='STRICT_TRANS_TABLES'"
                ),
            },
            "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = Path(os.getenv("STATIC_ROOT", "/home/sfkilvrs/public_html/static"))
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", "/home/sfkilvrs/public_html/media"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/customer/login/"
LOGIN_REDIRECT_URL = "/customer/dashboard/"
LOGOUT_REDIRECT_URL = "/"

if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    X_FRAME_OPTIONS = "DENY"

USE_X_FORWARDED_PROTO = os.getenv("USE_X_FORWARDED_PROTO", "0").lower() in {"1", "true", "yes", "on"}
if USE_X_FORWARDED_PROTO:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# BEGIN PHASE 4 SECURITY SETTINGS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "1").lower() in {"1","true","yes","on"}
# END PHASE 4 SECURITY SETTINGS

# BEGIN AFFILIATE PARTNER PROGRAM PHASE 7 SETTINGS
AFFILIATE_COOKIE_NAME = "dph_ref"
if "store.middleware.AffiliateAttributionMiddleware" not in MIDDLEWARE:
    try:
        _affiliate_middleware_index = MIDDLEWARE.index("django.contrib.auth.middleware.AuthenticationMiddleware") + 1
    except ValueError:
        _affiliate_middleware_index = len(MIDDLEWARE)
    MIDDLEWARE.insert(_affiliate_middleware_index, "store.middleware.AffiliateAttributionMiddleware")
_affiliate_context_processor = "store.context_processors.affiliate_ui"
for _template_engine in TEMPLATES:
    _processors = _template_engine.setdefault("OPTIONS", {}).setdefault("context_processors", [])
    if _affiliate_context_processor not in _processors:
        _processors.append(_affiliate_context_processor)
# END AFFILIATE PARTNER PROGRAM PHASE 7 SETTINGS

# BEGIN PHASE 10 PRIVATE MEDIA SETTINGS
# فایل‌های سه‌بعدی مشتری خارج از MEDIA عمومی ذخیره می‌شوند.
PRIVATE_MEDIA_ROOT = Path(os.getenv("PRIVATE_MEDIA_ROOT", str(BASE_DIR / "private_media")))
# END PHASE 10 PRIVATE MEDIA SETTINGS

# BEGIN PHASE19C SMARTBASE ADMIN

_SMARTBASE_REQUIRED_APPS = [
    "easy_thumbnails",
    "polymorphic",
    "filer",
    "widget_tweaks",
    "ckeditor",
    "ckeditor_uploader",
    "nested_admin",
    "django_htmx",
    "django.contrib.postgres",
    "django_smartbase_admin",
    "django_smartbase_admin.audit",
    "django_smartbase_admin.messaging",
    "smartbase_admin_bridge.apps.SmartBaseAdminBridgeConfig",
]

_SMARTBASE_LEGACY_APPS = {
    "admin_console",
    "admin_console.apps.AdminConsoleConfig",
}

INSTALLED_APPS = [
    app
    for app in list(INSTALLED_APPS)
    if app not in _SMARTBASE_LEGACY_APPS
    and app not in _SMARTBASE_REQUIRED_APPS
]
INSTALLED_APPS.extend(_SMARTBASE_REQUIRED_APPS)

_SMARTBASE_LOCALE_MIDDLEWARE = "django.middleware.locale.LocaleMiddleware"
MIDDLEWARE = [
    item
    for item in list(MIDDLEWARE)
    if item != _SMARTBASE_LOCALE_MIDDLEWARE
]
try:
    _smartbase_session_index = MIDDLEWARE.index(
        "django.contrib.sessions.middleware.SessionMiddleware"
    )
except ValueError:
    _smartbase_session_index = 0
MIDDLEWARE.insert(
    _smartbase_session_index + 1,
    _SMARTBASE_LOCALE_MIDDLEWARE,
)

for _template_backend in TEMPLATES:
    _template_dirs = _template_backend.setdefault("DIRS", [])
    _project_template_dir = BASE_DIR / "templates"
    if _project_template_dir not in _template_dirs:
        _template_dirs.insert(0, _project_template_dir)

SB_ADMIN_CONFIGURATION = "config.sbadmin_config.SBAdminConfiguration"
PROJECT_NAME = "3DPrintHub"
CKEDITOR_UPLOAD_PATH = "uploads/ckeditor/"
SB_ADMIN_MESSAGING_ATTACHMENT_UPLOAD_TO = "messaging/attachments/"
FILER_ENABLE_PERMISSIONS = True

THUMBNAIL_ALIASES = {
    **globals().get("THUMBNAIL_ALIASES", {}),
    "": {
        **globals().get("THUMBNAIL_ALIASES", {}).get("", {}),
        "smartbase_admin_preview": {
            "size": (240, 240),
            "crop": True,
            "upscale": False,
        },
    },
}

# END PHASE19C SMARTBASE ADMIN


# BEGIN PHASE 19 GOOGLE AUTHENTICATION
SITE_ID = int(os.getenv("DJANGO_SITE_ID", "1"))
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = os.getenv("ACCOUNT_EMAIL_VERIFICATION", "none")
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = False
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "").strip()
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "").strip()
GOOGLE_OAUTH_ENABLED = bool(GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET)
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "OAUTH_PKCE_ENABLED": True,
        "FETCH_USERINFO": True,
        "EMAIL_AUTHENTICATION": True,
    }
}
if GOOGLE_OAUTH_ENABLED:
    SOCIALACCOUNT_PROVIDERS["google"]["APPS"] = [{
        "client_id": GOOGLE_OAUTH_CLIENT_ID,
        "secret": GOOGLE_OAUTH_CLIENT_SECRET,
        "key": "",
    }]
# END PHASE 19 GOOGLE AUTHENTICATION

# BEGIN PHASE 22 TRANSACTIONAL EMAIL / PASSWORD RECOVERY
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
    if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "1").lower() in {"1", "true", "yes", "on"}
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "0").lower() in {"1", "true", "yes", "on"}
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "3DPrintHub <no-reply@3dprinthub.ir>")
SERVER_EMAIL = os.getenv("SERVER_EMAIL", DEFAULT_FROM_EMAIL)
PASSWORD_RESET_TIMEOUT = int(os.getenv("PASSWORD_RESET_TIMEOUT", "3600"))
# END PHASE 22 TRANSACTIONAL EMAIL / PASSWORD RECOVERY

# BEGIN PHASE 25 LINK WORKER MONITORING
LINK_WORKER_HEALTH_TOKEN = os.getenv("LINK_WORKER_HEALTH_TOKEN", "").strip()
# END PHASE 25 LINK WORKER MONITORING

# BEGIN PHASE 26 REALTIME CHANNELS
# Keep Django's normal runserver and template/static resolution unchanged.
# Production ASGI is started explicitly with RUN_PHASE26_ASGI.ps1 or systemd.
if "channels" not in INSTALLED_APPS:
    INSTALLED_APPS.append("channels")

ASGI_APPLICATION = "config.asgi.application"
REALTIME_REDIS_URL = os.getenv("REALTIME_REDIS_URL", "").strip()
REALTIME_POLL_FALLBACK_SECONDS = max(int(os.getenv("REALTIME_POLL_FALLBACK_SECONDS", "5")), 2)
REALTIME_ALLOW_POLLING_ONLY = os.getenv("REALTIME_ALLOW_POLLING_ONLY", "0").lower() in {"1", "true", "yes", "on"}
REALTIME_REDIS_AUTO_FALLBACK = os.getenv(
    "REALTIME_REDIS_AUTO_FALLBACK",
    "1" if (DEBUG or REALTIME_ALLOW_POLLING_ONLY) else "0",
).lower() in {"1", "true", "yes", "on"}


def _realtime_redis_reachable(url: str) -> bool:
    if not url:
        return False
    if not REALTIME_REDIS_AUTO_FALLBACK:
        return True
    try:
        import socket
        from urllib.parse import urlsplit
        parsed = urlsplit(url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 6379
        with socket.create_connection((host, port), timeout=0.25):
            return True
    except OSError:
        return False


_REALTIME_USE_REDIS = bool(REALTIME_REDIS_URL and _realtime_redis_reachable(REALTIME_REDIS_URL))
if _REALTIME_USE_REDIS:
    REALTIME_BACKEND_MODE = "redis"
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
    # Local development and explicitly configured shared hosting use HTTP polling.
    # In-memory channels are process-local; polling and the database remain the source of truth.
    REALTIME_BACKEND_MODE = "polling" if REALTIME_ALLOW_POLLING_ONLY else "memory"
    CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
# END PHASE 26 REALTIME CHANNELS

# BEGIN PHASE 30 ONLINE PAYMENT GATEWAY
PAYMENT_GATEWAY_ENABLED = os.getenv("PAYMENT_GATEWAY_ENABLED", "0").lower() in {"1", "true", "yes", "on"}
PAYMENT_GATEWAY_PROVIDER = os.getenv("PAYMENT_GATEWAY_PROVIDER", "zarinpal").strip().lower()
PAYMENT_GATEWAY_HTTP_TIMEOUT = max(int(os.getenv("PAYMENT_GATEWAY_HTTP_TIMEOUT", "15")), 3)
PAYMENT_GATEWAY_PENDING_TTL_MINUTES = max(int(os.getenv("PAYMENT_GATEWAY_PENDING_TTL_MINUTES", "30")), 5)
PAYMENT_GATEWAY_VERIFY_LOCK_SECONDS = max(int(os.getenv("PAYMENT_GATEWAY_VERIFY_LOCK_SECONDS", "60")), 15)
PAYMENT_GATEWAY_DESCRIPTION_PREFIX = os.getenv("PAYMENT_GATEWAY_DESCRIPTION_PREFIX", "3DPrintHub").strip() or "3DPrintHub"

ZARINPAL_MERCHANT_ID = os.getenv("ZARINPAL_MERCHANT_ID", "").strip()
ZARINPAL_ACCESS_TOKEN = os.getenv("ZARINPAL_ACCESS_TOKEN", "").strip()
ZARINPAL_SANDBOX = os.getenv("ZARINPAL_SANDBOX", "1" if DEBUG else "0").lower() in {"1", "true", "yes", "on"}
ZARINPAL_CURRENCY = os.getenv("ZARINPAL_CURRENCY", "IRT").strip().upper()
ZARINPAL_REQUEST_URL = os.getenv("ZARINPAL_REQUEST_URL", "https://api.zarinpal.com/pg/v4/payment/request.json").strip()
ZARINPAL_VERIFY_URL = os.getenv("ZARINPAL_VERIFY_URL", "https://api.zarinpal.com/pg/v4/payment/verify.json").strip()
ZARINPAL_START_URL = os.getenv("ZARINPAL_START_URL", "https://www.zarinpal.com/pg/StartPay/").strip()
ZARINPAL_SANDBOX_REQUEST_URL = os.getenv("ZARINPAL_SANDBOX_REQUEST_URL", "https://sandbox.zarinpal.com/pg/v4/payment/request.json").strip()
ZARINPAL_SANDBOX_VERIFY_URL = os.getenv("ZARINPAL_SANDBOX_VERIFY_URL", "https://sandbox.zarinpal.com/pg/v4/payment/verify.json").strip()
ZARINPAL_SANDBOX_START_URL = os.getenv("ZARINPAL_SANDBOX_START_URL", "https://sandbox.zarinpal.com/pg/StartPay/").strip()
# END PHASE 30 ONLINE PAYMENT GATEWAY

# BEGIN PHASE 48 CATALOG PUBLISHING BRIDGE
CATALOG_BRIDGE_TOKEN = os.getenv("CATALOG_BRIDGE_TOKEN", "").strip()
CATALOG_BRIDGE_PENDING_ROOT = Path(
    os.getenv(
        "CATALOG_BRIDGE_PENDING_ROOT",
        str(BASE_DIR / "imports" / "desktop_catalog" / "pending"),
    )
)
if "catalog_bridge.apps.CatalogBridgeConfig" not in INSTALLED_APPS:
    INSTALLED_APPS.append("catalog_bridge.apps.CatalogBridgeConfig")
# END PHASE 48 CATALOG PUBLISHING BRIDGE
