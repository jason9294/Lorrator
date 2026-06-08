from logging.config import dictConfig


def setup_logging(level: str = "INFO"):
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                # "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "format": "%(levelname)-8s | [%(name)s] %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": level,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
        },
        "loggers": {
            "app": {
                "level": level,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],  # 指向你定義的 handler
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console"],  # 指向你定義的 handler
                "propagate": False,
            },
        },
    }
    dictConfig(config)
