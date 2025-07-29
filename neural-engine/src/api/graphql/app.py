"""GraphQL application setup."""

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
import logging

from .schema.queries import Query
from .schema.mutations import Mutation
from .schema.subscriptions import Subscription

logger = logging.getLogger(__name__)

# Create GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
)

# Create GraphQL router with WebSocket support for subscriptions
graphql_router = GraphQLRouter(
    schema,
    subscription_protocols=[
        GRAPHQL_TRANSPORT_WS_PROTOCOL,
        GRAPHQL_WS_PROTOCOL,
    ],
)
