from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.db.session import get_db
from app.models.product_mapping import ProductMapping
from app.models.user import User
from app.schemas.product import ProductMappingCreate, ProductMappingResponse, ProductSyncDiffResponse
from app.services.moysklad import get_ms1_client, get_ms2_client
from app.services.product_sync import ProductSyncService

router = APIRouter()


@router.get("/mappings", response_model=List[ProductMappingResponse])
def read_product_mappings(
        skip: int = 0,
        limit: int = 100,
        ms1_id: Optional[str] = Query(None, description="Filter by MS1 product ID"),
        ms2_id: Optional[str] = Query(None, description="Filter by MS2 product ID"),
        product_name: Optional[str] = Query(None, description="Filter by product name (partial match)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve product mappings between MS1 and MS2.
    """
    query = db.query(ProductMapping)

    if ms1_id:
        query = query.filter(ProductMapping.ms1_id == ms1_id)
    if ms2_id:
        query = query.filter(ProductMapping.ms2_id == ms2_id)
    if product_name:
        query = query.filter(ProductMapping.ms1_name.ilike(f"%{product_name}%"))

    mappings = query.offset(skip).limit(limit).all()
    return mappings


@router.post("/mappings", response_model=ProductMappingResponse)
def create_product_mapping(
        *,
        db: Session = Depends(get_db),
        mapping_in: ProductMappingCreate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new product mapping.
    """
    # Check if mapping already exists
    existing = db.query(ProductMapping).filter(
        (ProductMapping.ms1_id == mapping_in.ms1_id) |
        (ProductMapping.ms2_id == mapping_in.ms2_id)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="A mapping for this product already exists",
        )

    # Create new mapping
    mapping = ProductMapping(
        ms1_id=mapping_in.ms1_id,
        ms2_id=mapping_in.ms2_id,
        ms1_name=mapping_in.ms1_name,
        ms2_name=mapping_in.ms2_name,
        ms1_external_code=mapping_in.ms1_external_code,
        ms2_external_code=mapping_in.ms2_external_code,
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)

    return mapping


@router.delete("/mappings/{mapping_id}", response_model=Dict[str, bool])
def delete_product_mapping(
        mapping_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a product mapping.
    """
    mapping = db.query(ProductMapping).filter(ProductMapping.id == mapping_id).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Product mapping not found")

    db.delete(mapping)
    db.commit()

    return {"success": True}


@router.get("/discrepancies", response_model=List[ProductSyncDiffResponse])
def get_product_discrepancies(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get product discrepancies between MS1 and MS2.
    """
    try:
        ms1_client = get_ms1_client()
        ms2_client = get_ms2_client()

        sync_service = ProductSyncService(ms1_client, ms2_client, db)
        discrepancies = sync_service.find_discrepancies(skip=skip, limit=limit)

        return discrepancies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get discrepancies: {str(e)}")