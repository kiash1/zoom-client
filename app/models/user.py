from pydantic.datetime_parse import datetime
from pydantic.main import BaseModel


class User(BaseModel):
    """
    email
    first name
    last name
    type basic 1 , licensed 2
    """
    email: str
    first_name: str
    last_name: str
    type: int


