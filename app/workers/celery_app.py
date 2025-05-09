from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from app.db.session import SessionLocal

import logging

# Initialize Celery
celery_app = Celery(
    "moysklad_sync",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configure Celery
celery_app.conf.task_routes = {
    "app.workers.celery_app.*": {"queue": "main-queue"}
}
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Configure scheduled tasks
celery_app.conf.beat_schedule = {
    "sync-orders-every-5-minutes": {
        "task": "app.workers.celery_app.sync_orders",
        "schedule": crontab(minute="*/5"),
    },
    "sync-returns-every-5-minutes": {
        "task": "app.workers.celery_app.sync_returns",
        "schedule": crontab(minute="*/5"),
    },
}


@celery_app.task
def sync_products():
    """
    Scheduled task to sync products between MS1 and MS2.
    """
    db = SessionLocal()
    try:
        # Initialize MoySklad clients
        from app.services.moysklad import get_ms1_client, get_ms2_client
        ms1_client = get_ms1_client()
        ms2_client = get_ms2_client()

        # Create sync service
        from app.services.product_sync import ProductSyncService
        sync_service = ProductSyncService(ms1_client, ms2_client, db)

        # Run sync
        result = sync_service.sync_all_products()

        # Log results
        logger = logging.getLogger("celery")
        logger.info(
            f"Product sync completed: {result['created']} created, "
            f"{result['updated']} updated, {result['failed']} failed, "
            f"{result['skipped']} skipped"
        )

        return result
    except Exception as e:
        logger.error(f"Product sync task failed: {str(e)}")
        raise
    finally:
        db.close()


@celery_app.task
def sync_orders():
    """
    Scheduled task to sync orders from MS1 to purchases in MS2.
    """
    db = SessionLocal()
    try:
        # Initialize MoySklad clients
        from app.services.moysklad import get_ms1_client, get_ms2_client
        ms1_client = get_ms1_client()
        ms2_client = get_ms2_client()

        # Create sync service
        from app.services.order_sync import OrderSyncService
        sync_service = OrderSyncService(ms1_client, ms2_client, db)

        # Run sync
        result = sync_service.sync_orders_to_purchases()

        # Log results
        import logging
        logger = logging.getLogger("celery")
        logger.info(
            f"Order sync completed: {result['created']} created, "
            f"{result['updated']} updated, {result['failed']} failed, "
            f"{result['skipped']} skipped"
        )

        return result
    except Exception as e:
        logger.error(f"Order sync task failed: {str(e)}")
        raise
    finally:
        db.close()


@celery_app.task
def sync_returns():
    """
    Scheduled task to sync returns from MS2 to MS1.
    """
    db = SessionLocal()
    try:
        # Initialize MoySklad clients
        from app.services.moysklad import get_ms1_client, get_ms2_client
        ms1_client = get_ms1_client()
        ms2_client = get_ms2_client()

        # Create sync service
        from app.services.return_sync import ReturnSyncService
        sync_service = ReturnSyncService(ms1_client, ms2_client, db)

        # Run sync
        result = sync_service.sync_returns()

        # Log results
        import logging
        logger = logging.getLogger("celery")
        logger.info(
            f"Return sync completed: {result['created']} created, "
            f"{result['updated']} updated, {result['failed']} failed, "
            f"{result['skipped']} skipped"
        )

        return result
    except Exception as e:
        logger.error(f"Return sync task failed: {str(e)}")
        raise
    finally:
        db.close()


@celery_app.task
def generate_report(report_type, parameters, user_id):
    """
    Task to generate a report.

    Args:
        report_type: Type of report to generate
        parameters: Report parameters
        user_id: User ID
    """
    db = SessionLocal()
    try:
        # Create report service
        from app.services.report import ReportService
        report_service = ReportService(db)

        # Generate report
        file_path = report_service.generate_report(
            report_type=report_type,
            parameters=parameters,
            user_id=user_id
        )

        # Log results
        import logging
        logger = logging.getLogger("celery")
        logger.info(f"Report generation completed: {report_type}, file: {file_path}")

        return {"file_path": file_path}
    except Exception as e:
        logger.error(f"Report generation task failed: {str(e)}")
        raise
    finally:
        db.close()


@celery_app.task
def generate_price_list(price_list_id, user_id):
    """
    Task to generate a price list PDF.

    Args:
        price_list_id: Price list ID
        user_id: User ID
    """
    db = SessionLocal()
    try:
        # Create price list service
        from app.services.price_list import PriceListService
        price_list_service = PriceListService(db)

        # Generate price list
        file_path = price_list_service.generate_pdf(
            price_list_id=price_list_id,
            user_id=user_id
        )

        # Log results
        import logging
        logger = logging.getLogger("celery")
        logger.info(f"Price list generation completed: {price_list_id}, file: {file_path}")

        return {"file_path": file_path}
    except Exception as e:
        logger.error(f"Price list generation task failed: {str(e)}")
        raise
    finally:
        db.close()