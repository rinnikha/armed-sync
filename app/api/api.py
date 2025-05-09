from fastapi import APIRouter

from app.api.endpoints import auth, users, sync, products, reports, price_lists, order_sync_config, moysklad_entities


api_router = APIRouter()


api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])

api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(sync.router, prefix="/sync", tags=["Synchronization"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(price_lists.router, prefix="/price-lists", tags=["Price Lists"])
api_router.include_router(order_sync_config.router, prefix="/order-sync-configs", tags=["Order Sync Configs"])
api_router.include_router(moysklad_entities.router, prefix="/moysklad", tags=["MoySklad Entities"])