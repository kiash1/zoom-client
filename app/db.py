import os

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from decouple import config

TORTOISE_ORM = {
    "connections": {"default": config("DATABASE_URL", cast=str, default="mysql://root:rootroot@127.0.0.1:3306/dmedzoom")},
    "apps": {
        "models": {
            "models": ["app.models.tortoise.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


def init_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        db_url=config("DATABASE_URL", cast=str, default="mysql://root:rootroot@127.0.0.1:3306/dmedzoom"),
        modules={"models": ["app.models.tortoise.models"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )

def init_db_app_launch(app: FastAPI) -> None:
    register_tortoise(
        app,
        db_url=config("DATABASE_URL", cast=str, default="mysql://root:rootroot@127.0.0.1:3306/dmedzoom"),
        modules={"models": ["app.models.tortoise.models"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )