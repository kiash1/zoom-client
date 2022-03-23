from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator



class HostUser(Model):
    id = fields.IntField(pk=True)
    host_email = fields.CharField(max_length=50, unique=True)
    host_id = fields.CharField(max_length=100, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        ordering = ['host_email']


class HostedMeeting(Model):
    """
    This references a hosted meeting by host user
    """

    id = fields.IntField(pk=True)
    meeting_id = fields.CharField(max_length=100)
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField(null=True,default=None)
    timezone = fields.CharField(max_length=20)
    event = fields.CharField(max_length=20,null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    hostuser = fields.ForeignKeyField(
        "models.HostUser", related_name="hostuser", description="user hosted this meeting"
    )

HostUserPydantic = pydantic_model_creator(HostUser)
HostedMeetingPydantic = pydantic_model_creator(HostedMeeting)
