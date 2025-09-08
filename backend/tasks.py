from celery import current_task
import time
import os
from datetime import datetime, timedelta

from backend.celery_worker import celery
from backend.services import ErrorLogService, NLPService, GenAIService

@celery.task(bind=True)
def process_log(self, cr_id, log_content):
    """
    Background task to process uploaded log files.
    
    Args:
        cr_id: Error log ID
        log_content: Content of the log file
    """
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 3, 'status': 'Starting log processing...'}
        )
        
        # Step 1: Generate NLP embeddings (placeholder)
        self.update_state(
            state='PROGRESS',
            meta={'current': 1, 'total': 3, 'status': 'Generating embeddings...'}
        )
        time.sleep(2)  # Simulate processing time
        
        embeddings_result = NLPService.generate_embeddings(log_content)
        
        # Step 2: Update error log with embeddings
        self.update_state(
            state='PROGRESS',
            meta={'current': 2, 'total': 3, 'status': 'Updating database...'}
        )
        time.sleep(1)
        
        if embeddings_result['success']:
            ErrorLogService.update_error_log(cr_id, {
                'Embedding': embeddings_result['embeddings']
            })
        
        # Step 3: Find similar logs (placeholder)
        self.update_state(
            state='PROGRESS',
            meta={'current': 3, 'total': 3, 'status': 'Finding similar logs...'}
        )
        time.sleep(1)
        
        similar_logs = NLPService.find_similar_logs(embeddings_result.get('embeddings', []))
        
        return {
            'status': 'completed',
            'cr_id': cr_id,
            'embeddings_generated': embeddings_result['success'],
            'similar_logs_found': len(similar_logs.get('similar_logs', [])),
            'message': 'Log processing completed successfully'
        }
        
    except Exception as exc:
        self.update_state(
            state='FAILURE',
            meta={'error': str(exc), 'status': 'Processing failed'}
        )
        raise exc

@celery.task(bind=True)
def generate_report(self, cr_id):
    """
    Background task to generate comprehensive report for an error log.
    
    Args:
        cr_id: Error log ID
    """
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 4, 'status': 'Starting report generation...'}
        )
        
        # Step 1: Get error log details
        self.update_state(
            state='PROGRESS',
            meta={'current': 1, 'total': 4, 'status': 'Fetching log details...'}
        )
        time.sleep(1)
        
        log_result = ErrorLogService.get_error_log_by_id(cr_id)
        if not log_result['success']:
            raise Exception(f"Error log not found: {cr_id}")
        
        error_log = log_result['data']
        
        # Step 2: Generate AI summary
        self.update_state(
            state='PROGRESS',
            meta={'current': 2, 'total': 4, 'status': 'Generating AI summary...'}
        )
        time.sleep(2)
        
        summary_result = GenAIService.generate_summary(error_log.get('LogContent', ''))
        
        # Step 3: Generate solution suggestions
        self.update_state(
            state='PROGRESS',
            meta={'current': 3, 'total': 4, 'status': 'Generating solutions...'}
        )
        time.sleep(2)
        
        solutions_result = GenAIService.suggest_solutions(error_log)
        
        # Step 4: Find similar logs
        self.update_state(
            state='PROGRESS',
            meta={'current': 4, 'total': 4, 'status': 'Finding similar logs...'}
        )
        time.sleep(1)
        
        similar_result = NLPService.find_similar_logs(error_log.get('Embedding', []))
        
        return {
            'status': 'completed',
            'cr_id': cr_id,
            'report': {
                'log_details': error_log,
                'ai_summary': summary_result if summary_result['success'] else None,
                'suggested_solutions': solutions_result if solutions_result['success'] else None,
                'similar_logs': similar_result if similar_result['success'] else None
            },
            'message': 'Report generation completed successfully'
        }
        
    except Exception as exc:
        self.update_state(
            state='FAILURE',
            meta={'error': str(exc), 'status': 'Report generation failed'}
        )
        raise exc

@celery.task
def cleanup_old_files():
    """
    Scheduled task to clean up old uploaded files.
    """
    try:
        upload_folder = 'uploads'
        cutoff_date = datetime.now() - timedelta(days=30)  # Remove files older than 30 days
        
        if not os.path.exists(upload_folder):
            return {'status': 'completed', 'files_removed': 0, 'message': 'Upload folder not found'}
        
        files_removed = 0
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_mtime < cutoff_date:
                    os.remove(file_path)
                    files_removed += 1
        
        return {
            'status': 'completed',
            'files_removed': files_removed,
            'cutoff_date': cutoff_date.isoformat(),
            'message': f'Cleanup completed: {files_removed} files removed'
        }
        
    except Exception as exc:
        return {
            'status': 'failed',
            'error': str(exc),
            'message': 'Cleanup task failed'
        }

@celery.task(bind=True)
def process_bulk_logs(self, log_data_list):
    """
    Background task to process multiple log files in bulk.
    
    Args:
        log_data_list: List of log data dictionaries
    """
    try:
        total_logs = len(log_data_list)
        processed_logs = []
        failed_logs = []
        
        for idx, log_data in enumerate(log_data_list):
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': idx,
                    'total': total_logs,
                    'status': f'Processing log {idx + 1} of {total_logs}...'
                }
            )
            
            try:
                # Create error log
                result = ErrorLogService.create_error_log(
                    log_data.get('metadata', {}),
                    log_data.get('content', '')
                )
                
                if result['success']:
                    processed_logs.append(result['data']['Cr_ID'])
                else:
                    failed_logs.append({
                        'data': log_data,
                        'error': result['message']
                    })
                    
            except Exception as e:
                failed_logs.append({
                    'data': log_data,
                    'error': str(e)
                })
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.1)
        
        return {
            'status': 'completed',
            'total_logs': total_logs,
            'processed_count': len(processed_logs),
            'failed_count': len(failed_logs),
            'processed_ids': processed_logs,
            'failed_logs': failed_logs,
            'message': f'Bulk processing completed: {len(processed_logs)} processed, {len(failed_logs)} failed'
        }
        
    except Exception as exc:
        self.update_state(
            state='FAILURE',
            meta={'error': str(exc), 'status': 'Bulk processing failed'}
        )
        raise exc

@celery.task
def health_check():
    """
    Task to check system health and connectivity.
    """
    try:
        # Check database connectivity
        stats_result = ErrorLogService.get_statistics()
        
        # Check if we can generate embeddings
        nlp_result = NLPService.generate_embeddings("test content")
        
        # Check if we can generate summaries
        genai_result = GenAIService.generate_summary("test log content")
        
        return {
            'status': 'healthy',
            'database_connected': stats_result['success'],
            'nlp_service_available': nlp_result['success'],
            'genai_service_available': genai_result['success'],
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Health check completed successfully'
        }
        
    except Exception as exc:
        return {
            'status': 'unhealthy',
            'error': str(exc),
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Health check failed'
        }
