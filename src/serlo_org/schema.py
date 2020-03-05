import graphene
import requests


class AbstractUuid(graphene.ObjectType):
    def __init__(self, *args, **data):
        super().__init__(*args, **data)
        self.id = data["id"]

    id = graphene.Int()


class ArticleUuid(AbstractUuid):
    pass


class PageUuid(AbstractUuid):
    pass


class UnknownUuid(AbstractUuid):
    pass


class Uuid(graphene.Union):
    class Meta:
        types = (ArticleUuid, PageUuid, UnknownUuid)


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
            if data["discriminator"] == "page":
                return PageUuid(id=data["id"])
            if data["discriminator"] == "entity":
                if data["type"] == "article":
                    return ArticleUuid(id=data["id"])
            return UnknownUuid(id=data["id"])
