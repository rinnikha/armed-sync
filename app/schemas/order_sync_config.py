from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrderSyncConfigBase(BaseModel):
    name: Optional[str] = None
    ms1_cp_id: Optional[str] = None
    ms2_organization_id: Optional[str] = None
    ms2_group_id: Optional[str] = None
    ms2_store_id: Optional[str] = None
    start_sync_datetime: datetime
    description: Optional[str] = None
    is_active: bool = True


class OrderSyncConfigCreate(OrderSyncConfigBase):
    pass


class OrderSyncConfigUpdate(OrderSyncConfigBase):
    start_sync_datetime: Optional[datetime] = None
    is_active: Optional[bool] = None


class OrderSyncConfigResponse(OrderSyncConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True