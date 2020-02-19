from django.db import models
import uuid
from typing import TypedDict


# class EventJson(TypedDict):
#     id: str
#     provider_id: str
#
#
# class NotificationJson(TypedDict):
#     event: EventJson
#     created_at: str


class Event(models.Model):
    event_id = models.CharField(max_length=200)
    provider_id = models.CharField(max_length=200)
    created_at = models.DateTimeField()
    #
    # def to_json(self) -> EventJson:
    #     return {"id": self.event_id, "provider_id": self.provider_id}


class User(models.Model):
    user_id = models.CharField(max_length=200)
    provider_id = models.CharField(max_length=200)


class Notification(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seen = models.BooleanField(default=False)
    #
    # def to_json(self) -> NotificationJson:
    #     return {
    #         "event": self.event.to_json(),
    #         "created_at": self.event.created_at,
    #     }
