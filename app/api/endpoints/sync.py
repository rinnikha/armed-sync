from typing import Any, Dict, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.db.session import get_db
from app.models.sync_log import SyncLog
from app.models.user import User
from app.schemas.sync import SyncLogResponse, SyncRequest
from app.services.moysklad import get_ms1_client, get_ms2_client
from app.services.product_sync import ProductSyncService
from app.services.order_sync import OrderSyncService
from app.services.return_sync import ReturnSyncService
from app.workers.celery_app import (
    sync_products as celery_sync_products,
    sync_orders as celery_sync_orders,
    sync_returns as celery_sync_returns,
)

router = APIRouter()


@router.post("/products", response_model=Dict[str, Any])
async def sync_products(
        background_tasks: BackgroundTasks,
        sync_request: SyncRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Trigger a product synchronization.
    If run_async is True, the sync will run in the background as a Celery task.
    Otherwise, it will run as a FastAPI background task.
    """
    # Check permissions
    if not current_user.has_permission("sync:products"):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if sync_request.run_async:
        # Run in Celery
        task = celery_sync_products.delay()
        return {"task_id": task.id, "status": "scheduled"}
    else:
        # Run immediately in background
        try:
            ms1_client = get_ms1_client()
            ms2_client = get_ms2_client()

            sync_service = ProductSyncService(ms1_client, ms2_client, db)
            background_tasks.add_task(sync_service.sync_all_products)

            return {"status": "started", "message": "Sync started in background"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/orders", response_model=Dict[str, Any])
async def sync_orders(
        background_tasks: BackgroundTasks,
        sync_request: SyncRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Trigger an order synchronization (MS1 orders to MS2 purchases).
    If run_async is True, the sync will run in the background as a Celery task.
    Otherwise, it will run as a FastAPI background task.
    """
    # Check permissions
    if not current_user.has_permission("sync:orders"):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if sync_request.run_async:
        # Run in Celery
        task = celery_sync_orders.delay()
        return {"task_id": task.id, "status": "scheduled"}
    else:
        # Run immediately in background
        try:
            ms1_client = get_ms1_client()
            ms2_client = get_ms2_client()

            sync_service = OrderSyncService(ms1_client, ms2_client, db)
            background_tasks.add_task(sync_service.sync_orders_to_purchases)

            return {"status": "started", "message": "Order sync started in background"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/returns", response_model=Dict[str, Any])
async def sync_returns(
        background_tasks: BackgroundTasks,
        sync_request: SyncRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Trigger a return synchronization (MS2 returns to MS1 returns).
    If run_async is True, the sync will run in the background as a Celery task.
    Otherwise, it will run as a FastAPI background task.
    """
    # Check permissions
    if not current_user.has_permission("sync:returns"):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if sync_request.run_async:
        # Run in Celery
        task = celery_sync_returns.delay()
        return {"task_id": task.id, "status": "scheduled"}
    else:
        # Run immediately in background
        try:
            ms1_client = get_ms1_client()
            ms2_client = get_ms2_client()

            sync_service = ReturnSyncService(ms1_client, ms2_client, db)
            background_tasks.add_task(sync_service.sync_returns)

            return {"status": "started", "message": "Return sync started in background"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/logs", response_model=List[SyncLogResponse])
def read_sync_logs(
        skip: int = 0,
        limit: int = 100,
        sync_type: str = Query(None, description="Filter by sync type (product, order, return)"),
        status: str = Query(None, description="Filter by status (completed, partial, failed)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve sync logs.
    """
    query = db.query(SyncLog)

    if sync_type:
        query = query.filter(SyncLog.type == sync_type)
    if status:
        query = query.filter(SyncLog.status == status)

    query = query.order_by(SyncLog.started_at.desc())
    logs = query.offset(skip).limit(limit).all()

    return logs


@router.get("/logs/{log_id}", response_model=SyncLogResponse)
def read_sync_log(
        log_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific sync log by id.
    """
    log = db.query(SyncLog).filter(SyncLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Sync log not found")

    return log