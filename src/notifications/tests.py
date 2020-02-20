from django.test import TestCase
from graphene.test import Client
from base64 import b64encode
from collections import OrderedDict

from .schema import schema
from .models import Notification, Event, User
from .tasks import create_notification, change_notification_status, create_event


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


class CreateEventTests(TestCase):
    def test_create_event(self) -> None:
        client = Client(schema)
        result = client.execute(
            """
            mutation {
                createEvent(
                    event: {
                        id: "event-1",
                        providerId: "event-provider"
                    },
                    createdAt: "2015-08-06T16:53:10+01:00"
                )
                {
                    event {
                        id
                    }
                }
            }
        """
        )
        self.assertEqual(
            result, {"data": {"createEvent": {"event": {"id": "event-1"}}}}
        )

    def test_create_event_only_once(self) -> None:
        client = Client(schema)
        result = client.execute(
            """
            mutation {
                createEvent(
                    event: {
                        id: "event-1",
                        providerId: "event-provider"
                    },
                    createdAt: "2015-08-06T16:53:10+01:00"
                )
                {
                    event {
                        id
                    }
                }
            }
        """
        )
        result = client.execute(
            """
            mutation {
                createEvent(
                    event: {
                        id: "event-1",
                        providerId: "event-provider"
                    },
                    createdAt: "2015-08-06T16:53:10+01:00"
                )
                {
                    event {
                        id
                    }
                }
            }
        """
        )
        self.assertEqual(Event.objects.count(), 1)


class CreateNotificationTests(TestCase):
    fixtures = ["fixtures.json"]

    def test_create_notification_for_nonexistingevent(self) -> None:
        from graphql.error.located_error import GraphQLLocatedError

        client = Client(schema)
        mutation = """
            mutation {
                createNotification(
                    event: {
                        id: "event-3",
                        providerId: "event-provider"
                    },
                    user: {
                        id: "user-1", 
                        providerId: "user-provider"
                    }
                )
                {
                    event {
                        id
                    }
                    seen
                }
            }
        """
        # TODO: transform into self.assertRaises()
        try:
            client.execute(mutation)
        except Event.DoesNotExist:
            raise GraphQLLocatedError

    def test_create_notification(self) -> None:
        client = Client(schema)
        result = client.execute(
            """
            mutation {
                createNotification(
                    event: {
                        id: "event-2",
                        providerId: "event-provider"
                    },
                    user: {
                        id: "user-2", 
                        providerId: "user-provider"
                    }
                )
                {
                    createdAt
                    event {
                        id
                    }
                    seen
                }
            }
        """
        )
        self.assertEqual(
            result,
            {
                "data": OrderedDict(
                    {
                        "createNotification": {
                            "createdAt": "2020-01-01T01:00:00+00:00",
                            "event": {"id": "event-2"},
                            "seen": False,
                        }
                    }
                )
            },
        )

    def test_create_notification_only_once(self) -> None:
        client = Client(schema)
        result = client.execute(
            """
            mutation {
                createNotification(
                    event: {
                        id: "event-2",
                        providerId: "event-provider"
                    },
                    user: {
                        id: "user-2", 
                        providerId: "user-provider"
                    }
                )
                {
                    createdAt
                    event {
                        id
                    }
                    seen
                }
            }
        """
        )
        result = client.execute(
            """
            mutation {
                createNotification(
                    event: {
                        id: "event-2",
                        providerId: "event-provider"
                    },
                    user: {
                        id: "user-2", 
                        providerId: "user-provider"
                    }
                )
                {
                    createdAt
                    event {
                        id
                    }
                    seen
                }
            }
        """
        )
        query_result = client.execute(
            """
            query {
                notifications {
                    totalCount
                }
            }
        """
        )
        self.assertEqual(
            query_result, {"data": OrderedDict({"notifications": {"totalCount": 4}})}
        )
        self.assertEqual(Notification.objects.count(), 4)


class NotificationStatusTests(TestCase):
    fixtures = ["fixtures.json"]

    def test_change_notification_status(self) -> None:
        clientMutationId = b64encode(
            bytes("notification-{}".format(1), "utf-8")
        ).decode("utf-8")

        client = Client(schema)
        result = client.execute(
            """
            mutation($id: String!, $seen: Boolean!) {
                changeNotificationStatus(
                    input: {
                        clientMutationId: $id, 
  	                    seen: $seen
                })
                {
                    seen
                }
            }
        """,
            variables={"id": clientMutationId, "seen": True},
        )
        self.assertEqual(
            result, {"data": OrderedDict({"changeNotificationStatus": {"seen": True}})}
        )
