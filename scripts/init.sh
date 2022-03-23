#!/bin/sh

aerich init -t app.db.TORTOISE_ORM
aerich init-db
aerich migrate
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000 --timeout-keep-alive 30