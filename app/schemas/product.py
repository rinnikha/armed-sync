from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class ProductMappingBase(BaseModel):
    ms1_id: str
    ms2_id: str
    ms1_name: Optional[str] = None
    ms2_name: Optional[str] = None
    ms1_external_code: Optional[str] = None
    ms2_external_code: Optional[str] = None


class ProductMappingCreate(ProductMappingBase):
    pass


class ProductMappingResponse(ProductMappingBase):
    id: int
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProductSyncDiff(BaseModel):
    field: str
    ms1_value: Optional[str] = None
    ms2_value: Optional[str] = None


class ProductSyncDiffResponse(BaseModel):
    product_id: str
    product_name: str
    ms1_id: str
    ms2_id: str
    differences: Dict[str, Dict[str, str]]