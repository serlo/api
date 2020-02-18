import graphene


class Query(graphene.ObjectType):
    version = graphene.String()

    def resolve_version(parent, info):
        return "0.0.0"


schema = graphene.Schema(query=Query)
