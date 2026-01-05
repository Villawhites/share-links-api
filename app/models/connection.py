from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, func, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Connection(Base):
    __tablename__ = "connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id_1 = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_id_2 = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="pending")  # pending, accepted, blocked
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    user_1 = relationship(
        "User",
        back_populates="connections_initiated",
        foreign_keys=[user_id_1]
    )
    user_2 = relationship(
        "User",
        back_populates="connections_received",
        foreign_keys=[user_id_2]
    )
    
    __table_args__ = (
        CheckConstraint("user_id_1 < user_id_2", name="different_users"),
        UniqueConstraint("user_id_1", "user_id_2", name="unique_connection"),
    )
    
    def __repr__(self):
        return f"<Connection {self.user_id_1} <-> {self.user_id_2}>"