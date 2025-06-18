"""
Service modules for MoySklad Sync System.
"""

# Import all services to make them available when importing from the services package
from src.services.moysklad import get_ms1_client, get_ms2_client
from src.services.order_sync import OrderSyncService