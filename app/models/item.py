from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base
import uuid

class Item(Base):
    __tablename__ = "items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collection_id = Column(UUID(as_uuid=True), ForeignKey("collections.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String(2048), nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(2048), nullable=True)
    platform = Column(String(100), nullable=True)  # instagram, tiktok, youtube, generic
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)  # soft delete
    version = Column(Integer, default=0)
    item_metadata = Column(JSONB, nullable=True)  # ← Cambié de 'metadata' a 'item_metadata'
    
    def __repr__(self):
        return f"<Item {self.title}>"