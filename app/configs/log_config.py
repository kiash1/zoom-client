from pydantic import BaseModel

class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "zoom-client"
    LOG_FORMAT: str = "[%(levelprefix)s %(asctime)s] [%(filename)s: %(name)s: %(lineno)s - %(funcName)20s()] %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        "zoom-client": {"handlers": ["default"], "level": LOG_LEVEL},
        "": {
            "handlers": ["default"],
            "level": LOG_LEVEL,
        },
    }