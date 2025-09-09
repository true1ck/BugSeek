#!/usr/bin/env python3
import sys
sys.path.append('.')
from flask import Flask
from backend.app import create_app
from backend.services import ErrorLogService

app = create_app()
with app.app_context():
    result = ErrorLogService.get_statistics()
    if result['success']:
        data = result['data']
        print('📊 Analytics Data Summary:')
        print(f'   • Total Logs: {data["total_logs"]}')
        print(f'   • Resolved: {data["resolved_count"]}')
        print(f'   • Solution Rate: {data["solution_rate"]}%')
        print(f'   • Teams: {data["teams_count"]}')
        print(f'   • Modules: {data["modules_count"]}')
        print(f'   • Recent Activity: {len(data["recent_activity"])} items')
        print('   • Top 3 Teams by Errors:')
        for team in data['team_stats'][:3]:
            print(f'     - {team["team"]}: {team["total_errors"]} errors ({team["solution_rate"]}% solved)')
    else:
        print(f'❌ Error: {result["message"]}')
