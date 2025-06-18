from celery import shared_task
from sqlalchemy.orm import Session

from src.db.session import SessionLocal
from src.services.order_sync import OrderSyncService
from src.services.moysklad import get_ms1_client, get_ms2_client

@shared_task
def sync_pending_orders():
    """Task to sync all pending orders."""
    db: Session = SessionLocal()
    try:
        service = OrderSyncService(
            ms1_client=get_ms1_client(),
            ms2_client=get_ms2_client(),
            db_session=db
        )
        service.sync_pending_orders()
    finally:
        db.close()

@shared_task
def update_order_sync_status():
    """Task to update sync status for all orders."""
    db: Session = SessionLocal()
    try:
        service = OrderSyncService(
            ms1_client=get_ms1_client(),
            ms2_client=get_ms2_client(),
            db_session=db
        )
        service.update_all_order_sync_status()
    finally:
        db.close() 