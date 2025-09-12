#!/usr/bin/env python3
"""
4_view_database.py
Interactive database viewer and explorer for BugSeek
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import textwrap

# Add project root to path
sys.path.append(str(Path(__file__).parent))

class BugSeekDatabaseViewer:
    """Interactive database viewer for BugSeek."""
    
    def __init__(self):
        """Initialize the database viewer."""
        self.app = None
        self.db = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup database connection."""
        try:
            from flask import Flask
            from backend.models import db, ErrorLog, ErrorLogFile, AIAnalysisResult, User
            from config.settings import config
            
            self.app = Flask(__name__)
            self.app.config.from_object(config['development'])
            self.db = db
            self.db.init_app(self.app)
            
            # Import models for easy access
            self.ErrorLog = ErrorLog
            self.ErrorLogFile = ErrorLogFile
            self.AIAnalysisResult = AIAnalysisResult
            self.User = User
            
        except ImportError as e:
            print(f"[ERROR] Import error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Database setup failed: {e}")
            sys.exit(1)
    
    def show_main_menu(self):
        """Display the main menu."""
        print("\n" + "=" * 60)
        print("BugSeek Database Viewer")
        print("=" * 60)
        print("1. Database Overview")
        print("2. Browse Error Logs")
        print("3. Search and Filter")
        print("4. Team Analytics")
        print("5. Error Statistics") 
        print("6. Export Data")
        print("7. Advanced Queries")
        print("8. Special Cases Explorer")
        print("9. Data Quality Check")
        print("A. View Demo Users")
        print("0. Exit")
        print("=" * 60)
    
    def get_user_choice(self):
        """Get user menu choice."""
        try:
            choice = input("Enter your choice (0-9, A): ").strip()
            return choice
        except KeyboardInterrupt:
            print("\n\n[INFO] Goodbye!")
            sys.exit(0)
    
    def database_overview(self):
        """Show database overview."""
        print("\n" + "=" * 50)
        print("DATABASE OVERVIEW")
        print("=" * 50)
        
        with self.app.app_context():
            try:
                from sqlalchemy import inspect, text, func
                
                # Test connectivity
                result = self.db.session.execute(text('SELECT 1')).scalar()
                print(f"[OK] Database connectivity: Connected")
                
                # Get table information
                inspector = inspect(self.db.engine)
                tables = inspector.get_table_names()
                
                print(f"\nTables in database: {len(tables)}")
                for table in tables:
                    columns = len(inspector.get_columns(table))
                    indexes = len(inspector.get_indexes(table))
                    print(f"  • {table:25} : {columns:2d} columns, {indexes:2d} indexes")
                
                # Basic statistics
                total_logs = self.ErrorLog.query.count()
                if total_logs > 0:
                    print(f"\n[INFO] Error Logs Statistics:")
                    print(f"  Total Error Logs: {total_logs}")
                    
                    # Get date range
                    oldest = self.db.session.query(func.min(self.ErrorLog.CreatedAt)).scalar()
                    newest = self.db.session.query(func.max(self.ErrorLog.CreatedAt)).scalar()
                    if oldest and newest:
                        print(f"  Date Range: {oldest.strftime('%Y-%m-%d')} to {newest.strftime('%Y-%m-%d')}")
                    
                    # Team count
                    team_count = self.db.session.query(self.ErrorLog.TeamName).distinct().count()
                    print(f"  Unique Teams: {team_count}")
                    
                    # Module count
                    module_count = self.db.session.query(self.ErrorLog.Module).distinct().count()
                    print(f"  Unique Modules: {module_count}")
                    
                    # Solution rate
                    solved_count = self.ErrorLog.query.filter_by(SolutionPossible=True).count()
                    solution_rate = (solved_count / total_logs * 100) if total_logs > 0 else 0
                    print(f"  Solution Rate: {solution_rate:.1f}% ({solved_count}/{total_logs})")
                else:
                    print("\n[INFO] No error logs found in database")
                
            except Exception as e:
                print(f"[ERROR] Failed to get database overview: {e}")
    
    def browse_error_logs(self):
        """Browse error logs with pagination."""
        print("\n" + "=" * 50)
        print("BROWSE ERROR LOGS")
        print("=" * 50)
        
        with self.app.app_context():
            try:
                page = 1
                per_page = 5
                
                while True:
                    # Get paginated logs
                    logs = self.ErrorLog.query.order_by(self.ErrorLog.CreatedAt.desc()).paginate(
                        page=page, per_page=per_page, error_out=False
                    )
                    
                    print(f"\nShowing page {page} of {logs.pages} (Total: {logs.total} logs)")
                    print("-" * 80)
                    
                    for i, log in enumerate(logs.items, 1):
                        print(f"\n[{(page-1)*per_page + i}] {log.ErrorName}")
                        print(f"    Team: {log.TeamName}")
                        print(f"    Module: {log.Module}")
                        print(f"    Severity: {log.Severity}")
                        print(f"    Environment: {log.Environment}")
                        print(f"    Owner: {log.Owner}")
                        print(f"    Solution: {'Yes' if log.SolutionPossible else 'No'}")
                        print(f"    Created: {log.CreatedAt.strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        # Show preview of log content
                        if log.LogContentPreview:
                            preview = log.LogContentPreview[:200] + "..." if len(log.LogContentPreview) > 200 else log.LogContentPreview
                            wrapped_preview = textwrap.fill(preview, width=70, initial_indent="    ", subsequent_indent="    ")
                            print(f"    Preview: {wrapped_preview}")
                    
                    print("\n" + "-" * 80)
                    print("Commands: (n)ext, (p)revious, (v)iew details [number], (q)uit to menu")
                    
                    choice = input("Enter command: ").strip().lower()
                    
                    if choice == 'n' and logs.has_next:
                        page += 1
                    elif choice == 'p' and logs.has_prev:
                        page -= 1
                    elif choice == 'q':
                        break
                    elif choice.startswith('v') and len(choice) > 1:
                        try:
                            log_num = int(choice[1:].strip())
                            if 1 <= log_num <= len(logs.items):
                                self._show_log_details(logs.items[log_num - 1])
                        except ValueError:
                            print("Invalid log number")
                    elif choice == 'n' and not logs.has_next:
                        print("No more pages")
                    elif choice == 'p' and not logs.has_prev:
                        print("Already on first page")
                    else:
                        print("Invalid command")
                
            except Exception as e:
                print(f"[ERROR] Failed to browse logs: {e}")
    
    def _show_log_details(self, log):
        """Show detailed information for a specific log."""
        print("\n" + "=" * 70)
        print(f"LOG DETAILS: {log.ErrorName}")
        print("=" * 70)
        
        print(f"CR ID: {log.Cr_ID}")
        print(f"Team: {log.TeamName}")
        print(f"Module: {log.Module}")
        print(f"Error Name: {log.ErrorName}")
        print(f"Owner: {log.Owner}")
        print(f"Severity: {log.Severity}")
        print(f"Environment: {log.Environment}")
        print(f"Solution Available: {'Yes' if log.SolutionPossible else 'No'}")
        print(f"Created: {log.CreatedAt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Updated: {log.UpdatedAt.strftime('%Y-%m-%d %H:%M:%S') if log.UpdatedAt else 'Never'}")
        print(f"Log File: {log.LogFileName}")
        
        print(f"\nDescription:")
        wrapped_desc = textwrap.fill(log.Description, width=65, initial_indent="  ", subsequent_indent="  ")
        print(wrapped_desc)
        
        if log.LogContentPreview:
            print(f"\nLog Content Preview:")
            print("-" * 40)
            content_lines = log.LogContentPreview.split('\n')
            for line in content_lines[:20]:  # Show first 20 lines
                print(f"  {line}")
            if len(content_lines) > 20:
                print(f"  ... ({len(content_lines) - 20} more lines)")
        
        if log.Embedding:
            try:
                embedding_data = json.loads(log.Embedding)
                print(f"\nEmbedding Info:")
                if isinstance(embedding_data, dict):
                    if 'confidence' in embedding_data:
                        print(f"  Confidence: {embedding_data['confidence']}")
                    if 'vector' in embedding_data:
                        print(f"  Vector Length: {len(embedding_data['vector'])}")
            except json.JSONDecodeError:
                pass
        
        input("\nPress Enter to continue...")
    
    def search_and_filter(self):
        """Search and filter error logs."""
        print("\n" + "=" * 50)
        print("SEARCH AND FILTER")
        print("=" * 50)
        
        with self.app.app_context():
            try:
                # Build query with filters
                query = self.ErrorLog.query
                filters_applied = []
                
                print("Enter filter criteria (press Enter to skip):")
                
                # Team filter
                team = input("Team name: ").strip()
                if team:
                    query = query.filter(self.ErrorLog.TeamName.ilike(f"%{team}%"))
                    filters_applied.append(f"Team: {team}")
                
                # Module filter
                module = input("Module name: ").strip()
                if module:
                    query = query.filter(self.ErrorLog.Module.ilike(f"%{module}%"))
                    filters_applied.append(f"Module: {module}")
                
                # Severity filter
                severity = input("Severity (low/medium/high/critical): ").strip()
                if severity:
                    query = query.filter(self.ErrorLog.Severity.ilike(f"%{severity}%"))
                    filters_applied.append(f"Severity: {severity}")
                
                # Environment filter
                environment = input("Environment (dev/staging/prod): ").strip()
                if environment:
                    query = query.filter(self.ErrorLog.Environment.ilike(f"%{environment}%"))
                    filters_applied.append(f"Environment: {environment}")
                
                # Solution filter
                solution = input("Has solution? (y/n): ").strip().lower()
                if solution in ['y', 'yes']:
                    query = query.filter(self.ErrorLog.SolutionPossible == True)
                    filters_applied.append("Has solution: Yes")
                elif solution in ['n', 'no']:
                    query = query.filter(self.ErrorLog.SolutionPossible == False)
                    filters_applied.append("Has solution: No")
                
                # Text search
                search_text = input("Search in description/content: ").strip()
                if search_text:
                    from sqlalchemy import or_
                    query = query.filter(or_(
                        self.ErrorLog.Description.ilike(f"%{search_text}%"),
                        self.ErrorLog.ErrorName.ilike(f"%{search_text}%"),
                        self.ErrorLog.LogContentPreview.ilike(f"%{search_text}%")
                    ))
                    filters_applied.append(f"Text search: {search_text}")
                
                # Execute query
                results = query.order_by(self.ErrorLog.CreatedAt.desc()).all()
                
                print(f"\n[RESULTS] Found {len(results)} matching logs")
                if filters_applied:
                    print("Filters applied:")
                    for filter_desc in filters_applied:
                        print(f"  • {filter_desc}")
                
                if results:
                    print("\nMatching logs:")
                    for i, log in enumerate(results[:10], 1):  # Show first 10 results
                        print(f"  {i:2d}. {log.ErrorName} ({log.TeamName} - {log.Severity})")
                        print(f"      {log.CreatedAt.strftime('%Y-%m-%d %H:%M')} - {log.Module}")
                    
                    if len(results) > 10:
                        print(f"  ... and {len(results) - 10} more results")
                
            except Exception as e:
                print(f"[ERROR] Search failed: {e}")
    
    def team_analytics(self):
        """Show team analytics."""
        print("\n" + "=" * 50)
        print("TEAM ANALYTICS")
        print("=" * 50)
        
        with self.app.app_context():
            try:
                from sqlalchemy import func
                
                # Team performance
                team_stats = self.db.session.query(
                    self.ErrorLog.TeamName,
                    func.count(self.ErrorLog.Cr_ID).label('total_errors'),
                    func.sum(func.cast(self.ErrorLog.SolutionPossible, self.db.Integer)).label('solutions'),
                    func.count(func.distinct(self.ErrorLog.Module)).label('modules_affected')
                ).group_by(self.ErrorLog.TeamName).order_by('total_errors desc').all()
                
                print("Team Performance Summary:")
                print("-" * 70)
                print(f"{'Team':20} {'Errors':>8} {'Solutions':>10} {'Rate':>8} {'Modules':>8}")
                print("-" * 70)
                
                for team, total, solutions, modules in team_stats:
                    solution_rate = (solutions / total * 100) if total > 0 else 0
                    print(f"{team:20} {total:>8} {solutions or 0:>10} {solution_rate:>7.1f}% {modules:>8}")
                
                # Severity distribution by team
                print(f"\nSeverity Distribution by Team:")
                print("-" * 70)
                
                severity_stats = self.db.session.query(
                    self.ErrorLog.TeamName,
                    self.ErrorLog.Severity,
                    func.count(self.ErrorLog.Cr_ID).label('count')
                ).group_by(self.ErrorLog.TeamName, self.ErrorLog.Severity).all()
                
                # Group by team
                team_severity = {}
                for team, severity, count in severity_stats:
                    if team not in team_severity:
                        team_severity[team] = {}
                    team_severity[team][severity] = count
                
                print(f"{'Team':20} {'Critical':>9} {'High':>6} {'Medium':>8} {'Low':>5}")
                print("-" * 70)
                
                for team in sorted(team_severity.keys()):
                    severities = team_severity[team]
                    critical = severities.get('critical', 0)
                    high = severities.get('high', 0)
                    medium = severities.get('medium', 0)
                    low = severities.get('low', 0)
                    print(f"{team:20} {critical:>9} {high:>6} {medium:>8} {low:>5}")
                
            except Exception as e:
                print(f"[ERROR] Team analytics failed: {e}")
    
    def error_statistics(self):
        """Show error statistics."""
        print("\n" + "=" * 50)
        print("ERROR STATISTICS")
        print("=" * 50)
        
        with self.app.app_context():
            try:
                from sqlalchemy import func
                
                total_logs = self.ErrorLog.query.count()
                if total_logs == 0:
                    print("[INFO] No error logs found")
                    return
                
                print(f"Total Error Logs: {total_logs}")
                
                # Environment distribution
                print(f"\nBy Environment:")
                env_stats = self.db.session.query(
                    self.ErrorLog.Environment,
                    func.count(self.ErrorLog.Cr_ID).label('count'),
                    (func.count(self.ErrorLog.Cr_ID) * 100.0 / total_logs).label('percentage')
                ).group_by(self.ErrorLog.Environment).order_by('count desc').all()
                
                for env, count, pct in env_stats:
                    print(f"  {env.capitalize():12}: {count:4d} ({pct:5.1f}%)")
                
                # Severity distribution
                print(f"\nBy Severity:")
                severity_stats = self.db.session.query(
                    self.ErrorLog.Severity,
                    func.count(self.ErrorLog.Cr_ID).label('count'),
                    (func.count(self.ErrorLog.Cr_ID) * 100.0 / total_logs).label('percentage')
                ).group_by(self.ErrorLog.Severity).order_by('count desc').all()
                
                for severity, count, pct in severity_stats:
                    print(f"  {severity.capitalize():12}: {count:4d} ({pct:5.1f}%)")
                
                # Solution availability
                print(f"\nSolution Availability:")
                solution_stats = self.db.session.query(
                    self.ErrorLog.SolutionPossible,
                    func.count(self.ErrorLog.Cr_ID).label('count'),
                    (func.count(self.ErrorLog.Cr_ID) * 100.0 / total_logs).label('percentage')
                ).group_by(self.ErrorLog.SolutionPossible).all()
                
                for has_solution, count, pct in solution_stats:
                    status = "Available" if has_solution else "Not Available"
                    print(f"  {status:12}: {count:4d} ({pct:5.1f}%)")
                
                # Most common error types
                print(f"\nMost Common Error Types:")
                error_types = self.db.session.query(
                    self.ErrorLog.ErrorName,
                    func.count(self.ErrorLog.Cr_ID).label('count')
                ).group_by(self.ErrorLog.ErrorName).order_by('count desc').limit(10).all()
                
                for error_name, count in error_types:
                    print(f"  {error_name[:40]:40}: {count:4d}")
                
            except Exception as e:
                print(f"[ERROR] Statistics failed: {e}")
    
    def export_data(self):
        """Export data to CSV or JSON."""
        print("\n" + "=" * 50)
        print("EXPORT DATA")
        print("=" * 50)
        
        print("Export options:")
        print("1. All error logs to CSV")
        print("2. All error logs to JSON")
        print("3. Team summary to CSV")
        print("4. Custom query results")
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            self._export_logs_csv()
        elif choice == '2':
            self._export_logs_json()
        elif choice == '3':
            self._export_team_summary()
        elif choice == '4':
            self._export_custom_query()
        else:
            print("Invalid choice")
    
    def _export_logs_csv(self):
        """Export all logs to CSV."""
        with self.app.app_context():
            try:
                import csv
                from datetime import datetime
                
                logs = self.ErrorLog.query.all()
                filename = f"bugseek_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow([
                        'CR_ID', 'TeamName', 'Module', 'ErrorName', 'Severity', 
                        'Environment', 'Owner', 'SolutionPossible', 'CreatedAt', 
                        'Description', 'LogFileName'
                    ])
                    
                    # Write data
                    for log in logs:
                        writer.writerow([
                            log.Cr_ID, log.TeamName, log.Module, log.ErrorName, 
                            log.Severity, log.Environment, log.Owner, 
                            log.SolutionPossible, log.CreatedAt, log.Description, 
                            log.LogFileName
                        ])
                
                print(f"[SUCCESS] Exported {len(logs)} logs to {filename}")
                
            except Exception as e:
                print(f"[ERROR] CSV export failed: {e}")
    
    def _export_logs_json(self):
        """Export all logs to JSON."""
        with self.app.app_context():
            try:
                logs = self.ErrorLog.query.all()
                filename = f"bugseek_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                data = []
                for log in logs:
                    data.append({
                        'cr_id': log.Cr_ID,
                        'team_name': log.TeamName,
                        'module': log.Module,
                        'error_name': log.ErrorName,
                        'severity': log.Severity,
                        'environment': log.Environment,
                        'owner': log.Owner,
                        'solution_possible': log.SolutionPossible,
                        'created_at': log.CreatedAt.isoformat() if log.CreatedAt else None,
                        'description': log.Description,
                        'log_filename': log.LogFileName,
                        'log_content_preview': log.LogContentPreview
                    })
                
                with open(filename, 'w', encoding='utf-8') as jsonfile:
                    json.dump(data, jsonfile, indent=2, ensure_ascii=False)
                
                print(f"[SUCCESS] Exported {len(logs)} logs to {filename}")
                
            except Exception as e:
                print(f"[ERROR] JSON export failed: {e}")
    
    def _export_team_summary(self):
        """Export team summary to CSV."""
        with self.app.app_context():
            try:
                import csv
                from sqlalchemy import func
                
                team_stats = self.db.session.query(
                    self.ErrorLog.TeamName,
                    func.count(self.ErrorLog.Cr_ID).label('total_errors'),
                    func.sum(func.cast(self.ErrorLog.SolutionPossible, self.db.Integer)).label('solutions'),
                    func.count(func.distinct(self.ErrorLog.Module)).label('modules_affected')
                ).group_by(self.ErrorLog.TeamName).all()
                
                filename = f"team_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    writer.writerow(['Team', 'Total_Errors', 'Solutions', 'Solution_Rate', 'Modules_Affected'])
                    
                    for team, total, solutions, modules in team_stats:
                        solution_rate = (solutions / total * 100) if total > 0 else 0
                        writer.writerow([team, total, solutions or 0, f"{solution_rate:.1f}%", modules])
                
                print(f"[SUCCESS] Exported team summary to {filename}")
                
            except Exception as e:
                print(f"[ERROR] Team summary export failed: {e}")
    
    def _export_custom_query(self):
        """Export custom query results."""
        print("Custom query export - coming soon!")
    
    def special_cases_explorer(self):
        """Explore special cases and edge cases."""
        print("\n" + "=" * 50)
        print("SPECIAL CASES EXPLORER")
        print("=" * 50)
        
        with self.app.app_context():
            try:
                # Look for special case error types
                special_error_types = [
                    'MEMORY_LEAK_GRADUAL_DEGRADATION',
                    'UNICODE_ENCODING_ERROR',
                    'RATE_LIMITER_OVERLOAD', 
                    'INTERMITTENT_CONNECTION_DROP',
                    'NULL_DATA_EXCEPTION',
                    'TIMEZONE_DST_CONFLICT',
                    'DATABASE_DEADLOCK_CONCURRENT',
                    'SYSTEM_RESOURCE_EXHAUSTION'
                ]
                
                special_cases = self.ErrorLog.query.filter(
                    self.ErrorLog.ErrorName.in_(special_error_types)
                ).all()
                
                print(f"Found {len(special_cases)} special case error logs:")
                
                for i, log in enumerate(special_cases, 1):
                    print(f"\n[{i}] {log.ErrorName}")
                    print(f"    Team: {log.TeamName}")
                    print(f"    Severity: {log.Severity}")
                    print(f"    Environment: {log.Environment}")
                    print(f"    Created: {log.CreatedAt.strftime('%Y-%m-%d %H:%M')}")
                    
                    # Show brief description
                    desc_preview = log.Description[:100] + "..." if len(log.Description) > 100 else log.Description
                    print(f"    Description: {desc_preview}")
                
                if special_cases:
                    print(f"\nThese cases represent edge scenarios for testing:")
                    print("• Memory leaks and resource exhaustion")
                    print("• Unicode and encoding issues") 
                    print("• High-frequency and extreme load scenarios")
                    print("• Network reliability and intermittent failures")
                    print("• Data validation and null handling")
                    print("• Time zone and scheduling conflicts")
                    print("• Database concurrency and deadlocks")
                    print("• System resource monitoring")
                else:
                    print("\n[INFO] No special cases found. Run script 3 to add them:")
                    print("python 3_add_special_cases_sample_data.py")
                
            except Exception as e:
                print(f"[ERROR] Special cases explorer failed: {e}")
    
    def data_quality_check(self):
        """Perform data quality checks."""
        print("\n" + "=" * 50)
        print("DATA QUALITY CHECK")
        print("=" * 50)
        
        with self.app.app_context():
            try:
                total_logs = self.ErrorLog.query.count()
                print(f"Total logs: {total_logs}")
                
                if total_logs == 0:
                    print("[INFO] No logs to check")
                    return
                
                # Check for required fields
                print("\nRequired Field Completeness:")
                
                missing_team = self.ErrorLog.query.filter(
                    (self.ErrorLog.TeamName.is_(None)) | 
                    (self.ErrorLog.TeamName == '')
                ).count()
                print(f"  Missing TeamName: {missing_team}")
                
                missing_module = self.ErrorLog.query.filter(
                    (self.ErrorLog.Module.is_(None)) | 
                    (self.ErrorLog.Module == '')
                ).count()
                print(f"  Missing Module: {missing_module}")
                
                missing_error_name = self.ErrorLog.query.filter(
                    (self.ErrorLog.ErrorName.is_(None)) | 
                    (self.ErrorLog.ErrorName == '')
                ).count()
                print(f"  Missing ErrorName: {missing_error_name}")
                
                missing_owner = self.ErrorLog.query.filter(
                    (self.ErrorLog.Owner.is_(None)) | 
                    (self.ErrorLog.Owner == '')
                ).count()
                print(f"  Missing Owner: {missing_owner}")
                
                # Check data consistency
                print("\nData Consistency:")
                
                # Valid severity levels
                valid_severities = ['low', 'medium', 'high', 'critical']
                invalid_severity = self.ErrorLog.query.filter(
                    ~self.ErrorLog.Severity.in_(valid_severities)
                ).count()
                print(f"  Invalid Severity levels: {invalid_severity}")
                
                # Valid environments
                valid_environments = ['dev', 'staging', 'prod', 'unknown']
                invalid_environment = self.ErrorLog.query.filter(
                    ~self.ErrorLog.Environment.in_(valid_environments)
                ).count()
                print(f"  Invalid Environment values: {invalid_environment}")
                
                # Check for duplicates
                print("\nDuplicate Detection:")
                from sqlalchemy import func
                
                duplicate_errors = self.db.session.query(
                    self.ErrorLog.ErrorName,
                    self.ErrorLog.TeamName,
                    self.ErrorLog.Module,
                    func.count(self.ErrorLog.Cr_ID).label('count')
                ).group_by(
                    self.ErrorLog.ErrorName,
                    self.ErrorLog.TeamName,
                    self.ErrorLog.Module
                ).having(func.count(self.ErrorLog.Cr_ID) > 1).all()
                
                print(f"  Potential duplicate groups: {len(duplicate_errors)}")
                
                if duplicate_errors:
                    print("  Top duplicate groups:")
                    for error_name, team, module, count in duplicate_errors[:5]:
                        print(f"    {error_name} ({team}-{module}): {count} instances")
                
                # Overall quality score
                total_issues = (missing_team + missing_module + missing_error_name + 
                              missing_owner + invalid_severity + invalid_environment)
                quality_score = max(0, 100 - (total_issues / total_logs * 100)) if total_logs > 0 else 100
                
                print(f"\nOverall Data Quality Score: {quality_score:.1f}%")
                
                if quality_score >= 95:
                    print("✅ Excellent data quality")
                elif quality_score >= 80:
                    print("⚠️  Good data quality with minor issues")
                elif quality_score >= 60:
                    print("⚠️  Moderate data quality - some cleanup needed")
                else:
                    print("❌ Poor data quality - significant issues found")
                
            except Exception as e:
                print(f"[ERROR] Data quality check failed: {e}")
    
    def view_demo_users(self):
        """View demo users and authentication data."""
        print("\n" + "=" * 50)
        print("DEMO USERS")
        print("=" * 50)
        
        with self.app.app_context():
            try:
                # Check if User table exists
                from sqlalchemy import inspect
                inspector = inspect(self.db.engine)
                tables = inspector.get_table_names()
                
                if 'users' not in tables:
                    print("[INFO] User table not found. Users may not be set up yet.")
                    print("Run: python 1_initialize_database.py to create users")
                    return
                
                # Get all users
                users = self.User.query.all()
                
                if not users:
                    print("[INFO] No demo users found in database.")
                    print("\nTo create demo users, run one of these scripts:")
                    print("• python 1_initialize_database.py")
                    print("• python 2_load_sample_data.py")
                    print("• python create_demo_users.py")
                    return
                
                print(f"Found {len(users)} demo users:")
                print("-" * 80)
                print(f"{'Employee ID':15} {'Role':25} {'Active':8} {'Created':20}")
                print("-" * 80)
                
                for user in users:
                    status = "Yes" if user.is_active else "No"
                    created = user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else "Unknown"
                    print(f"{user.employee_id:15} {user.role:25} {status:8} {created:20}")
                
                print("\n" + "=" * 50)
                print("AUTHENTICATION CREDENTIALS")
                print("=" * 50)
                print("Use these credentials to log into the application:")
                print()
                print("Employee ID / Password:")
                print("• admin / admin123 (System Administrator)")
                print("• developer / dev123 (Developer User)")
                print("• testuser / test123 (Test User)")
                print("• hackathon / hackathon2025 (Hackathon Participant)")
                print("• demo / demo123 (Demo User)")
                print("\nNote: Passwords are hashed in the database for security.")
                
                # Check for any non-active users
                inactive_users = [u for u in users if not u.is_active]
                if inactive_users:
                    print(f"\n[WARN] {len(inactive_users)} inactive users found:")
                    for user in inactive_users:
                        print(f"  • {user.employee_id} ({user.role})")
                
            except Exception as e:
                print(f"[ERROR] Failed to view demo users: {e}")
                import traceback
                traceback.print_exc()
    
    def run(self):
        """Main run loop."""
        print("🔍 BugSeek Database Viewer")
        print("Interactive database exploration tool")
        
        while True:
            self.show_main_menu()
            choice = self.get_user_choice()
            
            if choice == '0':
                print("\n[INFO] Goodbye!")
                break
            elif choice == '1':
                self.database_overview()
            elif choice == '2':
                self.browse_error_logs()
            elif choice == '3':
                self.search_and_filter()
            elif choice == '4':
                self.team_analytics()
            elif choice == '5':
                self.error_statistics()
            elif choice == '6':
                self.export_data()
            elif choice == '7':
                print("Advanced queries - coming soon!")
            elif choice == '8':
                self.special_cases_explorer()
            elif choice == '9':
                self.data_quality_check()
            elif choice.upper() == 'A':
                self.view_demo_users()
            else:
                print("Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")

def main():
    """Main function."""
    try:
        viewer = BugSeekDatabaseViewer()
        viewer.run()
    except KeyboardInterrupt:
        print("\n\n[INFO] Goodbye!")
    except Exception as e:
        print(f"\n[ERROR] Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
