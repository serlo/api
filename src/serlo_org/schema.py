import graphene
import requests


class AbstractUuid(graphene.ObjectType):
    def __init__(self, *args, **data):
        super().__init__(*args, **data)
        self.id = data["id"]

    id = graphene.Int()


class UnknownUuid(AbstractUuid):
    pass


class PageUuid(AbstractUuid):
    pass


class Uuid(graphene.Union):
    class Meta:
        types = (PageUuid, UnknownUuid)


class Alias(graphene.InputObjectType):
    instance = graphene.String(required=True)
    path = graphene.String(required=True)


class Query(graphene.ObjectType):
    uuid = graphene.Field(Uuid, alias=Alias(), id=graphene.Int())

    def resolve_uuid(self, info, **payload):
        # by alias
        alias_payload = payload.get("alias")
        if alias_payload:
            # TODO:
            response = requests.post(
                "http://host.docker.internal:9009/api/resolve-alias",
                json={
                    "instance": alias_payload.get("instance"),
                    "path": alias_payload.get("path"),
                },
            )
            data = response.json()
            if data["type"] == "page":
                return PageUuid(id=data["id"])
            if data["id"]:
                return UnknownUuid(id=data["id"])
        return UnknownUuid(id=123)
