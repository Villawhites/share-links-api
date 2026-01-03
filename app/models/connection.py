from sqlalchemy import Column, String, DateTime, ForeignKey, func, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
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
    
    __table_args__ = (
        CheckConstraint("user_id_1 < user_id_2", name="different_users"),
        UniqueConstraint("user_id_1", "user_id_2", name="unique_connection"),
    )
    
    def __repr__(self):
        return f"<Connection {self.user_id_1} <-> {self.user_id_2}>"