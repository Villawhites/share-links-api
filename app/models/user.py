from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, func, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    avatar_url = Column(String(2048), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones - especificar foreign_keys explícitamente
    connections_initiated = relationship(
        "Connection",
        back_populates="user_1",
        foreign_keys="Connection.user_id_1",
        cascade="all, delete-orphan"
    )
    connections_received = relationship(
        "Connection",
        back_populates="user_2",
        foreign_keys="Connection.user_id_2",
        cascade="all, delete-orphan"
    )
    collections = relationship(
        "Collection",
        back_populates="creator",
        foreign_keys="Collection.created_by",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User {self.email}>"