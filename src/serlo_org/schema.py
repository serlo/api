import graphene
import logging
import requests

from shared.graphql import get_fields

logger = logging.getLogger(__name__)


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
    default = graphene.Boolean()
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


class Article(AbstractEntity):
    pass


class Page(AbstractUuid):
    pass


class UnknownUuid(AbstractUuid):
    def __init__(self, *args, **data):
        super().__init__(*args, **data)
        self.discriminator = data["discriminator"]

    discriminator = UuidDiscriminator()


class Uuid(graphene.Union):
    class Meta:
        types = (Article, ArticleRevision, Page, UnknownUuid)


class Alias(graphene.InputObjectType):
    instance = Instance(required=True)
    path = graphene.String(required=True)


def resolve_license(_parent, _info, **payload):
    data = requests.post(
        "http://host.docker.internal:9009/api/license", json={"id": payload.get("id")},
    ).json()
    return {
        "id": data["id"],
        "instance": data["instance"],
        "default": data["default"],
        "title": data["title"],
        "url": data["url"],
        "content": data["content"],
        "agreement": data["agreement"],
        "icon_href": data["iconHref"],
    }


def resolve_uuid(_parent, info, **payload):
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
                "http://host.docker.internal:9009/api/uuid", json={"id": id_payload},
            )

    requested_fields = get_fields(info)
    logger.error(requested_fields)
    data = fetch_info().json()
    if data["discriminator"] == "page":
        return Page(id=data["id"])
    if data["discriminator"] == "entity":
        if data["type"] == "article":
            requested_fields = requested_fields["Article"]
            article = Article(id=data["id"], instance=data["instance"])
            if "currentRevision" in requested_fields:
                article.current_revision = {"id": data["currentRevisionId"]}
                if list(requested_fields["currentRevision"].keys()) > ["id"]:
                    article.current_revision = resolve_uuid(
                        None, info, id=data["currentRevisionId"]
                    )
            if "license" in requested_fields:
                article.license = {"id": data["licenseId"]}
                if list(requested_fields["license"].keys()) > ["id"]:
                    article.license = resolve_license(None, info, id=data["licenseId"])
            return article
    if data["discriminator"] == "entityRevision":
        if data["type"] == "article":
            revision = ArticleRevision(id=data["id"])
            revision.title = data["fields"]["title"]
            revision.content = data["fields"]["content"]
            revision.changes = data["fields"]["changes"]
            return revision

    return UnknownUuid(id=data["id"], discriminator=data["discriminator"])


class Query(graphene.ObjectType):
    license = graphene.Field(
        License, id=graphene.Int(required=True), resolver=resolve_license
    )
    uuid = graphene.Field(Uuid, alias=Alias(), id=graphene.Int(), resolver=resolve_uuid)
