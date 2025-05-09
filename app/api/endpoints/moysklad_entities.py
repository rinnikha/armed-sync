from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.services.moysklad import get_ms1_client, get_ms2_client

router = APIRouter()

# MS1 Counterparties
@router.get("/ms1/counterparties", response_model=List[Dict[str, Any]])
def get_ms1_counterparties(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve counterparties from MS1.
    """
    try:
        ms1_client = get_ms1_client()
        query = ms1_client.counterparties.query()
        
        # Apply search filter if provided
        if search:
            query.search(search)
        
        # Apply pagination
        query.limit(limit).offset(skip)
        
        # Get the counterparties
        counterparties, meta = ms1_client.counterparties.find_all(query)
        
        # Format response
        result = []
        for cp in counterparties:
            result.append({
                "id": cp.id,
                "name": cp.name,
                "meta": cp.meta.href if cp.meta else None,
                "type": "counterparty"
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching MS1 counterparties: {str(e)}")

# MS2 Counterparties
@router.get("/ms2/counterparties", response_model=List[Dict[str, Any]])
def get_ms2_counterparties(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve counterparties from MS2.
    """
    try:
        ms2_client = get_ms2_client()
        query = ms2_client.counterparties.query()
        
        # Apply search filter if provided
        if search:
            query.search(search)
        
        # Apply pagination
        query.limit(limit).offset(skip)
        
        # Get the counterparties
        counterparties, meta = ms2_client.counterparties.find_all(query)
        
        # Format response
        result = []
        for cp in counterparties:
            result.append({
                "id": cp.id,
                "name": cp.name,
                "meta": cp.meta.href if cp.meta else None,
                "type": "counterparty"
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching MS2 counterparties: {str(e)}")

# MS2 Groups
@router.get("/ms2/groups", response_model=List[Dict[str, Any]])
def get_ms2_groups(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve groups from MS2.
    """
    try:
        ms2_client = get_ms2_client()
        # Note: The groups endpoint may vary based on MoySklad API structure
        # You might need to adjust this based on the actual API
        response = ms2_client.api_client.get("entity/group")
        
        groups = response.get("rows", [])
        
        # Format response
        result = []
        for group in groups:
            # Filter by search term if provided
            if search and search.lower() not in group.get("name", "").lower():
                continue
                
            result.append({
                "id": group.get("id"),
                "name": group.get("name"),
                "meta": group.get("meta", {}).get("href"),
                "type": "group"
            })
        
        # Manual pagination (if API doesn't support it)
        start = skip
        end = skip + limit
        return result[start:end]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching MS2 groups: {str(e)}")

# MS2 Organizations
@router.get("/ms2/organizations", response_model=List[Dict[str, Any]])
def get_ms2_organizations(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve organizations from MS2.
    """
    try:
        ms2_client = get_ms2_client()
        query = ms2_client.organizations.query()
        
        # Apply search filter if provided
        if search:
            query.search(search)
        
        # Apply pagination
        query.limit(limit).offset(skip)
        
        # Get the organizations
        organizations, meta = ms2_client.organizations.find_all(query)
        
        # Format response
        result = []
        for org in organizations:
            result.append({
                "id": org.id,
                "name": org.name,
                "meta": org.meta.href if org.meta else None,
                "type": "organization"
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching MS2 organizations: {str(e)}")

# MS2 Stores
@router.get("/ms2/stores", response_model=List[Dict[str, Any]])
def get_ms2_stores(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve stores from MS2.
    """
    try:
        ms2_client = get_ms2_client()
        query = ms2_client.stores.query()
        
        # Apply search filter if provided
        if search:
            query.search(search)
        
        # Apply pagination
        query.limit(limit).offset(skip)
        
        # Get the stores
        stores, meta = ms2_client.stores.find_all(query)
        
        # Format response
        result = []
        for store in stores:
            result.append({
                "id": store.id,
                "name": store.name,
                "meta": store.meta.href if store.meta else None,
                "type": "store"
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching MS2 stores: {str(e)}")

# Get specific entity by ID from MS1
@router.get("/ms1/entity/{entity_type}/{entity_id}", response_model=Dict[str, Any])
def get_ms1_entity(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve a specific entity from MS1 by ID and type.
    """
    try:
        ms1_client = get_ms1_client()
        
        if entity_type == "counterparty":
            entity = ms1_client.counterparties.find_by_id(entity_id)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported entity type: {entity_type}")
        
        # Format response
        return {
            "id": entity.id,
            "name": entity.name,
            "meta": entity.meta.href if entity.meta else None,
            "type": entity_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching MS1 entity: {str(e)}")

# Get specific entity by ID from MS2
@router.get("/ms2/entity/{entity_type}/{entity_id}", response_model=Dict[str, Any])
def get_ms2_entity(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve a specific entity from MS2 by ID and type.
    """
    try:
        ms2_client = get_ms2_client()
        
        if entity_type == "counterparty":
            entity = ms2_client.counterparties.find_by_id(entity_id)
        elif entity_type == "organization":
            entity = ms2_client.organizations.find_by_id(entity_id)
        elif entity_type == "store":
            entity = ms2_client.stores.find_by_id(entity_id)
        elif entity_type == "group":
            # Groups might require a direct API call
            response = ms2_client.api_client.get(f"entity/group/{entity_id}")
            return {
                "id": response.get("id"),
                "name": response.get("name"),
                "meta": response.get("meta", {}).get("href"),
                "type": "group"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported entity type: {entity_type}")
        
        # Format response
        return {
            "id": entity.id,
            "name": entity.name,
            "meta": entity.meta.href if entity.meta else None,
            "type": entity_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching MS2 entity: {str(e)}")