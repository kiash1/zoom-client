import json
import logging
import requests
from datetime import datetime
from decouple import config
from fastapi import APIRouter,  Response
from starlette.requests import Request
from fastapi.encoders import jsonable_encoder
from typing import Optional
from fastapi.security import OAuth2PasswordBearer

from ..dependencies import verify_zoom_hook,generate_jwt_for_robimed

from ..models.tortoise.models import HostUser, HostedMeeting


logger = logging.getLogger(__name__)

zoom_user_meeting_api = config("zoom_user_meeting_api", cast=str, default="/users/{}/meetings")
zoom_meeting_api = config("zoom_meeting_api", cast=str, default="/meetings/")
robi_appointment_meeting_update_api = config("ROBI_MED_SERVICE_BASE", cast=str, default="") + config(
    "ROBI_MED_MEETING_UPDATE_URL", cast=str, default="")

router = APIRouter(
    prefix="/zoom-events",
    tags=["events"],
)


def update_appointment_meeting(data):
    api =   robi_appointment_meeting_update_api.format(data.get("meeting_id"))
    response_data = {}
    try:
        logger.info(f"---------ROBI: Initialize call to {api}-----------------")
        jwt = generate_jwt_for_robimed()
        response = requests.put(
            api,
            headers={
                "authorization": "Bearer {}".format(jwt),
                "Content-type": "application/json"
            },
            data=json.dumps(jsonable_encoder(data))
        )
        # print("JWT {}".format(jwt))
        response_data = response.json()
        logger.info(f"Response from {api}: {response_data}")
        logger.info(f"----------Finished {api} call----------------")
    except Exception as ex:
        logger.info(ex)



@router.post("/")
async def zoom_events(request: Request):
    logger.info("ZOOM EVENT OCCURRED!!!")
    req_body = await request.json()
    req_headers = jsonable_encoder(request.headers)
    verify_zoom_hook(req_headers["authorization"])

    logger.info(req_body)
    logger.info(req_headers)

    currentmeeting = {
        "event": req_body.get("event"),
        "meeting_id": req_body["payload"]["object"].get("id"),
        "host_id": req_body["payload"]["object"].get("host_id"),
        "start_time": req_body["payload"]["object"].get("start_time"),
        "end_time": req_body["payload"]["object"].get("end_time"),
        "timezone": req_body["payload"]["object"].get("timezone")

    }

    try:
        currentmeeting["start_time"] = datetime.strptime(currentmeeting["start_time"], "%Y-%m-%dT%H:%M:%SZ")

        hosted_user = await HostUser.get(host_id=currentmeeting["host_id"])
        await HostedMeeting.get_or_create(
            meeting_id=currentmeeting["meeting_id"],
            start_time=currentmeeting["start_time"],
            timezone=currentmeeting["timezone"],
            hostuser=hosted_user,
            event=currentmeeting["event"]
        )
        currentmeeting["status"] = config("MEETING_STARTED", cast=int, default=1)
        if currentmeeting["end_time"]:
            meeting_hosted = await HostedMeeting.get(meeting_id=currentmeeting["meeting_id"]).all().order_by(
                '-id').first()
            currentmeeting["end_time"] = datetime.strptime(currentmeeting["end_time"], "%Y-%m-%dT%H:%M:%SZ")
            meeting_hosted.event = currentmeeting["event"]
            meeting_hosted.end_time = currentmeeting["end_time"]
            await meeting_hosted.save()
            currentmeeting["status"] = config("MEETING_ENDED", cast=int,default=2)

    except Exception as ex:
        # TODO specify unraised exceptions mostly parse error
        logger.info(str(ex))

    update_appointment_meeting(currentmeeting)
    logger.info("*******Current Meeting*******")
    logger.info(currentmeeting)

    return Response(status_code=200)
