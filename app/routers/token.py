from fastapi import APIRouter

from ..dependencies import generate_test_service_jwt#generate_jwt

router = APIRouter(
    prefix="/token",
    tags=["token"],
)

#TODO COMMENT OUT, ONLY FOR TEST PURPOSE
@router.get("/create/")
async def get_jwt_token():
    # https://stackoverflow.com/questions/25837452/python-get-current-time-in-right-timezone
    return {
        "token": generate_test_service_jwt()
    }
