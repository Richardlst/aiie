from typing import Annotated
from fastapi import Depends
from .connections import connections
from .schemas import WSConnections
from .connection_manager import ConnectionManager


def get_connections() -> WSConnections:
    return connections


def get_connection_manager(
    connections: WSConnections = Depends(get_connections),
) -> ConnectionManager:
    return ConnectionManager(connections=connections)


ConnectionManagerDep = Annotated[ConnectionManager, Depends(get_connection_manager)]
