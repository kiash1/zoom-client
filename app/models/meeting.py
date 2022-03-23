from pydantic.datetime_parse import datetime
from pydantic.main import BaseModel
from typing import Optional

class MeetingSettings(BaseModel):
    """
    approval_type: 2 no registration required
    join_before_host: bool
    jbh_time: 0 to allow participant to join 10 minutes before start time

    """
    approval_type: int
    join_before_host: bool
    jbh_time: int
    host_video: bool
    participant_video: bool


class Meeting(BaseModel):
    """
    topic
    type 1 instant
    start_time
    password
    duration minute
    schedule_for email or zoom userid
    """
    meeting_id: Optional[int] = None
    topic: str
    type: int
    duration: int
    password: str
    schedule_for: str
    timezone : Optional[str] = "UTC"
    settings: MeetingSettings


class MeetingEvent(BaseModel):
    meeting_id: str
    host_id: str
    host_email: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    timezone: Optional[str] = None
