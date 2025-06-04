from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.order_sync import OrderSyncService
from app.services.moysklad import get_ms1_client, get_ms2_client

from dotenv import load_dotenv
import os

dotenv_path = "../.env"
load_dotenv(dotenv_path)

db_generator = get_db()

db: Session = next(db_generator)

if __name__ == "__main__":
    ms1_client = get_ms1_client()
    ms2_client = get_ms2_client()
    order_sync_service = OrderSyncService(ms1_client, ms2_client, db)

    # order_sync_service.update_all_order_sync_status()
    order_sync_service.sync_pending_orders()