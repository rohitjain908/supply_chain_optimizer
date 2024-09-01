from pydantic import BaseModel as PydanticBaseModel, Field
from typing import Optional, Any, List
from enum import IntEnum


class StatusCode(IntEnum):
    """Enum for HTTP status codes relevant to the route cost response."""

    OK = 200
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    TOO_MANY_REQUESTS = 429


class BaseModel(PydanticBaseModel):
    """Base model for all data models"""

    class Config:
        populate_by_name = True
        validate_assignment = True
        arbitrary_types_allowed = True
        protected_namespaces = ()


class RouteCostResponse(BaseModel):
    """Model for route cost response."""

    status: StatusCode
    error: Optional[str] = None
    data: Optional[Any] = None

class AvailableRoute(BaseModel):

    routeNumber: int
    distance: float

class WareHouse(BaseModel):

    warehouseId: str
    demand: int
    availableRoutes: List[AvailableRoute]


class StoresResponse(BaseModel):

    warehouses: List[WareHouse]