from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SyncRequest(BaseModel):
    run_async: bool = Field(True, description="Run the sync in the background as a Celery task")


class SyncLogBase(BaseModel):
    type: str
    status: str
    summary: Optional[Dict[str, Any]] = None
    errors: Optional[str] = None


class SyncLogResponse(SyncLogBase):
    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True