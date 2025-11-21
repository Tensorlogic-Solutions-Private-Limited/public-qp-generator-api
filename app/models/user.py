from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.audit_mixin import AuditMixin


class Role(Base, AuditMixin):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    role_code = Column(String, unique=True, nullable=False)
    role_name = Column(String, unique=True, nullable=False)
    users = relationship("User", back_populates="role", cascade="all, delete")

class User(Base, AuditMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    role = relationship("Role", back_populates="users")