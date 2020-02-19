from .models import Event, User, Notification
from datetime import datetime
from typing import TypedDict, List


class UserPayload(TypedDict):
    provider_id: str
    id: str


class EventPayload(TypedDict):
    provider_id: str
    id: str


class CreateEventPayload(TypedDict):
    event: EventPayload
    created_at: str


class NotificationPayload(TypedDict):
    event: EventPayload
    user: UserPayload


CreateNotificationPayload = NotificationPayload
ReadNotificationPayload = NotificationPayload


def create_event(payload: CreateEventPayload) -> Event:
    event = get_event_or_create(payload)
    return event


def create_notification(payload: CreateNotificationPayload) -> Notification:
    user = get_user_or_create(payload["user"])
    event = Event.objects.get(
        event_id=payload["event"]["id"], provider_id=payload["event"]["provider_id"]
    )
    notification, _ = Notification.objects.get_or_create(event=event, user=user)
    return notification


def read_notification(payload: ReadNotificationPayload) -> Notification:
    notification = create_notification(payload)
    notification.seen = True
    notification.save()
    return notification


def get_user_or_create(payload: UserPayload) -> User:
    user, _ = User.objects.get_or_create(
        user_id=payload["id"], provider_id=payload["provider_id"]
    )
    return user


def get_event_or_create(payload: CreateEventPayload) -> Event:
    event, _ = Event.objects.get_or_create(
        event_id=payload["event"]["id"],
        provider_id=payload["event"]["provider_id"],
        created_at=payload["created_at"],
    )
    return event


def datetime_from_timestamp(timestamp: str) -> datetime:
    return datetime.fromisoformat(timestamp)
