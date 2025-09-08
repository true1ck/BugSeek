from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import requests
import os
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configuration
API_BASE_URL = 'http://localhost:5000'

def make_api_request(endpoint, method='GET', data=None, files=None):
    """Make API request to backend."""
    try:
        url = f"{API_BASE_URL}/api/v1{endpoint}"
        
        if method == 'GET':
            response = requests.get(url, params=data, timeout=10)
        elif method == 'POST':
            if files:
                response = requests.post(url, data=data, files=files, timeout=30)
            else:
                response = requests.post(url, json=data, timeout=10)
        
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return {'success': False, 'message': f'Connection error: {str(e)}'}, 500

@app.route('/')
def index():
    """Main dashboard."""
    # Get basic stats
    stats_data, _ = make_api_request("/statistics")
    stats = stats_data.get('data', {}) if stats_data.get('success') else {}
    
    return render_template('index.html', stats=stats)

@app.route('/upload')
def upload_page():
    """Upload page."""
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_log():
    """Handle log upload."""
    try:
        # Get form data
        team_name = request.form.get('team_name')
        module = request.form.get('module')
        owner = request.form.get('owner')
        description = request.form.get('description')
        solution_possible = 'solution_possible' in request.form
        
        # Get uploaded file
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('upload_page'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('upload_page'))
        
        # Validate required fields
        if not all([team_name, module, owner, description]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('upload_page'))
        
        # Prepare data for API
        data = {
            'TeamName': team_name,
            'Module': module,
            'Owner': owner,
            'Description': description,
            'SolutionPossible': solution_possible
        }
        
        files = {'file': (file.filename, file, file.mimetype)}
        
        # Submit to API
        result, status_code = make_api_request('/logs/upload', 'POST', data=data, files=files)
        
        if status_code == 201 and result.get('success'):
            flash(f'Log uploaded successfully! CR ID: {result.get("Cr_ID")}', 'success')
            return redirect(url_for('view_report', cr_id=result.get("Cr_ID")))
        else:
            flash(f'Upload failed: {result.get("message", "Unknown error")}', 'error')
            return redirect(url_for('upload_page'))
            
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('upload_page'))

@app.route('/logs')
def logs_list():
    """List all logs."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    team_filter = request.args.get('team', '')
    
    # Prepare filters
    filters = {}
    if search:
        filters['search'] = search
    if team_filter:
        filters['TeamName'] = team_filter
    
    filters['page'] = page
    filters['per_page'] = 10
    
    result, status_code = make_api_request('/logs/', 'GET', data=filters)
    
    logs = []
    pagination = {}
    
    if status_code == 200 and result.get('success'):
        logs = result.get('data', {}).get('logs', [])
        pagination = result.get('data', {}).get('pagination', {})
    
    return render_template('logs.html', logs=logs, pagination=pagination, search=search, team_filter=team_filter)

@app.route('/report/<cr_id>')
def view_report(cr_id):
    """View detailed report."""
    result, status_code = make_api_request(f'/reports/{cr_id}')
    
    if status_code == 200 and result.get('success'):
        report_data = result.get('data', {})
        return render_template('report.html', report=report_data)
    else:
        flash(f'Report not found: {result.get("message", "Unknown error")}', 'error')
        return redirect(url_for('logs_list'))

@app.route('/search')
def search_page():
    """Advanced search page."""
    return render_template('search.html')

@app.route('/analytics')
def analytics_page():
    """Analytics dashboard page."""
    return render_template('analytics.html')

@app.route('/docs')
def documentation_page():
    """Documentation page with API reference and guides."""
    return render_template('docs.html')

@app.route('/api/health')
def health_check():
    """Check API health."""
    result, status_code = make_api_request('/health')
    return jsonify({
        'api_status': 'connected' if status_code == 200 else 'disconnected',
        'frontend_status': 'running'
    })

if __name__ == '__main__':
    app.run(debug=True, port=8080)
