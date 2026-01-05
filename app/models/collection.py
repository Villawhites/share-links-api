from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, func, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(
        UUID(as_uuid=True),
        ForeignKey("connections.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name = Column(String(255), nullable=False)
    icon = Column(String(50), nullable=True)  # emoji
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    version = Column(Integer, default=0)
    
    # Relaciones
    creator = relationship(
        "User",
        back_populates="collections",
        foreign_keys=[created_by]
    )
    connection = relationship(
        "Connection",
        foreign_keys=[connection_id]
    )
    
    def __repr__(self):
        return f"<Collection {self.name}>"