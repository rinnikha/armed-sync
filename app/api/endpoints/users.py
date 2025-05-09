from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_superuser, get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def read_users(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/me", response_model=UserResponse)
def read_user_me(
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_user_me(
        *,
        db: Session = Depends(get_db),
        full_name: str = Body(None),
        email: str = Body(None),
        password: str = Body(None),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update current user.
    """
    current_user_data = UserUpdate(
        full_name=full_name or current_user.full_name,
        email=email or current_user.email,
        password=password,
    )

    # Check if email is being changed and already exists
    if current_user_data.email != current_user.email:
        user_with_email = db.query(User).filter(User.email == current_user_data.email).first()
        if user_with_email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )

    # Update user
    if current_user_data.full_name is not None:
        current_user.full_name = current_user_data.full_name
    if current_user_data.email is not None:
        current_user.email = current_user_data.email
    if current_user_data.password is not None:
        from app.core.security import get_password_hash
        current_user.hashed_password = get_password_hash(current_user_data.password)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def read_user_by_id(
        user_id: int = Path(..., ge=1),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
        *,
        db: Session = Depends(get_db),
        user_id: int = Path(..., ge=1),
        user_in: UserUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    # Update user
    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.password is not None:
        from app.core.security import get_password_hash
        user.hashed_password = get_password_hash(user_in.password)
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    if user_in.is_superuser is not None:
        user.is_superuser = user_in.is_superuser

    db.add(user)
    db.commit()
    db.refresh(user)

    return user