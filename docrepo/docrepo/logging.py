# Logging
# See:
#   https://betterstack.com/community/guides/logging/how-to-start-logging-with-django/#step-5-using-logging-extensions
#

LOG_FILE = "logs/server.log"
DJANGO_LOG_FILE = "logs/django.log"
LOG_LEVEL = "DEBUG"
DJANGO_LOG_LEVEL = "INFO"

LOGGING_FORMAT = (
    "%(asctime)s [%(levelname)s]"
    + " [%(name)s.%(funcName)s]:%(lineno)s"
    + " %(message)s"
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {"format": LOGGING_FORMAT},
        "console": {"format": LOGGING_FORMAT},
    },
    "handlers": {
        "default": {
            "level": LOG_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE,
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "standard",
        },
        "request_handler": {
            "level": DJANGO_LOG_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": DJANGO_LOG_FILE,
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "standard",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "loggers": {
        "root": {
            "handlers": ["console", "default", "request_handler"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django.request": {  # Stop SQL debug from logging to main logger
            "handlers": ["request_handler"],
            "level": DJANGO_LOG_LEVEL,
            "propagate": False,
        },
    },
}
