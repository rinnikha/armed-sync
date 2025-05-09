from typing import List, Optional

from pydantic import BaseModel


class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: int

    class Config:
        orm_mode = True


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permissions: List[str] = []


class RoleUpdate(RoleBase):
    permissions: Optional[List[str]] = None


class RoleResponse(RoleBase):
    id: int
    permissions: List[PermissionResponse] = []

    class Config:
        orm_mode = True