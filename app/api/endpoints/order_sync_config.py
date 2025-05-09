from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.db.session import get_db
from app.models.order_sync_config import OrderSyncConfig
from app.models.user import User
from app.schemas.order_sync_config import (
    OrderSyncConfigCreate,
    OrderSyncConfigResponse,
    OrderSyncConfigUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[OrderSyncConfigResponse])
def read_order_sync_configs(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve order sync configurations.
    """
    configs = db.query(OrderSyncConfig).offset(skip).limit(limit).all()
    return configs


@router.post("/", response_model=OrderSyncConfigResponse)
def create_order_sync_config(
        *,
        db: Session = Depends(get_db),
        config_in: OrderSyncConfigCreate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new order sync configuration.
    """

    config = OrderSyncConfig(
        name=config_in.name,
        ms1_cp_meta=config_in.ms1_cp_meta,
        ms2_group_meta=config_in.ms2_group_meta,
        ms2_organization_meta=config_in.ms2_organization_meta,
        ms2_store_meta=config_in.ms2_store_meta,
        start_sync_datetime=config_in.start_sync_datetime,
        description=config_in.description,
        is_active=config_in.is_active,
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.get("/{config_id}", response_model=OrderSyncConfigResponse)
def read_order_sync_config(
        *,
        db: Session = Depends(get_db),
        config_id: int,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get specific order sync configuration by ID.
    """
    config = db.query(OrderSyncConfig).filter(OrderSyncConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Order sync config not found")
    return config


@router.put("/{config_id}", response_model=OrderSyncConfigResponse)
def update_order_sync_config(
        *,
        db: Session = Depends(get_db),
        config_id: int,
        config_in: OrderSyncConfigUpdate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update an order sync configuration.
    """
    config = db.query(OrderSyncConfig).filter(OrderSyncConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Order sync config not found")

    update_data = config_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.delete("/{config_id}")
def delete_order_sync_config(
        *,
        db: Session = Depends(get_db),
        config_id: int,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete an order sync configuration.
    """
    config = db.query(OrderSyncConfig).filter(OrderSyncConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Order sync config not found")

    db.delete(config)
    db.commit()
    return {"success": True}