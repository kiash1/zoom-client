from datetime import datetime


def date_validator(date: str):
    return datetime.fromisoformat(date)
