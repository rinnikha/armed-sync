from datetime import datetime

from moysklad_api.utils.helpers import ms_datetime_to_string
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Double
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

    id = Column(Integer, primary_key=True, autoincrement=True)
    ms1_order_id = Column(String, nullable=False)
    ms2_purchase_id = Column(String, nullable=True)
    ms1_state_href = Column(String, nullable=False)
    sync_status = Column(Enum(OrderSyncStatus), nullable=False, default=OrderSyncStatus.WAITING_FOR_CONFIRM)
    order_amount = Column(Double, nullable=False)
    modification_status = Column(Enum(OrderModificationStatus), nullable=True)
    info_msg = Column(String, nullable=True)
    error_msg = Column(String, nullable=True)

    moment = Column(DateTime, nullable=False, default=datetime.now)

    config_id = Column(Integer, ForeignKey('order_sync_config.id'), nullable=False)
    config = relationship("OrderSyncConfig", back_populates="sync_orders")

    created = Column(DateTime, nullable=False, default=datetime.now)
    modified = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            "ms1_order_id": self.ms1_order_id,
            "ms2_purchase_id": self.ms2_purchase_id if self.ms2_purchase_id else None,
            'ms1_state_href': self.ms1_state_href,
            'order_amount': self.order_amount,
            'sync_status': self.sync_status.value,
            'config': self.config.to_dict() if self.config else None,
            'modification_status': self.modification_status.value if self.modification_status else None,
            'moment': ms_datetime_to_string(self.moment),
            'info_msg': self.info_msg,
            'error_msg': self.error_msg,

            'created': ms_datetime_to_string(self.created),
            'modified': ms_datetime_to_string(self.modified),
        } 