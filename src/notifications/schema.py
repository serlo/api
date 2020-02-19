from base64 import b64encode, b64decode

import graphene
from graphql.utils.ast_to_dict import ast_to_dict
from typing import List

from . import models, tasks


class Event(graphene.ObjectType):
    provider_id = graphene.String()
    id = graphene.String()


class User(graphene.ObjectType):
    provider_id = graphene.String()
    id = graphene.String()


class EventInput(graphene.InputObjectType):
    provider_id = graphene.String(required=True)
    id = graphene.String(required=True)


class UserInput(graphene.InputObjectType):
    provider_id = graphene.String(required=True)
    id = graphene.String(required=True)


class Node(graphene.relay.Node):
    class Meta:
        name = "Node"

    @staticmethod
    def get_node_from_global_id(info, global_id, only_type=None):
        type, id = b64decode(global_id).decode("utf-8").split("-")
        if type == "notification":
            n = models.Notification.objects.get(pk=id)
            return map_notification(n)


class Notification(graphene.ObjectType):
    class Meta:
        interfaces = (graphene.relay.Node,)

    id = graphene.ID(required=True)
    event = graphene.Field(Event)
    user = graphene.Field(User)
    created_at = graphene.DateTime()
    # html = graphene.String()
    seen = graphene.Boolean()


class NotificationConnection(graphene.relay.Connection):
    class Meta:
        node = Notification

    total_count = graphene.Int()

    def resolve_total_count(root, info):
        return models.Notification.objects.count()


def map_notification(n: models.Notification):
    temp = {
        "id": b64encode(bytes("notification-{}".format(n.id), "utf-8")).decode("utf-8"),
        "event": {"provider_id": n.event.provider_id, "id": n.event.event_id},
        "user": {"provider_id": n.user.provider_id, "id": n.user.user_id},
        "created_at": n.event.created_at,
        "seen": n.seen,
    }
    # if "html" in requested_fields:
    #     temp["html"] = html[n.event.event_id]["content"]
    return temp


# class CreateEvent(graphene.Mutation):
#     pass
#
class CreateNotification(graphene.Mutation):
    class Arguments:
        event = EventInput(required=True)
        user = UserInput(required=True)

    id = graphene.ID(required=True)
    event = graphene.Field(Event)
    user = graphene.Field(User)
    created_at = graphene.DateTime()
    seen = graphene.Boolean()

    @staticmethod
    def mutate(root, info, event, user):
        n = tasks.create_notification(
            {
                "event": {"id": event.id, "provider_id": event.provider_id},
                "user": {"id": user.id, "provider_id": user.provider_id},
            }
        )
        return CreateNotification(**map_notification(n))


class ChangeNotification(graphene.relay.ClientIDMutation):
    class Input:
        pass

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        return


class Query(graphene.ObjectType):
    notification = Node.Field(Notification)
    notifications = graphene.relay.ConnectionField(
        NotificationConnection, user=graphene.Argument(UserInput),
    )

    def resolve_notifications(self, info, **payload):
        requested_fields = get_fields(info)

        def get_notifications() -> List[models.Notification]:
            user = payload.get("user")
            if not user:
                return list(models.Notification.objects.all())
            try:
                user = models.User.objects.get(
                    provider_id=user["provider_id"], user_id=user["id"]
                )
            except models.User.DoesNotExist:
                return []
            return list(user.notification_set.all())

        notifications = get_notifications()
        event_ids = [n.event.event_id for n in notifications]

        # if "html" in requested_fields:
        #     html = render_events(
        #         {"event_ids": event_ids, "lang": payload.get("lang"), "format": "html"}
        #     )
        # else:
        #     html = {}

        return list(map(map_notification, notifications))


class Mutation(graphene.ObjectType):
    create_notification = CreateNotification.Field()
    change_notification = ChangeNotification.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)


def collect_fields(node, fragments):
    """Recursively collects fields from the AST
    Args:
        node (dict): A node in the AST
        fragments (dict): Fragment definitions
    Returns:
        A dict mapping each field found, along with their sub fields.
        {'name': {},
         'sentimentsPerLanguage': {'id': {},
                                   'name': {},
                                   'totalSentiments': {}},
         'slug': {}}
    """

    field = {}

    if node.get("selection_set"):
        for leaf in node["selection_set"]["selections"]:
            if leaf["kind"] == "Field":
                field.update({leaf["name"]["value"]: collect_fields(leaf, fragments)})
            elif leaf["kind"] == "FragmentSpread":
                field.update(
                    collect_fields(fragments[leaf["name"]["value"]], fragments)
                )

    return field


def get_fields(info):
    """A convenience function to call collect_fields with info
    Args:
        info (ResolveInfo)
    Returns:
        dict: Returned from collect_fields
    """

    fragments = {}
    node = ast_to_dict(info.field_asts[0])

    for name, value in info.fragments.items():
        fragments[name] = ast_to_dict(value)

    return collect_fields(node, fragments)
