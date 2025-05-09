from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ProductMapping(Base):
    id = Column(Integer, primary_key=True, index=True)
    ms1_id = Column(String, nullable=False, index=True, unique=True)
    ms2_id = Column(String, nullable=False, index=True, unique=True)
    ms1_name = Column(String, nullable=True)
    ms2_name = Column(String, nullable=True)
    ms1_external_code = Column(String, nullable=True)
    ms2_external_code = Column(String, nullable=True)
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())