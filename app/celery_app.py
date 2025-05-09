from celery import Celery
from celery.schedules import crontab

celery_app = Celery('app')

celery_app.conf.beat_schedule = {
    'sync-pending-orders': {
        'task': 'app.tasks.order_sync.sync_pending_orders',
        'schedule': crontab(minute='*/5'),  # Run every 5 minutes
    },
    'check-order-statuses': {
        'task': 'app.tasks.order_sync.check_order_statuses',
        'schedule': crontab(minute='*/1'),  # Run every minute
    },
} 