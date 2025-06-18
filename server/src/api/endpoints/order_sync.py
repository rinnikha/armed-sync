from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.api import deps
from src.services.order_sync import OrderSyncService
from src.services.moysklad import get_ms1_client, get_ms2_client
from src.models.order_sync import OrderSync, OrderSyncStatus, OrderModificationStatus

router = APIRouter()

@router.get("/orders")
def get_orders(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sync_status: Optional[OrderSyncStatus] = None,
    modification_status: Optional[OrderModificationStatus] = None,
    config_id: Optional[int] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    search: Optional[str] = None
):
    """
    Get order sync entities with pagination and filters.
    """
    query = db.query(OrderSync)

    # Apply filters
    if sync_status:
        query = query.filter(OrderSync.sync_status == sync_status)
    if config_id:
        query = query.filter(OrderSync.config_id == config_id)
    if created_after:
        query = query.filter(OrderSync.created >= created_after)
    if created_before:
        query = query.filter(OrderSync.created <= created_before)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (OrderSync.ms1_order_id.ilike(search_term)) |
            (OrderSync.ms2_purchase_id.ilike(search_term)) |
            (OrderSync.info_msg.ilike(search_term)) |
            (OrderSync.error_msg.ilike(search_term))
        )

    # Get total count before pagination
    total = query.count()

    # Apply pagination
    orders = query.order_by(OrderSync.created.desc()).offset(skip).limit(limit).all()

    return {
        "items": [order.to_dict() for order in orders],
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/orders/{order_id}", response_model=dict)
def get_order(
    order_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """
    Get a specific order sync entity by ID.
    """
    order = db.query(OrderSync).filter(OrderSync.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order.to_dict()

@router.post("/orders/{order_id}/resync")
def resync_order(
    order_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """
    Resync a specific order using sync_single_order method.
    """
    order = db.query(OrderSync).filter(OrderSync.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        service = OrderSyncService(
            ms1_client=get_ms1_client(),
            ms2_client=get_ms2_client(),
            db_session=db
        )
        updated_order = service.sync_single_order(order)
        return {
            "message": "Order resynced successfully",
            "order": updated_order.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-statuses")
def update_order_sync_statuses(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """
    Manually trigger update of order sync statuses.
    """
    try:
        service = OrderSyncService(
            ms1_client=get_ms1_client(),
            ms2_client=get_ms2_client(),
            db_session=db
        )
        service.update_all_order_sync_status()
        return {"message": "Order sync statuses updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-pending")
def sync_pending_orders(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """
    Manually trigger sync of pending orders.
    """
    try:
        service = OrderSyncService(
            ms1_client=get_ms1_client(),
            ms2_client=get_ms2_client(),
            db_session=db
        )
        service.sync_pending_orders()
        return {"message": "Pending orders synced successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-all")
def sync_all_orders(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """
    Manually trigger full sync process:
    1. Update order sync statuses
    2. Sync pending orders
    """
    try:
        service = OrderSyncService(
            ms1_client=get_ms1_client(),
            ms2_client=get_ms2_client(),
            db_session=db
        )
        # First update statuses
        service.update_all_order_sync_status()
        # Then sync pending orders
        service.sync_pending_orders()
        return {"message": "Full sync process completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 