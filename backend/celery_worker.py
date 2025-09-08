from celery import Celery
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config

def create_celery_app(config_name='development'):
    """Create and configure Celery app."""
    
    # Get configuration
    app_config = config[config_name]
    
    # Create Celery instance
    celery_app = Celery(
        'bugseek',
        broker=app_config.CELERY_BROKER_URL,
        backend=app_config.CELERY_RESULT_BACKEND,
        include=['backend.tasks']
    )
    
    # Configure Celery
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        result_expires=3600,  # 1 hour
        task_routes={
            'backend.tasks.process_log': {'queue': 'log_processing'},
            'backend.tasks.generate_report': {'queue': 'report_generation'},
            'backend.tasks.cleanup_old_files': {'queue': 'maintenance'},
        },
        worker_prefetch_multiplier=1,
        task_acks_late=True,
    )
    
    return celery_app

# Create Celery app instance
celery = create_celery_app()

if __name__ == '__main__':
    celery.start()
