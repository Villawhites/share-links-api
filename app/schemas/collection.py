from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class CollectionCreate(BaseModel):
    name: str
    icon: str | None = None

class CollectionUpdate(BaseModel):
    name: str | None = None
    icon: str | None = None

class CollectionResponse(BaseModel):
    id: UUID
    connection_id: UUID
    name: str
    icon: str | None
    created_by: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True