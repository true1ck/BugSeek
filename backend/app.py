from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from flask_restx import Api, Resource, fields, reqparse
from werkzeug.datastructures import FileStorage
from sqlalchemy import text
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config
from backend.models import db, create_tables
from backend.services import ErrorLogService, FileService, NLPService, GenAIService

def create_app(config_name='development'):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Initialize Flask-RESTx with Swagger UI
    api = Api(
        app, 
        version='1.0', 
        title='BugSeek API',
        description='Error Log Management System API with NLP and GenAI capabilities',
        doc='/api/docs/',
        prefix='/api/v1'
    )
    
    # Create database tables
    with app.app_context():
        create_tables(app)
    
    # Define API models for Swagger documentation
    error_log_model = api.model('ErrorLog', {
        'Cr_ID': fields.String(description='Unique change request ID', example='cr_20250908_1234567890'),
        'TeamName': fields.String(required=True, description='Team responsible for the error', example='Frontend'),
        'Module': fields.String(required=True, description='System module where error occurred', example='Authentication'),
        'Description': fields.String(required=True, description='Brief description of the error', example='Login timeout after 30 seconds'),
        'Owner': fields.String(required=True, description='Email of the person responsible', example='john.doe@company.com'),
        'LogFileName': fields.String(description='Name of the uploaded log file', example='auth_error.log'),
        'FileSize': fields.Integer(description='Size of the log file in bytes', example=2048),
        'LogContent': fields.String(description='Content of the log file', example='2025-09-08 15:30:00 ERROR: Connection timeout...'),
        'SolutionPossible': fields.Boolean(default=False, description='Whether a solution is available', example=True),
        'CreatedAt': fields.DateTime(description='Timestamp when log was uploaded', example='2025-09-08T15:30:00Z'),
        'UpdatedAt': fields.DateTime(description='Timestamp when log was last updated', example='2025-09-08T15:35:00Z'),
        'Embedding': fields.List(fields.Float, description='NLP embeddings for similarity search')
    })
    
    ai_summary_model = api.model('AISummary', {
        'summary': fields.String(description='AI-generated summary of the error', example='Authentication timeout detected in login module. Likely caused by database connection issues.'),
        'confidence': fields.Integer(description='Confidence score (0-100)', example=85),
        'keywords': fields.List(fields.String, description='Key terms extracted from the log', example=['timeout', 'authentication', 'database']),
        'severity': fields.String(description='Estimated severity level', enum=['low', 'medium', 'high', 'critical'], example='high')
    })
    
    solution_model = api.model('Solution', {
        'id': fields.Integer(description='Solution ID', example=1),
        'description': fields.String(description='Detailed solution description', example='Increase the database connection timeout from 30 to 60 seconds in config.yml'),
        'confidence': fields.Integer(description='Confidence score for this solution (0-100)', example=90),
        'steps': fields.List(fields.String, description='Step-by-step instructions'),
        'category': fields.String(description='Solution category', enum=['configuration', 'code', 'infrastructure', 'data'], example='configuration'),
        'estimated_time': fields.String(description='Estimated time to implement', example='15 minutes'),
        'risk_level': fields.String(description='Risk level of implementing this solution', enum=['low', 'medium', 'high'], example='low')
    })
    
    suggested_solutions_model = api.model('SuggestedSolutions', {
        'solutions': fields.List(fields.Nested(solution_model), description='List of suggested solutions'),
        'total_count': fields.Integer(description='Total number of solutions found', example=3),
        'best_match': fields.Nested(solution_model, description='Highest confidence solution')
    })
    
    similar_logs_model = api.model('SimilarLogs', {
        'logs': fields.List(fields.Nested(error_log_model), description='List of similar error logs'),
        'similarity_threshold': fields.Float(description='Minimum similarity score used', example=0.8),
        'total_found': fields.Integer(description='Total number of similar logs found', example=5)
    })
    
    report_model = api.model('ErrorReport', {
        'log_details': fields.Nested(error_log_model, description='Detailed error log information'),
        'ai_summary': fields.Nested(ai_summary_model, description='AI-generated analysis summary'),
        'suggested_solutions': fields.Nested(suggested_solutions_model, description='AI-suggested solutions'),
        'similar_logs': fields.Nested(similar_logs_model, description='Similar error logs for reference')
    })
    
    pagination_model = api.model('Pagination', {
        'page': fields.Integer(description='Current page number', example=1),
        'per_page': fields.Integer(description='Items per page', example=20),
        'total_pages': fields.Integer(description='Total number of pages', example=5),
        'total_items': fields.Integer(description='Total number of items', example=92),
        'has_next': fields.Boolean(description='Whether there are more pages', example=True),
        'has_prev': fields.Boolean(description='Whether there are previous pages', example=False)
    })
    
    logs_response_model = api.model('LogsResponse', {
        'logs': fields.List(fields.Nested(error_log_model), description='List of error logs'),
        'pagination': fields.Nested(pagination_model, description='Pagination information')
    })
    
    statistics_model = api.model('Statistics', {
        'total_logs': fields.Integer(description='Total number of error logs', example=245),
        'resolved_count': fields.Integer(description='Number of resolved errors', example=189),
        'pending_count': fields.Integer(description='Number of pending errors', example=56),
        'teams_count': fields.Integer(description='Number of active teams', example=8),
        'modules_count': fields.Integer(description='Number of different modules', example=12),
        'avg_file_size': fields.Float(description='Average file size in KB', example=15.7),
        'latest_upload': fields.DateTime(description='Timestamp of latest upload', example='2025-09-08T15:30:00Z'),
        'top_teams': fields.List(fields.Raw, description='Teams with most errors'),
        'top_modules': fields.List(fields.Raw, description='Modules with most errors')
    })
    
    health_response_model = api.model('HealthResponse', {
        'status': fields.String(description='System health status', enum=['healthy', 'unhealthy'], example='healthy'),
        'database': fields.String(description='Database connection status', example='connected'),
        'version': fields.String(description='API version', example='1.0.0'),
        'uptime': fields.String(description='System uptime', example='2h 15m'),
        'statistics': fields.Nested(statistics_model, description='Basic system statistics')
    })
    
    success_response_model = api.model('SuccessResponse', {
        'success': fields.Boolean(description='Whether the request was successful', example=True),
        'message': fields.String(description='Success message', example='Operation completed successfully'),
        'data': fields.Raw(description='Response data (varies by endpoint)')
    })
    
    error_response_model = api.model('ErrorResponse', {
        'success': fields.Boolean(description='Whether the request was successful', example=False),
        'message': fields.String(description='Error message', example='Validation failed: TeamName is required'),
        'error_code': fields.String(description='Machine-readable error code', example='VALIDATION_ERROR'),
        'details': fields.Raw(description='Additional error details', example={'field': 'TeamName', 'issue': 'Required field missing'})
    })
    
    upload_parser = reqparse.RequestParser()
    upload_parser.add_argument('file', location='files', type=FileStorage, required=True, help='Log file to upload')
    upload_parser.add_argument('TeamName', required=True, help='Team responsible for the error')
    upload_parser.add_argument('Module', required=True, help='System module where error occurred')
    upload_parser.add_argument('Description', required=True, help='Brief description of the error')
    upload_parser.add_argument('Owner', required=True, help='Email of the person responsible for fixing')
    upload_parser.add_argument('SolutionPossible', type=bool, default=False, help='Whether a solution is available')
    
    # API Namespaces
    logs_ns = api.namespace('logs', description='Error logs operations')
    reports_ns = api.namespace('reports', description='Report operations')
    automation_ns = api.namespace('automation', description='Automation endpoints')
    health_ns = api.namespace('health', description='Health check')
    
    @logs_ns.route('/upload')
    class LogUpload(Resource):
        @logs_ns.expect(upload_parser)
        @logs_ns.doc('upload_log', 
                    description='Upload a new error log file with metadata. The file will be processed and AI analysis will be generated.',
                    security=None)
        @logs_ns.response(201, 'Log uploaded successfully', success_response_model)
        @logs_ns.response(400, 'Bad request - validation error', error_response_model)
        @logs_ns.response(500, 'Internal server error', error_response_model)
        def post(self):
            """Upload a new error log with metadata and generate AI analysis"""
            try:
                args = upload_parser.parse_args()
                
                # Save uploaded file
                file_result = FileService.save_uploaded_file(
                    args['file'], 
                    app.config['UPLOAD_FOLDER']
                )
                
                if not file_result['success']:
                    return {'success': False, 'message': file_result['message']}, 400
                
                # Prepare data for error log creation
                log_data = {
                    'TeamName': args['TeamName'],
                    'Module': args['Module'],
                    'Description': args['Description'],
                    'Owner': args['Owner'],
                    'ErrorName': 'Auto-generated',  # Default value since ErrorName is kept in DB only
                    'LogFileName': file_result['filename'],
                    'SolutionPossible': args.get('SolutionPossible', False)
                }
                
                # Create error log entry
                result = ErrorLogService.create_error_log(
                    log_data, 
                    file_result['content']
                )
                
                if result['success']:
                    # Generate placeholder embeddings
                    nlp_result = NLPService.generate_embeddings(file_result['content'])
                    if nlp_result['success']:
                        # Update log with embeddings
                        ErrorLogService.update_error_log(
                            result['data']['Cr_ID'],
                            {'Embedding': nlp_result['embeddings']}
                        )
                    
                    report_url = f"/api/v1/reports/{result['data']['Cr_ID']}"
                    return {
                        'success': True,
                        'message': 'Log uploaded successfully',
                        'report_url': report_url,
                        'Cr_ID': result['data']['Cr_ID']
                    }, 201
                else:
                    return {'success': False, 'message': result['message']}, 400
                    
            except Exception as e:
                return {'success': False, 'message': str(e)}, 500
    
    @logs_ns.route('/')
    class LogList(Resource):
        @logs_ns.doc('list_logs',
                    description='Get a paginated list of error logs with optional filtering by team, module, owner, etc.')
        @logs_ns.param('page', 'Page number for pagination', type='integer', default=1)
        @logs_ns.param('per_page', 'Number of items per page (max 100)', type='integer', default=20)
        @logs_ns.param('TeamName', 'Filter by team name (exact match)')
        @logs_ns.param('Module', 'Filter by system module (exact match)')
        @logs_ns.param('Owner', 'Filter by owner email (exact match)')
        @logs_ns.param('SolutionPossible', 'Filter by solution availability', type='boolean')
        @logs_ns.param('search', 'Search in log content, descriptions, and filenames')
        @logs_ns.param('date_from', 'Filter logs created after this date (YYYY-MM-DD)')
        @logs_ns.param('date_to', 'Filter logs created before this date (YYYY-MM-DD)')
        @logs_ns.response(200, 'Success', success_response_model)
        @logs_ns.response(400, 'Bad request - invalid parameters', error_response_model)
        def get(self):
            """Get paginated list of error logs with advanced filtering options"""
            try:
                # Parse query parameters
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 20, type=int)
                
                filters = {
                    'TeamName': request.args.get('TeamName'),
                    'Module': request.args.get('Module'),
                    'ErrorName': request.args.get('ErrorName'),
                    'Owner': request.args.get('Owner'),
                    'search': request.args.get('search')
                }
                
                # Handle boolean filter
                solution_possible = request.args.get('SolutionPossible')
                if solution_possible is not None:
                    filters['SolutionPossible'] = solution_possible.lower() == 'true'
                
                # Remove None values from filters
                filters = {k: v for k, v in filters.items() if v is not None}
                
                result = ErrorLogService.get_error_logs(filters, page, per_page)
                
                if result['success']:
                    # Normalize pagination keys for frontend templates
                    pagination = result.get('pagination', {})
                    normalized_pagination = {
                        'page': pagination.get('page'),
                        'per_page': pagination.get('per_page'),
                        'total_pages': pagination.get('pages'),
                        'total_items': pagination.get('total'),
                        'has_next': pagination.get('has_next'),
                        'has_prev': pagination.get('has_prev')
                    }

                    return {
                        'success': True,
                        'data': {
                            'logs': result.get('data', []),
                            'pagination': normalized_pagination
                        }
                    }, 200
                else:
                    return {'success': False, 'message': result['message']}, 400
                    
            except Exception as e:
                return {'success': False, 'message': str(e)}, 500
    
    @reports_ns.route('/<string:cr_id>')
    class LogReport(Resource):
        @reports_ns.doc('get_report',
                       description='Get comprehensive report for a specific error log including AI analysis, suggested solutions, and similar logs',
                       params={'cr_id': 'Unique Change Request ID for the error log'})
        @reports_ns.response(200, 'Report retrieved successfully', success_response_model)
        @reports_ns.response(404, 'Error log not found', error_response_model)
        @reports_ns.response(500, 'Internal server error', error_response_model)
        def get(self, cr_id):
            """Get detailed report with AI analysis for a specific error log"""
            try:
                result = ErrorLogService.get_error_log_by_id(cr_id)
                
                if result['success']:
                    error_log = result['data']
                    
                    # Generate AI summary (placeholder)
                    summary_result = GenAIService.generate_summary(error_log.get('LogContent', ''))
                    
                    # Generate solution suggestions (placeholder)
                    solutions_result = GenAIService.suggest_solutions(error_log)
                    
                    # Find similar logs (placeholder)
                    similar_result = NLPService.find_similar_logs(error_log.get('Embedding', []))
                    
                    # Prepare comprehensive report
                    report = {
                        'log_details': error_log,
                        'ai_summary': summary_result if summary_result['success'] else None,
                        'suggested_solutions': solutions_result if solutions_result['success'] else None,
                        'similar_logs': similar_result if similar_result['success'] else None
                    }
                    
                    return {'success': True, 'data': report}, 200
                else:
                    return {'success': False, 'message': result['message']}, 404
                    
            except Exception as e:
                return {'success': False, 'message': str(e)}, 500
    
    @automation_ns.route('/validate')
    class AutomationValidate(Resource):
        @automation_ns.expect(error_log_model)
        @automation_ns.doc('validate_automation')
        def post(self):
            """Placeholder endpoint for automation framework validation"""
            try:
                data = request.get_json()
                
                # TODO: Implement actual validation logic
                # For now, return success with placeholder report link
                
                return {
                    'success': True,
                    'message': 'Validation completed (placeholder)',
                    'report_url': '/api/v1/reports/placeholder-id',
                    'status': 'validated'
                }, 200
                
            except Exception as e:
                return {'success': False, 'message': str(e)}, 500
    
    @health_ns.route('/')
    class HealthCheck(Resource):
        @health_ns.doc('health_check',
                      description='Check system health including database connectivity and basic statistics')
        @health_ns.response(200, 'System is healthy', health_response_model)
        @health_ns.response(500, 'System has issues', error_response_model)
        def get(self):
            """Comprehensive system health check with statistics"""
            try:
                # Check database connection
                db.session.execute(text('SELECT 1'))
                
                # Get basic statistics
                stats_result = ErrorLogService.get_statistics()
                
                return {
                    'status': 'healthy',
                    'database': 'connected',
                    'statistics': stats_result['data'] if stats_result['success'] else None,
                    'version': '1.0.0'
                }, 200
                
            except Exception as e:
                return {
                    'status': 'unhealthy',
                    'error': str(e)
                }, 500
    
    # Additional utility endpoints
    @app.route('/api/v1/statistics')
    def get_statistics():
        """Get system statistics"""
        try:
            result = ErrorLogService.get_statistics()
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify({'success': False, 'message': result['message']}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/')
    def root_index():
        return redirect('/api/docs/')

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'message': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'success': False, 'message': 'Internal server error'}), 500
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Run the development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
