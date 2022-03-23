from datetime import datetime, timezone, timedelta

import jwt
import json
import logging
import redis
from decouple import config
from jwt import exceptions as JWTExceptions
from fastapi import HTTPException,Request
from typing import Optional


logger = logging.getLogger(__name__)
zoom_root_api = config("zoom_root_api", cast=str, default="https://api.zoom.us/v2/")
zoom_hook_token =  config("zoom_hook_token", cast=str, default=None)

app_redis = redis.Redis(
    host=config("redis_host", cast=str, default="localhost"),
    port=config("redis_port", cast=int, default=6379),
    db=config("redis_db", cast=int, default=0)
)

zoom_jwt_credentials = {
    "api_key": config("api_key", cast=str),
    "api_secret": config("api_secret", cast=str),
}

service_jwt_credentials = {
    "WEB_SERVICE": config("web_service_jwt_secret", cast=str),
    "APP_SERVICE": config("app_service_jwt_secret", cast=str),

}
zoom_admin_email = config("email", cast=str, default="mazg1493@gmail.com")

#TODO discard after finalization
def generate_test_service_jwt():
    expiry_seconds = config("jwt_expiry_seconds", cast=int, default=604800)
    utc_datetime = datetime.now(timezone.utc)
    current_datetime = datetime.astimezone(utc_datetime)
    expiry_time = (current_datetime + timedelta(seconds=expiry_seconds))
    epoch_time = int(expiry_time.timestamp())

    jwt_payload = {
        "iss": "ROBI MED SETVICE",
        "exp": epoch_time
    }

    jwt_token = jwt.encode(jwt_payload, service_jwt_credentials.get("APP_SERVICE", ""), algorithm="HS256")


    return jwt_token if not isinstance(jwt_token, bytes) else jwt_token.decode("utf-8")


def verify_zoom_hook(token):
    if token != zoom_hook_token:
        raise HTTPException(status_code=401, detail="Unauthorized ")

def verify_jwt_authorize(token: str, role: str):
    try:
        secret_key = service_jwt_credentials.get(role,"")
        decoded_token = jwt.decode(jwt=token, key=secret_key, algorithms="HS256")
    except (JWTExceptions.InvalidTokenError, JWTExceptions.InvalidSignatureError,
                         JWTExceptions.DecodeError, JWTExceptions.ExpiredSignatureError)as ex:
        logger.info(str(ex))
        raise HTTPException(status_code=401, detail="Unauthorized "+str(ex))
    return True



def generate_jwt():
    expiry_seconds = config("jwt_expiry_seconds", cast=int, default=604800)
    utc_datetime = datetime.now(timezone.utc)
    current_datetime = datetime.astimezone(utc_datetime)
    expiry_time = (current_datetime + timedelta(seconds=expiry_seconds))
    epoch_time = int(expiry_time.timestamp())

    jwt_payload = {
        "iss": zoom_jwt_credentials.get("api_key", ""),
        "exp": epoch_time
    }

    jwt_token = jwt.encode(jwt_payload, zoom_jwt_credentials.get("api_secret", ""), algorithm="HS256")

    app_redis.set("jwt", jwt_token, expiry_seconds)

    return jwt_token if not isinstance(jwt_token, bytes) else jwt_token.decode("utf-8")


def get_jwt():
    jwt_token = app_redis.get("jwt")
    #if not jwt_token:
    #TODO check jwt expiry then generate else use the one saved in redis
    jwt_token = generate_jwt()
    return jwt_token if not isinstance(jwt_token, bytes) else jwt_token.decode("utf-8")


def generate_jwt_for_robimed():
    expiry_seconds = config("jwt_expiry_seconds", cast=int, default=604800)
    utc_datetime = datetime.now(timezone.utc)
    current_datetime = datetime.astimezone(utc_datetime)
    expiry_time = (current_datetime + timedelta(seconds=expiry_seconds))
    epoch_time = int(expiry_time.timestamp())

    jwt_payload = {
        "iss": "ROBI MED SERVICE",
        "exp": epoch_time
    }

    jwt_token = jwt.encode(jwt_payload, config("robi_service_jwt_secret", cast=str, default="RobiMedServiceSecretKey"), algorithm="HS256")

    return jwt_token if not isinstance(jwt_token, bytes) else jwt_token.decode("utf-8")


def get_assigned_meeting_id(doc_mail):
    # "host":"nabil@zssbd.com" : { "current_meeting" : meeting_id }
    current_meeting = app_redis.hget("host", doc_mail)
    if current_meeting:
        return json.loads(current_meeting.decode('utf-8'))
    return {"current_meeting": None}


def set_assigned_meeting_id(doc_mail, meeting_id):
    data_to_save = {"current_meeting": meeting_id}
    app_redis.hset("host", doc_mail, json.dumps(data_to_save).encode('utf-8'))
    logger.info("***** meeting saved ******")
    logger.info(get_assigned_meeting_id(doc_mail))
