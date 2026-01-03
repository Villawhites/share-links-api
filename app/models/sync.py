from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger, Boolean, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base
import uuid

class SyncLog(Base):
    __tablename__ = "sync_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)  # collection, item
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    operation = Column(String(50), nullable=False)  # create, update, delete
    data = Column(JSONB, nullable=False)
    timestamp = Column(BigInteger, nullable=False, index=True)  # client timestamp en ms
    server_timestamp = Column(DateTime, default=func.now())
    synced = Column(Boolean, default=False, index=True)
    conflict_resolved = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<SyncLog {self.entity_type} {self.operation}>"