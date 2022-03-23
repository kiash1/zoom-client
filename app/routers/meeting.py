import json
import logging
import requests
from decouple import config
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from pydantic.datetime_parse import datetime

from ..dependencies import zoom_root_api, get_jwt, get_assigned_meeting_id, set_assigned_meeting_id,verify_jwt_authorize
from ..models.meeting import Meeting
from ..models.tortoise.models import HostUser, HostedMeeting, HostedMeetingPydantic
from tortoise.query_utils import Q
from tortoise.query_utils import Prefetch


logger = logging.getLogger(__name__)
zoom_user_meeting_api = config("zoom_user_meeting_api", cast=str, default="/users/{}/meetings")
zoom_meeting_api = config("zoom_meeting_api", cast=str, default="/meetings/")

router = APIRouter(
    prefix="/meetings",
    tags=["meetings"],
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#zoom api to get meeting details
def get_meeting_details(meeting_id: int):
    request_url = zoom_root_api + zoom_meeting_api + str(meeting_id)
    jwt = get_jwt()
    if jwt:
        try:
            logger.info(f"---------ZOOM: Initialize call to {request_url}-----------------")
            response = requests.get(request_url, headers={
                "authorization": "Bearer {}".format(jwt),
                "Content-type": "application/json"
            })
            json_response = response.json()

            logger.info(f"Response from {request_url}: {json_response}")
            logger.info(f"----------Finished {request_url} call----------------")

            if response.status_code == 200:
                if json_response.get("status", "") == "waiting":
                    return {
                        "reuse": True,
                        "data": json_response
                    }

            return {
                "reuse": False,
                "data": json_response
            }
        except Exception as ex:
            logger.info(str(ex))
            return {
                "reuse": False,
                "data": str(ex)
            }


#for doctor portal web dhaka med service role="WEB_SERVICE")
#meeting details saved in redis mapped with host email for reusing if not started/used yet
@router.post("/")
async def create_meetings(meeting: Meeting,token: str = Depends(oauth2_scheme)):
    logger.info(f"---------Initialize creating zoom meeting-----------------")
    authorized = verify_jwt_authorize(token=token,role="WEB_SERVICE")
    jwt = get_jwt()
    if jwt:
        # dont use host, host email is mapped in redis
        host_email = meeting.schedule_for
        logger.info(f"---------Host Email: {host_email}-----------------")

        # check existing meeting can be reused
        meeting_id = meeting.meeting_id if meeting.meeting_id else get_assigned_meeting_id(host_email).get("current_meeting",None)

        if meeting_id:
            data = get_meeting_details(meeting_id)
            can_reuse = data.get("reuse", False)
            if can_reuse:
                response = data.get("data", "")
                return response

        logger.info(f"---------ZOOM: Initialize call to {zoom_root_api + zoom_user_meeting_api.format(host_email)}------------")
        response = requests.post(
            zoom_root_api + zoom_user_meeting_api.format(host_email),
            headers={
                "authorization": "Bearer {}".format(jwt),
                "Content-type": "application/json"
            },
            data=json.dumps(jsonable_encoder(meeting))
        )

        try:
            response_data = response.json()
            logger.info(f"------Response: {response_data}---------")

            set_assigned_meeting_id(host_email, response_data.get("id"))
            return response_data
        except json.decoder.JSONDecodeError as e:
            logger.error(f"Error: {e}")
        logger.info(f"---------Finished call to {zoom_root_api + zoom_user_meeting_api.format(host_email)}------------")
    logger.info(f"---------JWT not found: {jwt}-----------------")
    return {}


#for client patient app service  role="APP_SERVICE"
@router.get("/hosted/{meeting_host}")
async def get_hosted_meeting(meeting_host: str, meeting_id: Optional[str] = None, token: str = Depends(oauth2_scheme)):
         authorized = verify_jwt_authorize(token=token, role="APP_SERVICE")
         meeting_id = meeting_id if meeting_id else get_assigned_meeting_id(meeting_host).get("current_meeting",None)
         if meeting_id:
             data = get_meeting_details(meeting_id)
             response = data.get("data", "")
             return response

         return {
             "meeting": "Not Started please contact your doctor / staffs"
         }


@router.get("/metrics/")
async def get_hosted_meeting(start_time: datetime, end_time: Optional[datetime] = None,
                             appointment_id: Optional[str] = None, meeting_host: Optional[str] = None,
                             token: str = Depends(oauth2_scheme)):
    authorized = verify_jwt_authorize(token=token, role="APP_SERVICE")
    meeting_metrics =  HostedMeeting.filter( Q(start_time__gte=start_time) )
    if end_time:
        meeting_metrics = meeting_metrics.filter( Q(end_time__lte=end_time) )

    if meeting_host:
        meeting_metrics = meeting_metrics.filter(Q(hostuser__host_email__iexact=meeting_host))

    # meeting_metrics_ret = await meeting_metrics.all().prefetch_related('hostuser')
    # print(meeting_metrics_ret)

    from tortoise.contrib.pydantic import pydantic_model_creator
    HostedMeetingPydantic = pydantic_model_creator(HostedMeeting)
    meeting_metrics_schema = await HostedMeetingPydantic.from_queryset(meeting_metrics.all().prefetch_related('hostuser'))


    return {
        "data": meeting_metrics_schema
    }
