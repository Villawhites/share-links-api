from pydantic import BaseModel
from uuid import UUID
from typing import Any

class SyncDataRequest(BaseModel):
    entity_type: str  # collection, item
    entity_id: UUID
    operation: str  # create, update, delete
    timestamp: int  # client timestamp en ms
    data: dict[str, Any]

class SyncResponse(BaseModel):
    status: str  # success, conflict
    resolved_conflict: bool = False
    server_data: dict[str, Any] | None = None
    message: str | None = None