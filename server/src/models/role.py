from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import relationship

from src.db.base_class import Base


class Permission(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)

    # Relationships
    roles = relationship("Role", secondary="rolepermission", back_populates="permissions")


class Role(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)

    # Relationships
    permissions = relationship("Permission", secondary="rolepermission", back_populates="roles")
    users = relationship("User", secondary="userrole", back_populates="roles")


class RolePermission(Base):
    __tablename__ = "rolepermission"

    role_id = Column(Integer, ForeignKey("role.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permission.id"), primary_key=True)

    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='_role_permission_uc'),
    )


class UserRole(Base):
    __tablename__ = "userrole"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("role.id"), primary_key=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='_user_role_uc'),
    )