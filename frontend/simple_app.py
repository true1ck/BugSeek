#!/usr/bin/env python3
"""
Simple Flask frontend app to test the AI integration with HTML templates
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.secret_key = 'bugseek-frontend-test-key'

# Backend API configuration
BACKEND_URL = "http://localhost:5000"
API_BASE = f"{BACKEND_URL}/api/v1"

@app.route('/')
def index():
    """Home page"""
    try:
        # Get basic statistics
        response = requests.get(f"{API_BASE}/health", timeout=5)
        backend_status = response.status_code == 200
        
        # Get recent logs
        logs_response = requests.get(f"{API_BASE}/logs/", params={'per_page': 5}, timeout=10)
        recent_logs = []
        if logs_response.status_code == 200:
            data = logs_response.json()
            if data.get('success'):
                recent_logs = data['data']['logs']
    except:
        backend_status = False
        recent_logs = []
    
    return render_template('index.html', 
                         backend_status=backend_status,
                         recent_logs=recent_logs)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload page"""
    if request.method == 'POST':
        try:
            # Get form data
            file = request.files.get('file')
            team_name = request.form.get('team_name')
            module = request.form.get('module')
            description = request.form.get('description')
            owner = request.form.get('owner')
            solution_possible = 'solution_possible' in request.form
            
            if not all([file, team_name, module, description, owner]):
                flash('All fields are required', 'error')
                return render_template('upload.html')
            
            # Prepare upload data
            files = {
                'file': (file.filename, file.stream, file.content_type)
            }
            
            data = {
                'TeamName': team_name,
                'Module': module,
                'Description': description,
                'Owner': owner,
                'SolutionPossible': solution_possible
            }
            
            # Upload to backend
            response = requests.post(f"{API_BASE}/logs/upload", data=data, files=files, timeout=30)
            
            if response.status_code == 201:
                result = response.json()
                if result.get('success'):
                    flash('Log uploaded successfully! AI analysis in progress...', 'success')
                    return redirect(url_for('report', cr_id=result['Cr_ID']))
                else:
                    flash(f"Upload failed: {result.get('message')}", 'error')
            else:
                flash(f"Upload failed: HTTP {response.status_code}", 'error')
                
        except Exception as e:
            flash(f"Upload error: {str(e)}", 'error')
    
    return render_template('upload.html')

@app.route('/report/<cr_id>')
def report(cr_id):
    """Report page"""
    try:
        # Get report data
        response = requests.get(f"{API_BASE}/reports/{cr_id}", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                report_data = data['data']
                return render_template('report.html', report=report_data)
            else:
                flash(f"Report not found: {data.get('message')}", 'error')
                return redirect(url_for('index'))
        else:
            flash(f"Failed to load report: HTTP {response.status_code}", 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f"Report error: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/logs')
def logs():
    """Logs listing page"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        team = request.args.get('team', '')
        module = request.args.get('module', '')
        
        # Build query params
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if search:
            params['search'] = search
        if team:
            params['TeamName'] = team
        if module:
            params['Module'] = module
        
        # Get logs
        response = requests.get(f"{API_BASE}/logs/", params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logs_data = data['data']['logs']
                pagination = data['data']['pagination']
                return render_template('logs.html', 
                                     logs=logs_data, 
                                     pagination=pagination,
                                     search=search,
                                     team=team,
                                     module=module)
        
        flash('Failed to load logs', 'error')
        return render_template('logs.html', logs=[], pagination={})
        
    except Exception as e:
        flash(f"Error loading logs: {str(e)}", 'error')
        return render_template('logs.html', logs=[], pagination={})

@app.route('/api/test')
def api_test():
    """API test endpoint"""
    try:
        # Test backend connectivity
        health_response = requests.get(f"{API_BASE}/health", timeout=5)
        health_data = health_response.json() if health_response.status_code == 200 else {}
        
        # Test AI status
        ai_response = requests.get(f"{API_BASE}/openai/status", timeout=5)
        ai_data = ai_response.json() if ai_response.status_code == 200 else {}
        
        return jsonify({
            'backend': {
                'status': health_response.status_code,
                'data': health_data
            },
            'ai': {
                'status': ai_response.status_code,
                'data': ai_data
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'backend': {'status': 'error'},
            'ai': {'status': 'error'}
        }), 500

if __name__ == '__main__':
    print("🌐 Starting BugSeek Frontend Test Server")
    print("   Backend API:", BACKEND_URL)
    print("   Frontend URL: http://localhost:8080")
    print("   Templates: frontend/templates/")
    
    app.run(host='0.0.0.0', port=8080, debug=True)
