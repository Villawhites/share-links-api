from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class ItemCreate(BaseModel):
    url: str
    title: str | None = None
    description: str | None = None

class ItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

class ItemResponse(BaseModel):
    id: UUID
    collection_id: UUID
    url: str
    title: str | None
    description: str | None
    thumbnail_url: str | None
    platform: str | None
    created_by: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    item_metadata: Optional[dict] = None  # ← Cambié de 'metadata' a 'item_metadata'
    
    class Config:
        from_attributes = True