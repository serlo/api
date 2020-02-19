from django.test import TestCase
from graphene.test import Client

from .schema import schema
from .models import Notification, Event, User


class NotificationQueryTests(TestCase):
    def test_no_notifications(self) -> None:
        client = Client(schema)
        result = client.execute(
            """
            query {
                notifications {
                    totalCount
                    edges {
                        node {
                            createdAt
                        }
                    }
                }
            }
        """
        )
        self.assertEqual(
            result, {"data": {"notifications": {"totalCount": 0, "edges": []}}}
        )

    def test_one_notification(self) -> None:
        user = User.objects.create(user_id="user-1", provider_id="user-provider")
        event = Event.objects.create(
            event_id="event-1",
            provider_id="event-provider",
            created_at="2015-08-06T16:53:10+01:00",
        )
        Notification.objects.create(event=event, user=user)

        client = Client(schema)
        result = client.execute(
            """
            query {
                notifications {
                    totalCount
                    edges {
                        node {
                            createdAt
                        }
                    }
                }
            }
        """
        )
        self.assertEqual(
            result,
            {
                "data": {
                    "notifications": {
                        "totalCount": 1,
                        "edges": [{"node": {"createdAt": "2015-08-06T15:53:10+00:00"}}],
                    }
                }
            },
        )

    def test_two_notifications(self) -> None:
        user = User.objects.create(user_id="user-1", provider_id="user-provider")
        user2 = User.objects.create(user_id="user-2", provider_id="user-provider")
        event = Event.objects.create(
            event_id="event-1",
            provider_id="event-provider",
            created_at="2015-08-06T16:53:10+01:00",
        )
        Notification.objects.create(event=event, user=user)
        Notification.objects.create(event=event, user=user2)

        client = Client(schema)
        result = client.execute(
            """
            query {
                notifications {
                    totalCount
                    edges {
                        node {
                            user {
                                id
                            }
                            createdAt
                        }
                    }
                }
            }
        """
        )
        self.assertEqual(
            result,
            {
                "data": {
                    "notifications": {
                        "totalCount": 2,
                        "edges": [
                            {
                                "node": {
                                    "user": {"id": "user-1"},
                                    "createdAt": "2015-08-06T15:53:10+00:00",
                                }
                            },
                            {
                                "node": {
                                    "user": {"id": "user-2"},
                                    "createdAt": "2015-08-06T15:53:10+00:00",
                                }
                            },
                        ],
                    }
                }
            },
        )
