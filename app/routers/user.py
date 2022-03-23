import json
import logging
import requests
from decouple import config
from fastapi import APIRouter,Depends
from fastapi.security import OAuth2PasswordBearer
from ..dependencies import app_redis, zoom_root_api, get_jwt,verify_jwt_authorize
zoom_user_api = config("zoom_user_api", cast=str, default="users")
from fastapi.encoders import jsonable_encoder
from ..models.user import User
from ..models.tortoise.models import HostUser
from tortoise import run_async

router = APIRouter(
    prefix="/user",
    tags=["meetings"],
)

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_information(user_email):
    jwt = get_jwt()
    if jwt:
        logger.info(f"---------ZOOM: Initialize getting user information: {zoom_root_api}{zoom_user_api}/{user_email}-----------------")
        response = requests.get(zoom_root_api+zoom_user_api+"/"+user_email, headers={
            "authorization": "Bearer {}".format(jwt),
            "Content-type": "application/json"
        })
        json_response = response.json()
        logger.info(f"---------Finished getting user information: {json_response}-----------------")
        return json_response
    return {}


@router.post("/create/")
async def create_basic_user(user: User, token: str = Depends(oauth2_scheme)):
    authorized = verify_jwt_authorize(token=token,role="WEB_SERVICE")
    jwt = get_jwt()
    if jwt:
        request_data = {
                "action": "create",
                "user_info":jsonable_encoder(user)
            }
        request_url = zoom_root_api + zoom_user_api
        logger.info(f"---------ZOOM: Initialize creating user information: {request_url}-----------------")
        response = requests.post(
            request_url,
            headers={
                "authorization": "Bearer {}".format(jwt),
                "Content-type": "application/json"
            },
            json=request_data

        )

        response_data = response.json()
        #create host user
        logger.info(f"----Response from creating user: {response_data}--------")
        if response.status_code == 201:
            host_user = await HostUser.get_or_create(host_id=str(response_data['id']), host_email=response_data['email'])
        elif response.status_code == 409:
            created_user = get_user_information(user.email)
            host_user = await HostUser.get_or_create(host_id=str(created_user['id']),
                                                     host_email=created_user['email'])


        return response_data
    return {}
