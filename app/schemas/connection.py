from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ConnectionCreate(BaseModel):
    user_id_2: UUID

class ConnectionAccept(BaseModel):
    status: str  # accepted, rejected

class ConnectionResponse(BaseModel):
    id: UUID
    user_id_1: UUID
    user_id_2: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True