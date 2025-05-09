from sqlalchemy import Column, DateTime, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class OrderSyncConfig(Base):
    __tablename__ = 'order_sync_config'

    """Configuration for order purchase synchronization."""
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, comment="Order Sync Config Name")
    ms1_cp_meta = Column(Text, nullable=True, comment="MS1 counterparty meta data")
    ms2_organization_meta = Column(Text, nullable=True, comment="MS2 organization meta data")
    ms2_group_meta = Column(Text, nullable=True, comment="MS2 group meta data")
    ms2_store_meta = Column(Text, nullable=True, comment="MS2 store meta data")
    start_sync_datetime = Column(DateTime, nullable=False, comment="Start synchronizing orders from this datetime")
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    orders = relationship("OrderSync", back_populates="config")

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def  __repr__(self):
        return f"<OrderSyncConfig id={self.id} start_sync_datetime={self.start_sync_datetime}>"