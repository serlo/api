import graphene

from serlo_org.schema import Query as SerloOrgQuery


class Query(SerloOrgQuery, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
