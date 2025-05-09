from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum

class OrderSyncStatus(str, enum.Enum):
    SYNCED = 'synced'
    PENDING = 'pending'
    WAITING_FOR_CONFIRM = 'waiting_for_confirm'
    MODIFIED = 'modified'
    FAILED = 'failed'

class OrderModificationStatus(str, enum.Enum):
    WAITING_FOR_APPROVE = 'waiting_for_approve'
    APPROVED = 'approved'
    RESYNCED = 'resynced'

class OrderSync(Base):
    __tablename__ = 'sync_orders'

    id = Column(String, primary_key=True)
    ms1_order_id = Column(String, nullable=False)
    ms2_purchase_id = Column(String, nullable=True)
    ms1_status = Column(String, nullable=False)
    sync_status = Column(Enum(OrderSyncStatus), nullable=False, default=OrderSyncStatus.WAITING_FOR_CONFIRM)
    modification_status = Column(Enum(OrderModificationStatus), nullable=True)
    info_msg = Column(String, nullable=True)
    error_msg = Column(String, nullable=True)

    config_id = Column(Integer, ForeignKey('order_sync_config.id'), nullable=False)
    config = relationship("OrderSyncConfig", back_populates="sync_orders")

    created = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            "ms1_order_id": self.ms1_order_id,
            "ms2_purchase_id": self.ms2_purchase_id if self.ms2_purchase_id else None,
            'ms1_status': self.ms1_status,
            'sync_status': self.sync_status.value,
            'modification_status': self.modification_status.value if self.modification_status else None,
            'info_msg': self.info_msg,
            'error_msg': self.error_msg,

            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
        } 