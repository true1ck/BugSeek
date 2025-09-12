from flask import Flask, request, jsonify, redirect, send_file, abort, current_app
from flask_cors import CORS
from flask_restx import Api, Resource, fields, reqparse
from werkzeug.datastructures import FileStorage
from sqlalchemy import text, func
from datetime import datetime
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config
from backend.models import db, create_tables, AIAnalysisResult, OpenAIStatus, SimilarLogMatch, ErrorLog, UserSolution
from backend.services import ErrorLogService, FileService, NLPService, GenAIService
try:
    from backend.ai_services import OpenAIService, AIAnalysisService
    AI_SERVICES_AVAILABLE = True
except ImportError:
    AI_SERVICES_AVAILABLE = False

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
                
                # Generate CR_ID first
                cr_id = str(__import__('uuid').uuid4())
                
                # Save uploaded file with new system
                file_result = FileService.save_uploaded_file(
                    args['file'], 
                    cr_id,
                    app.config['UPLOAD_FOLDER']
                )
                
                if not file_result['success']:
                    return {'success': False, 'message': file_result['message']}, 400
                
                # Prepare data for error log creation
                log_data = {
                    'Cr_ID': cr_id,
                    'TeamName': args['TeamName'],
                    'Module': args['Module'],
                    'Description': args['Description'],
                    'Owner': args['Owner'],
                    'LogFileName': file_result['file_record'].OriginalFileName,
                    'SolutionPossible': args.get('SolutionPossible', False)
                }
                
                # Detect severity and environment from description/module (basic heuristics)
                severity = 'medium'
                if any(word in args['Description'].lower() for word in ['critical', 'fatal', 'crash']):
                    severity = 'critical'
                elif any(word in args['Description'].lower() for word in ['warning', 'warn', 'minor']):
                    severity = 'low'
                elif any(word in args['Description'].lower() for word in ['error', 'exception', 'fail']):
                    severity = 'high'
                
                environment = 'unknown'
                if any(word in args['Description'].lower() for word in ['prod', 'production']):
                    environment = 'prod'
                elif any(word in args['Description'].lower() for word in ['dev', 'development']):
                    environment = 'dev'
                elif any(word in args['Description'].lower() for word in ['test', 'staging']):
                    environment = 'staging'
                
                # Create error log entry
                result = ErrorLogService.create_error_log(
                    log_data, 
                    file_result['content_preview'],
                    severity,
                    environment
                )
                
                if result['success']:
                    # Generate embeddings
                    nlp_result = NLPService.generate_embeddings(file_result['content'])
                    if nlp_result['success']:
                        # Update log with embeddings
                        ErrorLogService.update_error_log(
                            result['data']['Cr_ID'],
                            {'Embedding': nlp_result['embeddings']}
                        )
                    
                    # Trigger AI analysis if available
                    if AI_SERVICES_AVAILABLE and current_app.config.get('AI_ANALYSIS_ENABLED', True):
                        try:
                            ai_service = AIAnalysisService()
                            analysis_result = ai_service.analyze_error_log(
                                result['data']['Cr_ID'],
                                file_result['content'][:10000],  # Limit content size
                                log_data
                            )
                        except Exception as ai_error:
                            current_app.logger.error(f"AI analysis failed: {ai_error}")
                    
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
    
    # New: Distinct options for selectors (teams/modules/owners)
    @logs_ns.route('/options/<string:kind>')
    class LogOptions(Resource):
        @logs_ns.doc('get_log_options', description='Get distinct values for selectors', params={'kind': 'teams | modules | owners'})
        def get(self, kind):
            try:
                mapping = {
                    'teams': ErrorLog.TeamName,
                    'modules': ErrorLog.Module,
                    'owners': ErrorLog.Owner,
                }
                column = mapping.get(kind.lower())
                if column is None:
                    return {'success': False, 'message': 'Invalid options kind'}, 400
                rows = db.session.query(column).distinct().order_by(column).all()
                values = [r[0] for r in rows if r[0]]
                return {'success': True, 'data': values}, 200
            except Exception as e:
                return {'success': False, 'message': str(e)}, 500
    
    @reports_ns.route('/<string:cr_id>')
    class LogReport(Resource):
        @reports_ns.doc('get_report',
                       description='Get comprehensive report for a specific error log including AI analysis, suggested solutions, detected error lines, similarity scores, and user solutions',
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
                    
                    # Get AI analysis if available
                    ai_analysis = None
                    analysis_row = None
                    try:
                        analysis_row = AIAnalysisResult.query.filter_by(Cr_ID=cr_id).first()
                        if analysis_row:
                            ai_analysis = analysis_row.to_dict()
                    except Exception as e:
                        current_app.logger.error(f"Failed to get AI analysis: {e}")
                    
                    # Generate or retrieve AI summary
                    if ai_analysis and ai_analysis.get('Summary'):
                        summary_result = {
                            'success': True,
                            'summary': ai_analysis['Summary'],
                            'confidence': ai_analysis.get('Confidence', 0.85),
                            'keywords': ai_analysis.get('Keywords', []),
                            'severity': ai_analysis.get('EstimatedSeverity', 'medium')
                        }
                    else:
                        summary_result = GenAIService.generate_summary(
                            error_log.get('LogContentPreview', ''),
                            error_log
                        )
                    
                    # Generate or retrieve solution suggestions
                    if ai_analysis and ai_analysis.get('SuggestedSolutions'):
                        solutions_result = {
                            'success': True,
                            'solutions': ai_analysis['SuggestedSolutions'],
                            'confidence': ai_analysis.get('Confidence', 0.75)
                        }
                    else:
                        solutions_result = GenAIService.suggest_solutions(error_log, summary_result)
                    
                    # Persist AI summary and suggestions best-effort
                    try:
                        import json as _json
                        if not analysis_row:
                            analysis_row = AIAnalysisResult(Cr_ID=cr_id, AnalysisType='summary', Status='completed')
                            db.session.add(analysis_row)
                        if summary_result.get('success'):
                            analysis_row.Summary = summary_result.get('summary')
                            analysis_row.EstimatedSeverity = summary_result.get('severity')
                            kws = summary_result.get('keywords') or []
                            analysis_row.Keywords = _json.dumps(kws) if kws else None
                        if solutions_result.get('success') and solutions_result.get('solutions') is not None:
                            # Store array
                            sols = solutions_result.get('solutions')
                            analysis_row.SuggestedSolutions = _json.dumps(sols)
                        db.session.commit()
                    except Exception as pe:
                        db.session.rollback()
                        current_app.logger.warning(f"Failed to persist AI summary/solutions: {pe}")
                    
                    # Detect error lines with line numbers (NLP) and persist
                    detected = []
                    try:
                        # Load full content
                        file_result = FileService.get_file_by_cr_id(cr_id)
                        content = ''
                        if file_result['success']:
                            read_res = FileService.read_file_content(file_result['file_record'].StoredPath)
                            if read_res['success']:
                                content = read_res['content']
                        if not content:
                            content = error_log.get('LogContentPreview', '') or ''
                        det = NLPService.extract_error_lines(content)
                        if det['success']:
                            detected = det['issues']
                            # Persist to AIAnalysisResult
                            try:
                                import json as _json
                                if not analysis_row:
                                    analysis_row = AIAnalysisResult(Cr_ID=cr_id, AnalysisType='summary', Status='completed')
                                    db.session.add(analysis_row)
                                analysis_row.DetectedIssues = _json.dumps(detected)
                                db.session.commit()
                            except Exception as pe:
                                db.session.rollback()
                                current_app.logger.warning(f"Failed to persist DetectedIssues: {pe}")
                    except Exception as de:
                        current_app.logger.warning(f"Detection failed: {de}")
                    
                    # Find similar logs
                    similar_result = NLPService.find_similar_logs(
                        cr_id,
                        error_log.get('Embedding', [])
                    )
                    
                    # Fetch user solutions
                    user_solutions = [s.to_dict() for s in UserSolution.query.filter_by(Cr_ID=cr_id).order_by(UserSolution.CreatedAt.desc()).all()]
                    
                    # Prepare comprehensive report
                    report = {
                        'log_details': error_log,
                        'ai_summary': summary_result if summary_result.get('success') else None,
                        'suggested_solutions': solutions_result if solutions_result.get('success') else None,
                        'detected_errors': detected,
                        'similar_logs': similar_result if similar_result.get('success') else None,
                        'user_solutions': user_solutions
                    }
                    
                    return {'success': True, 'data': report}, 200
                else:
                    return {'success': False, 'message': result['message']}, 404
                    
            except Exception as e:
                return {'success': False, 'message': str(e)}, 500
    
    @logs_ns.route('/<string:cr_id>/file')
    class LogFileDownload(Resource):
        @logs_ns.doc('download_log_file',
                    description='Download the original log file for a specific error log',
                    params={'cr_id': 'Unique Change Request ID for the error log'})
        @logs_ns.response(200, 'File downloaded successfully')
        @logs_ns.response(404, 'File not found', error_response_model)
        @logs_ns.response(500, 'Internal server error', error_response_model)
        def get(self, cr_id):
            """Download the original log file"""
            try:
                file_result = FileService.get_file_by_cr_id(cr_id)
                
                if not file_result['success']:
                    return {'success': False, 'message': file_result['message']}, 404
                
                file_record = file_result['file_record']
                
                # Check if file exists on disk
                if not os.path.exists(file_record.StoredPath):
                    return {'success': False, 'message': 'File not found on disk'}, 404
                
                # Send file with proper headers
                return send_file(
                    file_record.StoredPath,
                    as_attachment=True,
                    download_name=file_record.OriginalFileName,
                    mimetype=file_record.MimeType or 'application/octet-stream'
                )
                
            except Exception as e:
                return {'success': False, 'message': str(e)}, 500
    
    @logs_ns.route('/<string:cr_id>/file/info')
    class LogFileInfo(Resource):
        @logs_ns.doc('get_log_file_info',
                    description='Get file metadata for a specific error log',
                    params={'cr_id': 'Unique Change Request ID for the error log'})
        @logs_ns.response(200, 'File info retrieved successfully', success_response_model)
        @logs_ns.response(404, 'File not found', error_response_model)
        def get(self, cr_id):
            """Get file metadata and information"""
            try:
                file_result = FileService.get_file_by_cr_id(cr_id)
                
                if not file_result['success']:
                    return {'success': False, 'message': file_result['message']}, 404
                
                return {
                    'success': True,
                    'data': file_result['file_record'].to_dict()
                }, 200
                
            except Exception as e:
                return {'success': False, 'message': str(e)}, 500
    
    @automation_ns.route('/validate')
    class AutomationValidate(Resource):
        @automation_ns.expect(error_log_model)
        @automation_ns.doc('validate_automation', description='Validate error log data for automation framework integration')
        @automation_ns.response(200, 'Validation completed successfully', success_response_model)
        @automation_ns.response(400, 'Validation failed', error_response_model)
        @automation_ns.response(500, 'Internal server error', error_response_model)
        def post(self):
            """Validate error log data for automation framework integration"""
            try:
                data = request.get_json()
                
                if not data:
                    return {
                        'success': False,
                        'message': 'No data provided for validation'
                    }, 400
                
                # Validation criteria
                validation_results = {
                    'required_fields': True,
                    'data_format': True,
                    'content_quality': True,
                    'automation_ready': True,
                    'issues': []
                }
                
                # Check required fields
                required_fields = ['TeamName', 'Module', 'ErrorName', 'Description']
                missing_fields = []
                
                for field in required_fields:
                    if not data.get(field):
                        missing_fields.append(field)
                        validation_results['required_fields'] = False
                
                if missing_fields:
                    validation_results['issues'].append(
                        f"Missing required fields: {', '.join(missing_fields)}"
                    )
                
                # Check data format and quality
                if data.get('Description') and len(data['Description']) < 10:
                    validation_results['content_quality'] = False
                    validation_results['issues'].append(
                        "Error description is too short for meaningful analysis"
                    )
                
                # Check for automation readiness (log content or file)
                has_log_content = bool(data.get('LogContentPreview')) or bool(data.get('LogFile'))
                if not has_log_content:
                    validation_results['automation_ready'] = False
                    validation_results['issues'].append(
                        "No log content available for automated analysis"
                    )
                
                # Overall validation status
                all_valid = all([
                    validation_results['required_fields'],
                    validation_results['data_format'],
                    validation_results['content_quality']
                ])
                
                # Generate validation report
                report_id = f"val_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{data.get('TeamName', 'unknown')}"
                
                validation_summary = {
                    'validation_id': report_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'input_data_summary': {
                        'team': data.get('TeamName', 'Unknown'),
                        'module': data.get('Module', 'Unknown'),
                        'error': data.get('ErrorName', 'Unknown'),
                        'has_description': bool(data.get('Description')),
                        'has_log_content': has_log_content
                    },
                    'validation_results': validation_results,
                    'overall_status': 'passed' if all_valid else 'failed_with_issues',
                    'automation_compatible': validation_results['automation_ready'],
                    'recommendations': []
                }
                
                # Add recommendations based on issues
                if not validation_results['required_fields']:
                    validation_summary['recommendations'].append(
                        "Ensure all required fields (TeamName, Module, ErrorName, Description) are provided"
                    )
                
                if not validation_results['content_quality']:
                    validation_summary['recommendations'].append(
                        "Provide more detailed error descriptions for better analysis"
                    )
                
                if not validation_results['automation_ready']:
                    validation_summary['recommendations'].append(
                        "Include log content or attach log files for automated processing"
                    )
                
                if all_valid:
                    validation_summary['recommendations'].append(
                        "Data is ready for automated analysis and processing"
                    )
                
                return {
                    'success': True,
                    'message': 'Validation completed successfully',
                    'data': validation_summary,
                    'report_url': f'/api/v1/automation/reports/{report_id}',
                    'status': validation_summary['overall_status']
                }, 200
                
            except Exception as e:
                current_app.logger.error(f"Automation validation error: {e}")
                return {
                    'success': False, 
                    'message': f'Validation failed: {str(e)}'
                }, 500
    
    @logs_ns.route('/<string:cr_id>/solutions')
    class LogSolutions(Resource):
        @logs_ns.doc('list_user_solutions', description='Get user-submitted solutions for an error log')
        def get(self, cr_id):
            try:
                items = [s.to_dict() for s in UserSolution.query.filter_by(Cr_ID=cr_id).order_by(UserSolution.CreatedAt.desc()).all()]
                return {'success': True, 'data': items}, 200
            except Exception as e:
                return {'success': False, 'message': str(e)}, 500
        
        @logs_ns.doc('create_user_solution', description='Submit a user solution for an error log')
        def post(self, cr_id):
            try:
                data = request.get_json(force=True) or {}
                content = (data.get('content') or '').strip()
                author = (data.get('author') or '').strip() or None
                is_official = bool(data.get('is_official', False))
                if not content:
                    return {'success': False, 'message': 'Content is required'}, 400
                item = UserSolution(Cr_ID=cr_id, Content=content, Author=author, IsOfficial=is_official)
                db.session.add(item)
                db.session.commit()
                return {'success': True, 'data': item.to_dict()}, 201
            except Exception as e:
                db.session.rollback()
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
    
    @app.route('/api/v1/analytics')
    def get_analytics():
        """Get comprehensive analytics data for dashboard"""
        try:
            result = ErrorLogService.get_statistics()
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify({'success': False, 'message': result['message']}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/v1/openai/status')
    def get_openai_status():
        """Get OpenAI connection status"""
        try:
            result = GenAIService.check_openai_status()
            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'connected': False,
                'message': 'Failed to check OpenAI status',
                'error': str(e)
            }), 500
    
    @app.route('/api/v1/openai/test')
    def test_openai_connection():
        """Test OpenAI connection with a simple request"""
        try:
            if AI_SERVICES_AVAILABLE:
                service = OpenAIService()
                result = service.check_connection()
                return jsonify(result), 200
            else:
                return jsonify({
                    'success': False,
                    'connected': False,
                    'message': 'AI services not available'
                }), 503
        except Exception as e:
            return jsonify({
                'success': False,
                'connected': False,
                'message': 'Connection test failed',
                'error': str(e)
            }), 500
    
    @app.route('/api/v1/ai/analyze/<string:cr_id>', methods=['POST'])
    def trigger_ai_analysis(cr_id):
        """Manually trigger AI analysis for a specific log"""
        try:
            if not AI_SERVICES_AVAILABLE:
                return jsonify({
                    'success': False,
                    'message': 'AI services not available'
                }), 503
            
            # Get the error log
            log_result = ErrorLogService.get_error_log_by_id(cr_id)
            if not log_result['success']:
                return jsonify(log_result), 404
            
            error_log = log_result['data']
            
            # Get file content
            file_result = FileService.get_file_by_cr_id(cr_id)
            log_content = ''
            if file_result['success']:
                content_result = FileService.read_file_content(file_result['file_record'].StoredPath)
                if content_result['success']:
                    log_content = content_result['content']
            
            if not log_content:
                log_content = error_log.get('LogContentPreview', '')
            
            # Perform AI analysis
            ai_service = AIAnalysisService()
            result = ai_service.analyze_error_log(
                cr_id,
                log_content[:10000],  # Limit content size
                error_log
            )
            
            return jsonify(result), 200 if result['success'] else 500
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'AI analysis failed',
                'error': str(e)
            }), 500
    
    @app.route('/api/v1/ai/status/<string:cr_id>')
    def get_ai_analysis_status(cr_id):
        """Get AI analysis status for a specific log"""
        try:
            if AI_SERVICES_AVAILABLE:
                analysis = AIAnalysisResult.query.filter_by(Cr_ID=cr_id).first()
                if analysis:
                    return jsonify({
                        'success': True,
                        'analysis': analysis.to_dict()
                    }), 200
            
            return jsonify({
                'success': False,
                'message': 'No AI analysis found for this log'
            }), 404
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Failed to get analysis status',
                'error': str(e)
            }), 500
    
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
