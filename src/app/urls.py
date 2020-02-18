from django.urls import path
from graphene_django.views import GraphQLView

from . import views

urlpatterns = [
    path("graphql", GraphQLView.as_view(graphiql=False)),
    path("health", views.health, name="health"),
]
