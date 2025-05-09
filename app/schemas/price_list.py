from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class PriceListBase(BaseModel):
    name: str
    description: Optional[str] = None
    min_quantity: int = 1
    template_id: Optional[int] = None
    additional_settings: Optional[Dict[str, Any]] = None


class PriceListCreate(PriceListBase):
    pass


class PriceListUpdate(PriceListBase):
    name: Optional[str] = None
    min_quantity: Optional[int] = None


class PriceListResponse(PriceListBase):
    id: int
    pdf_path: Optional[str] = None
    last_generated_at: Optional[datetime] = None
    created_by_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True