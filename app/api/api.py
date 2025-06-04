from fastapi import APIRouter

from app.api.endpoints import auth, users, order_sync_config, moysklad_entities, order_sync


api_router = APIRouter()


api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(order_sync_config.router, prefix="/order-sync-configs", tags=["Order Sync Configs"])
api_router.include_router(moysklad_entities.router, prefix="/moysklad", tags=["MoySklad Entities"])
api_router.include_router(order_sync.router, prefix="/order-sync", tags=["Order Sync"])