from typing import Any, Dict, List

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.db.session import get_db
from app.models.price_list import PriceList
from app.models.user import User
from app.schemas.price_list import PriceListCreate, PriceListResponse, PriceListUpdate
from app.services.price_list import PriceListService
from app.workers.celery_app import generate_price_list as celery_generate_price_list

router = APIRouter()


@router.get("/", response_model=List[PriceListResponse])
def read_price_lists(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve price lists.
    """
    # Regular users can only see their own price lists
    query = db.query(PriceList)
    if not current_user.is_superuser:
        query = query.filter(PriceList.created_by_id == current_user.id)

    price_lists = query.order_by(PriceList.created_at.desc()).offset(skip).limit(limit).all()
    return price_lists


@router.post("/", response_model=PriceListResponse)
def create_price_list(
        *,
        db: Session = Depends(get_db),
        price_list_in: PriceListCreate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new price list configuration.
    """
    # Check permissions
    if not current_user.has_permission("price_list:create"):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    price_list = PriceList(
        name=price_list_in.name,
        description=price_list_in.description,
        min_quantity=price_list_in.min_quantity,
        template_id=price_list_in.template_id,
        additional_settings=price_list_in.additional_settings,
        created_by_id=current_user.id
    )
    db.add(price_list)
    db.commit()
    db.refresh(price_list)

    return price_list


@router.get("/{price_list_id}", response_model=PriceListResponse)
def read_price_list(
        price_list_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific price list by id.
    """
    price_list = db.query(PriceList).filter(PriceList.id == price_list_id).first()
    if not price_list:
        raise HTTPException(status_code=404, detail="Price list not found")

    # Check permissions
    if not current_user.is_superuser and price_list.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return price_list


@router.put("/{price_list_id}", response_model=PriceListResponse)
def update_price_list(
        *,
        db: Session = Depends(get_db),
        price_list_id: int,
        price_list_in: PriceListUpdate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a price list.
    """
    price_list = db.query(PriceList).filter(PriceList.id == price_list_id).first()
    if not price_list:
        raise HTTPException(status_code=404, detail="Price list not found")

    # Check permissions
    if not current_user.is_superuser and price_list.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Update fields
    if price_list_in.name is not None:
        price_list.name = price_list_in.name
    if price_list_in.description is not None:
        price_list.description = price_list_in.description
    if price_list_in.min_quantity is not None:
        price_list.min_quantity = price_list_in.min_quantity
    if price_list_in.template_id is not None:
        price_list.template_id = price_list_in.template_id
    if price_list_in.additional_settings is not None:
        price_list.additional_settings = price_list_in.additional_settings

    db.add(price_list)
    db.commit()
    db.refresh(price_list)

    return price_list


@router.delete("/{price_list_id}", response_model=Dict[str, bool])
def delete_price_list(
        price_list_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a price list.
    """
    price_list = db.query(PriceList).filter(PriceList.id == price_list_id).first()
    if not price_list:
        raise HTTPException(status_code=404, detail="Price list not found")

    # Check permissions
    if not current_user.is_superuser and price_list.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(price_list)
    db.commit()

    return {"success": True}


@router.post("/{price_list_id}/generate", response_model=Dict[str, Any])
async def generate_price_list_pdf(
        background_tasks: BackgroundTasks,
        price_list_id: int,
        run_async: bool = Form(False),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Generate a PDF price list.
    If run_async is True, the generation will run in the background as a Celery task.
    Otherwise, it will run as a FastAPI background task.
    """
    price_list = db.query(PriceList).filter(PriceList.id == price_list_id).first()
    if not price_list:
        raise HTTPException(status_code=404, detail="Price list not found")

    # Check permissions
    if not current_user.has_permission("price_list:generate"):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if run_async:
        # Run in Celery
        task = celery_generate_price_list.delay(
            price_list_id=price_list_id,
            user_id=current_user.id
        )
        return {"task_id": task.id, "status": "scheduled"}
    else:
        # Run immediately in background
        try:
            price_list_service = PriceListService(db)
            background_tasks.add_task(
                price_list_service.generate_pdf,
                price_list_id=price_list_id,
                user_id=current_user.id
            )

            return {"status": "started", "message": "Price list generation started in background"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Price list generation failed: {str(e)}")


@router.get("/{price_list_id}/download")
def download_price_list(
        price_list_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Download a price list PDF.
    """
    import os
    price_list = db.query(PriceList).filter(PriceList.id == price_list_id).first()
    if not price_list:
        raise HTTPException(status_code=404, detail="Price list not found")

    # Check if pdf exists
    if not price_list.pdf_path or not os.path.exists(price_list.pdf_path):
        raise HTTPException(status_code=404, detail="Price list PDF not found")

    return FileResponse(
        path=price_list.pdf_path,
        filename=f"{price_list.name}.pdf",
        media_type="application/pdf"
    )