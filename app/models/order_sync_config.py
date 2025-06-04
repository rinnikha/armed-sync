from moysklad_api.utils.helpers import ms_datetime_to_string
from sqlalchemy import Column, DateTime, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class OrderSyncConfig(Base):
    __tablename__ = 'order_sync_config'

    """Configuration for order purchase synchronization."""
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, comment="Order Sync Config Name")
    ms1_cp_id = Column(String, nullable=True, comment="MS1 counterparty meta data")
    ms2_organization_id = Column(String, nullable=True, comment="MS2 organization meta data")
    ms2_group_id = Column(String, nullable=True, comment="MS2 group meta data")
    ms2_store_id = Column(String, nullable=True, comment="MS2 store meta data")
    start_sync_datetime = Column(DateTime, nullable=False, comment="Start synchronizing orders from this datetime")
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    sync_orders = relationship("OrderSync", back_populates="config")

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
         return {
            'id': self.id,
            'name': self.name,
            'ms1_cp_id': self.ms1_cp_id,
            'ms2_organization_id': self.ms2_organization_id,
            'ms2_group_id': self.ms2_group_id,
            'ms2_store_id': self.ms2_store_id,
            'start_sync_datetime': ms_datetime_to_string(self.start_sync_datetime),
            'description': self.description,
            'is_active': self.is_active,

            'created': ms_datetime_to_string(self.created_at),
            'modified': ms_datetime_to_string(self.updated_at),
        }

    def  __repr__(self):
        return f"<OrderSyncConfig id={self.id} start_sync_datetime={self.start_sync_datetime}>"
