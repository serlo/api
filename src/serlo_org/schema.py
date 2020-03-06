import graphene
import requests


class AbstractUuid(graphene.ObjectType):
    def __init__(self, *args, **data):
        super().__init__(*args, **data)
        self.id = data["id"]

    id = graphene.Int()


class UuidDiscriminator(graphene.Enum):
    entity = "entity"
    page = "page"


class Instance(graphene.Enum):
    de = "de"
    en = "en"


class License(graphene.ObjectType):
    id = graphene.Int()
    instance = Instance()
    title = graphene.String()
    url = graphene.String()
    content = graphene.String()
    agreement = graphene.String()
    icon_href = graphene.String()


class EntityRevision(AbstractUuid):
    # author = graphene.Field(User)
    # date = graphene.DateTime
    pass


class ArticleRevision(EntityRevision):
    title = graphene.String()
    content = graphene.String()
    changes = graphene.String()


class AbstractEntity(AbstractUuid):
    def __init__(self, *args, **data):
        super().__init__(*args, **data)
        self.instance = data["instance"]

    instance = Instance()
    license = graphene.Field(License)
    current_revision = graphene.Field(ArticleRevision)
    # date = graphene.DateTime


class ArticleUuid(AbstractEntity):
    pass


class PageUuid(AbstractUuid):
    pass


class UnknownUuid(AbstractUuid):
    def __init__(self, *args, **data):
        super().__init__(*args, **data)
        self.discriminator = data["discriminator"]

    discriminator = UuidDiscriminator()


class Uuid(graphene.Union):
    class Meta:
        types = (ArticleUuid, PageUuid, UnknownUuid)


class Alias(graphene.InputObjectType):
    instance = Instance(required=True)
    path = graphene.String(required=True)


class Query(graphene.ObjectType):
    uuid = graphene.Field(Uuid, alias=Alias(), id=graphene.Int())

    def resolve_uuid(self, info, **payload):
        def fetch_info():
            alias_payload = payload.get("alias")
            if alias_payload:
                return requests.post(
                    "http://host.docker.internal:9009/api/url-alias",
                    json={
                        "instance": alias_payload.get("instance"),
                        "path": alias_payload.get("path"),
                    },
                )
            id_payload = payload.get("id")
            if id_payload:
                return requests.post(
                    "http://host.docker.internal:9009/api/uuid",
                    json={"id": id_payload},
                )

        data = fetch_info().json()
        if data["discriminator"] == "page":
            return PageUuid(id=data["id"])
        if data["discriminator"] == "entity":
            if data["type"] == "article":
                article = ArticleUuid(id=data["id"], instance=data["instance"])
                article.current_revision = {"id": data["currentRevisionId"]}
                article.license = {"id": data["licenseId"]}
                return article
        return UnknownUuid(id=data["id"], discriminator=data["discriminator"])
