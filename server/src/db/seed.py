import os
import getpass
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from src.core.security import get_password_hash
from src.db.session import SessionLocal
from src.models import OrderSyncConfig
from src.models.role import Role, Permission, RolePermission
from src.models.user import User, UserRole

from src.core.config import settings


def get_admin_credentials() -> Tuple[str, str, str, str]:
    """
    Get admin credentials from environment variables or interactive input.
    Returns tuple of (username, email, password, full_name)
    """
    # Try to get from environment variables
    admin_username = settings.ADMIN_USERNAME
    admin_email = settings.ADMIN_EMAIL
    admin_password = settings.ADMIN_PASSWORD
    admin_full_name = settings.ADMIN_FULL_NAME

    # If any credential is missing, ask for all of them
    if not all([admin_username, admin_email, admin_password]):
        print("\nAdmin credentials not found in environment variables.")
        print("Please enter admin credentials:")
        
        admin_username = input("Username: ").strip()
        while not admin_username:
            print("Username cannot be empty!")
            admin_username = input("Username: ").strip()

        admin_email = input("Email: ").strip()
        while not admin_email or "@" not in admin_email:
            print("Please enter a valid email address!")
            admin_email = input("Email: ").strip()

        admin_password = getpass.getpass("Password: ")
        while not admin_password:
            print("Password cannot be empty!")
            admin_password = getpass.getpass("Password: ")

        admin_full_name = input("Full Name [Administrator]: ").strip() or "Administrator"

    return admin_username, admin_email, admin_password, admin_full_name


def seed_permissions(db: Session) -> dict:
    """Seed default permissions and return a dict of created permissions."""
    permissions = {
        "sync:products": "Synchronize products between MS1 and MS2",
        "sync:orders": "Synchronize orders from MS1 to purchases in MS2",
        "sync:returns": "Synchronize returns from MS2 to MS1",
        "reports:view": "View reports",
        "reports:generate": "Generate reports",
        "price_list:view": "View price lists",
        "price_list:create": "Create price lists",
        "price_list:generate": "Generate price list PDFs",
        "users:view": "View users",
        "users:create": "Create users",
        "users:update": "Update users",
        "users:delete": "Delete users",
    }

    created_permissions = {}
    for perm_name, perm_desc in permissions.items():
        permission = db.query(Permission).filter(Permission.name == perm_name).first()
        if not permission:
            permission = Permission(name=perm_name, description=perm_desc)
            db.add(permission)
            created_permissions[perm_name] = permission

    db.commit()
    return created_permissions


def seed_roles(db: Session, permissions: dict) -> dict:
    """Seed default roles and their permissions."""
    roles = {
        "admin": "Administrator with all permissions",
        "manager": "Manager with limited permissions",
        "viewer": "Viewer with read-only permissions",
    }

    created_roles = {}
    for role_name, role_desc in roles.items():
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name, description=role_desc)
            db.add(role)
            created_roles[role_name] = role

    db.commit()

    # Assign permissions to roles
    if created_roles:
        # Admin has all permissions
        for perm in permissions.values():
            role_perm = RolePermission(role_id=created_roles["admin"].id, permission_id=perm.id)
            db.add(role_perm)

        # Manager has all but user management permissions
        for perm_name, perm in permissions.items():
            if not perm_name.startswith("users:") or perm_name == "users:view":
                role_perm = RolePermission(role_id=created_roles["manager"].id, permission_id=perm.id)
                db.add(role_perm)

        # Viewer has only view permissions
        for perm_name, perm in permissions.items():
            if perm_name.endswith(":view"):
                role_perm = RolePermission(role_id=created_roles["viewer"].id, permission_id=perm.id)
                db.add(role_perm)

        db.commit()

    return created_roles


def seed_order_sync_configs(db:Session) -> None:
    surx_config = OrderSyncConfig(
        name="Сурхандарья дилер",
        ms1_cp_id="2aaf3539-c9aa-11ee-0a80-14bd001cd277",
        ms2_organization_id="ede4cf84-726e-11ef-0a80-13bb002099d9",
        ms2_group_id="9e1a85f9-da15-11ef-0a80-03cd0002ff84",
        ms2_store_id="cb75c159-da47-11ef-0a80-06a3000bf6d5",
        start_sync_datetime=datetime(2025, 5, 14, 00, 00, 0),
        description="Test",
        is_active=True
    )

    xorezm_config = OrderSyncConfig(
        name="Хорезм дилер",
        ms1_cp_id="b1af39d5-3df4-11ef-0a80-04a2001561ed",
        ms2_organization_id="ede4cf84-726e-11ef-0a80-13bb002099d9",
        ms2_group_id="8d6c723f-dc14-11ef-0a80-040f0022fd53",
        ms2_store_id="9a936901-dc14-11ef-0a80-10cd0022a9b0",
        start_sync_datetime=datetime(2025, 5, 14, 00, 00, 0),
        description="Test",
        is_active=True
    )

    db.add(surx_config)
    db.add(xorezm_config)
    db.commit()


def seed_admin_user(db: Session, roles: dict) -> None:
    """Seed default admin user if it doesn't exist."""
    admin_username, admin_email, admin_password, admin_full_name = get_admin_credentials()
    
    admin_user = db.query(User).filter(User.email == admin_email).first()
    if not admin_user:
        admin_user = User(
            username=admin_username,
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            full_name=admin_full_name,
            is_active=True,
            is_superuser=True,
        )
        db.add(admin_user)
        db.commit()

        # Assign admin role to admin user
        if "admin" in roles:
            user_role = UserRole(user_id=admin_user.id, role_id=roles["admin"].id)
            db.add(user_role)
            db.commit()
            print(f"\nAdmin user '{admin_username}' created successfully!")
    else:
        print(f"\nAdmin user '{admin_username}' already exists.")


def seed_db() -> None:
    """Main function to seed the database with initial data."""
    print("Starting database seeding...")
    db = SessionLocal()
    try:
        print("Seeding order sync configs...")
        seed_order_sync_configs(db)
        print("Seeding permissions...")
        permissions = seed_permissions(db)
        print("Seeding roles...")
        roles = seed_roles(db, permissions)
        print("Seeding admin user...")
        seed_admin_user(db, roles)
        print("\nDatabase seeding completed successfully!")
    except Exception as e:
        print(f"\nError during seeding: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()