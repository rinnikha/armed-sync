from celery import shared_task
from app.db.session import SessionLocal
from app.models.order import Order, OrderSyncStatus
from app.models.order_sync_config import OrderSyncConfig
from app.services.order_sync import OrderSyncService

@shared_task
def sync_pending_orders():
    """
    Celery task to sync all pending orders.
    """
    db = SessionLocal()
    try:
        # Get all pending orders
        orders = db.query(Order).filter(Order.sync_status == OrderSyncStatus.PENDING).all()
        
        # Get active sync configurations
        configs = {
            config.id: config
            for config in db.query(OrderSyncConfig).filter(OrderSyncConfig.is_active == True).all()
        }
        
        # Initialize sync service
        sync_service = OrderSyncService(db)
        
        # Process each order
        for order in orders:
            if order.config_id not in configs:
                continue
                
            try:
                sync_service.sync_order(order, configs[order.config_id])
            except Exception as e:
                # Log error and continue with next order
                print(f"Error syncing order {order.id}: {str(e)}")
                continue
                
    finally:
        db.close()

@shared_task
def check_order_statuses():
    """
    Celery task to check status of orders.
    """
    db = SessionLocal()
    try:
        # Get orders that need status check
        orders = db.query(Order).filter(
            Order.sync_status.in_([OrderSyncStatus.WAITING_FOR_CONFIRM, OrderSyncStatus.PENDING])
        ).all()
        
        # Initialize sync service
        sync_service = OrderSyncService(db)
        
        # Check each order
        for order in orders:
            try:
                sync_service.check_order_status(order)
            except Exception as e:
                # Log error and continue with next order
                print(f"Error checking order status {order.id}: {str(e)}")
                continue
                
        # Check for modified orders
        sync_service.check_modified_orders()
        
    finally:
        db.close() 