from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime

from src.db.base_class import Base
from src.models.role import UserRole


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    roles = relationship("Role", secondary="userrole", back_populates="users")

    def has_permission(self, permission_name: str) -> bool:
        """
        Check if the user has a specific permission based on their roles.
        """
        # Superusers have all permissions
        if self.is_superuser:
            return True

        # Check if any of the user's roles has the permission
        for role in self.roles:
            if any(perm.name == permission_name for perm in role.permissions):
                return True

        return False