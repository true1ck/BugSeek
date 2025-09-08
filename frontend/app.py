import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config

# Configure Streamlit page
st.set_page_config(
    page_title="BugSeek - Error Log Management",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/bugseek',
        'Report a bug': 'https://github.com/your-repo/bugseek/issues',
        'About': "BugSeek v1.0 - Professional Error Log Management System"
    }
)

# Load configuration
config = Config()
API_BASE_URL = config.BACKEND_API_URL

# Custom CSS for professional styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e9ecef;
    }
    
    .upload-section {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #007bff;
        margin: 1rem 0;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    
    .log-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    .report-header {
        background: linear-gradient(90deg, #007bff, #6f42c1);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Utility functions
def make_api_request(endpoint, method='GET', data=None, files=None):
    """Make API request to backend."""
    try:
        url = f"{API_BASE_URL}/api/v1{endpoint}"
        
        if method == 'GET':
            response = requests.get(url, params=data, timeout=30)
        elif method == 'POST':
            if files:
                response = requests.post(url, data=data, files=files, timeout=30)
            else:
                response = requests.post(url, json=data, timeout=30)
        
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return {'success': False, 'message': f'Connection error: {str(e)}'}, 500

def display_success_message(message):
    """Display success message."""
    st.markdown(f'<div class="success-message">✅ {message}</div>', unsafe_allow_html=True)

def display_error_message(message):
    """Display error message."""
    st.markdown(f'<div class="error-message">❌ {message}</div>', unsafe_allow_html=True)

def display_log_card(log):
    """Display log information in a card format."""
    with st.container():
        st.markdown('<div class="log-card">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.subheader(f"🔍 {log['ErrorName']}")
            st.write(f"**Team:** {log['TeamName']}")
            st.write(f"**Module:** {log['Module']}")
            st.write(f"**Owner:** {log['Owner']}")
        
        with col2:
            st.write(f"**File:** {log['LogFileName']}")
            st.write(f"**Size:** {log.get('FileSize', 0):,} bytes")
            st.write(f"**Created:** {log['CreatedAt'][:10] if log.get('CreatedAt') else 'N/A'}")
        
        with col3:
            solution_color = "🟢" if log.get('SolutionPossible') else "🔴"
            st.write(f"**Solution:** {solution_color}")
            
            if st.button(f"View Report", key=f"view_{log['Cr_ID']}", use_container_width=True):
                st.session_state.selected_log_id = log['Cr_ID']
                st.session_state.current_page = "Report"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Upload"

if 'selected_log_id' not in st.session_state:
    st.session_state.selected_log_id = None

# Sidebar navigation
with st.sidebar:
    st.title("🔍 BugSeek")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["Upload", "Search", "Reports", "Dashboard"],
        index=["Upload", "Search", "Reports", "Dashboard"].index(st.session_state.current_page)
    )
    
    if page != st.session_state.current_page:
        st.session_state.current_page = page
        st.rerun()
    
    st.markdown("---")
    
    # Quick stats
    stats_data, status_code = make_api_request("/statistics")
    if status_code == 200 and stats_data.get('success'):
        stats = stats_data['data']
        st.metric("Total Logs", stats.get('total_logs', 0))
        st.metric("With Solutions", stats.get('logs_with_solutions', 0))
        st.metric("Solution Rate", f"{stats.get('solution_rate', 0):.1f}%")
    
    st.markdown("---")
    
    # Theme toggle placeholder
    st.selectbox("Theme", ["Light", "Dark"], disabled=True)
    
    # API Status
    health_data, health_status = make_api_request("/health")
    if health_status == 200:
        st.success("🟢 API Connected")
    else:
        st.error("🔴 API Disconnected")

# Main content area
if st.session_state.current_page == "Upload":
    st.title("📤 Upload Error Log")
    st.markdown("Upload your error log files with metadata for analysis and reporting.")
    
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a log file",
            type=['txt', 'log', 'json', 'xml'],
            help="Supported formats: TXT, LOG, JSON, XML (Max 16MB)"
        )
        
        if uploaded_file is not None:
            # Show file info
            st.write("📁 **File Details:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Name:** {uploaded_file.name}")
            with col2:
                st.write(f"**Size:** {uploaded_file.size:,} bytes")
            with col3:
                st.write(f"**Type:** {uploaded_file.type}")
            
            # Preview file content
            if st.checkbox("Preview file content"):
                try:
                    content = str(uploaded_file.read(), "utf-8")[:1000]
                    st.text_area("File Content Preview", content, height=200)
                    uploaded_file.seek(0)  # Reset file pointer
                except:
                    st.warning("Unable to preview file content")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Metadata form
    st.subheader("📝 Error Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        team_name = st.text_input("Team Name *", placeholder="e.g., Frontend Team")
        module = st.text_input("Module *", placeholder="e.g., Authentication")
        error_name = st.text_input("Error Name *", placeholder="e.g., Login Timeout Error")
    
    with col2:
        owner = st.text_input("Owner *", placeholder="e.g., john.doe@company.com")
        solution_possible = st.checkbox("Solution Available", help="Check if a solution is known")
    
    description = st.text_area(
        "Error Description *", 
        placeholder="Provide a detailed description of the error...",
        height=100
    )
    
    # Submit button
    if st.button("🚀 Upload Log", type="primary", use_container_width=True):
        # Validation
        if not all([uploaded_file, team_name, module, error_name, owner, description]):
            display_error_message("Please fill in all required fields marked with *")
        else:
            with st.spinner("Uploading and processing log file..."):
                # Prepare form data
                files = {
                    'file': (uploaded_file.name, uploaded_file, uploaded_file.type)
                }
                
                data = {
                    'TeamName': team_name,
                    'Module': module,
                    'ErrorName': error_name,
                    'Owner': owner,
                    'Description': description,
                    'SolutionPossible': solution_possible
                }
                
                # Upload file
                response_data, status_code = make_api_request("/logs/upload", "POST", data=data, files=files)
                
                if status_code == 201 and response_data.get('success'):
                    display_success_message(f"Log uploaded successfully! Report ID: {response_data['Cr_ID']}")
                    
                    # Show report link
                    if st.button("View Report", type="secondary"):
                        st.session_state.selected_log_id = response_data['Cr_ID']
                        st.session_state.current_page = "Report"
                        st.experimental_rerun()
                else:
                    display_error_message(f"Upload failed: {response_data.get('message', 'Unknown error')}")

elif st.session_state.current_page == "Search":
    st.title("🔍 Search Error Logs")
    st.markdown("Search and filter through your error logs with advanced filtering options.")
    
    # Search filters
    with st.expander("🔧 Search Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("Search Term", placeholder="Enter keywords...")
            team_filter = st.text_input("Team Name", placeholder="Filter by team...")
        
        with col2:
            module_filter = st.text_input("Module", placeholder="Filter by module...")
            owner_filter = st.text_input("Owner", placeholder="Filter by owner...")
        
        with col3:
            error_filter = st.text_input("Error Name", placeholder="Filter by error...")
            solution_filter = st.selectbox("Solution Available", ["All", "Yes", "No"])
    
    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        page = st.number_input("Page", min_value=1, value=1)
    with col2:
        per_page = st.selectbox("Results per page", [10, 20, 50, 100], index=1)
    
    # Search button
    if st.button("🔍 Search", type="primary"):
        # Prepare filters
        filters = {
            'page': page,
            'per_page': per_page
        }
        
        if search_term:
            filters['search'] = search_term
        if team_filter:
            filters['TeamName'] = team_filter
        if module_filter:
            filters['Module'] = module_filter
        if owner_filter:
            filters['Owner'] = owner_filter
        if error_filter:
            filters['ErrorName'] = error_filter
        if solution_filter != "All":
            filters['SolutionPossible'] = solution_filter == "Yes"
        
        # Make search request
        with st.spinner("Searching..."):
            response_data, status_code = make_api_request("/logs/", data=filters)
            
            if status_code == 200 and response_data.get('success'):
                logs = response_data['data']
                pagination = response_data['pagination']
                
                st.success(f"Found {pagination['total']} logs (Page {pagination['page']} of {pagination['pages']})")
                
                # Display results
                if logs:
                    st.subheader("📋 Search Results")
                    
                    for log in logs:
                        display_log_card(log)
                    
                    # Pagination info
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.write(f"Showing {len(logs)} results of {pagination['total']} total")
                else:
                    st.info("No logs found matching your search criteria.")
            else:
                display_error_message(f"Search failed: {response_data.get('message', 'Unknown error')}")

elif st.session_state.current_page == "Reports" or st.session_state.current_page == "Report":
    if st.session_state.selected_log_id:
        # Individual report view
        log_id = st.session_state.selected_log_id
        
        with st.spinner("Loading report..."):
            response_data, status_code = make_api_request(f"/reports/{log_id}")
            
            if status_code == 200 and response_data.get('success'):
                report = response_data['data']
                log_details = report['log_details']
                
                # Report header
                st.markdown(
                    f'''
                    <div class="report-header">
                        <h1>📊 Error Report</h1>
                        <h3>{log_details['ErrorName']}</h3>
                        <p>Report ID: {log_details['Cr_ID']}</p>
                    </div>
                    ''', 
                    unsafe_allow_html=True
                )
                
                # Back button
                if st.button("← Back to Search"):
                    st.session_state.current_page = "Search"
                    st.experimental_rerun()
                
                # Log details section
                st.subheader("📋 Log Details")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Team:** {log_details['TeamName']}")
                    st.write(f"**Module:** {log_details['Module']}")
                    st.write(f"**Owner:** {log_details['Owner']}")
                    st.write(f"**Error Name:** {log_details['ErrorName']}")
                
                with col2:
                    st.write(f"**File Name:** {log_details['LogFileName']}")
                    st.write(f"**File Size:** {log_details.get('FileSize', 0):,} bytes")
                    st.write(f"**Created:** {log_details['CreatedAt'][:19] if log_details.get('CreatedAt') else 'N/A'}")
                    st.write(f"**Solution Available:** {'✅ Yes' if log_details.get('SolutionPossible') else '❌ No'}")
                
                st.write(f"**Description:**")
                st.write(log_details['Description'])
                
                # Log content preview
                if log_details.get('LogContent'):
                    with st.expander("📄 Log File Content", expanded=False):
                        st.text_area(
                            "File Content", 
                            log_details['LogContent'][:2000] + ('...' if len(log_details['LogContent']) > 2000 else ''),
                            height=300
                        )
                
                # AI Analysis sections (placeholders)
                st.subheader("🤖 AI Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🧠 AI Summary**")
                    if report.get('ai_summary') and report['ai_summary'].get('success'):
                        st.info(report['ai_summary']['summary'])
                        st.caption(f"Confidence: {report['ai_summary']['confidence']*100:.1f}%")
                    else:
                        st.warning("AI summary not available (placeholder)")
                
                with col2:
                    st.markdown("**🔍 Similar Logs**")
                    if report.get('similar_logs') and report['similar_logs'].get('success'):
                        similar_count = len(report['similar_logs'].get('similar_logs', []))
                        st.info(f"Found {similar_count} similar logs")
                    else:
                        st.warning("Similarity analysis not available (placeholder)")
                
                # Solution suggestions
                st.subheader("💡 Suggested Solutions")
                if report.get('suggested_solutions') and report['suggested_solutions'].get('success'):
                    solutions = report['suggested_solutions']['solutions']
                    for i, solution in enumerate(solutions, 1):
                        st.write(f"**{i}.** {solution}")
                    st.caption(f"Confidence: {report['suggested_solutions']['confidence']*100:.1f}%")
                else:
                    st.warning("Solution suggestions not available (placeholder)")
            
            else:
                display_error_message(f"Failed to load report: {response_data.get('message', 'Unknown error')}")
                if st.button("← Back to Search"):
                    st.session_state.current_page = "Search"
                    st.experimental_rerun()
    
    else:
        st.title("📊 Recent Reports")
        st.markdown("View recent error log reports and analytics.")
        
        # Load recent logs
        with st.spinner("Loading recent reports..."):
            response_data, status_code = make_api_request("/logs/", data={'per_page': 10})
            
            if status_code == 200 and response_data.get('success'):
                logs = response_data['data']
                
                if logs:
                    st.subheader("📋 Recent Reports")
                    for log in logs:
                        display_log_card(log)
                else:
                    st.info("No reports available.")
            else:
                display_error_message("Failed to load reports")

elif st.session_state.current_page == "Dashboard":
    st.title("📊 Analytics Dashboard")
    st.markdown("Overview of system statistics and error log analytics.")
    
    # Load statistics
    with st.spinner("Loading dashboard data..."):
        stats_data, status_code = make_api_request("/statistics")
        
        if status_code == 200 and stats_data.get('success'):
            stats = stats_data['data']
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Error Logs",
                    value=stats.get('total_logs', 0),
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="Logs with Solutions",
                    value=stats.get('logs_with_solutions', 0),
                    delta=None
                )
            
            with col3:
                solution_rate = stats.get('solution_rate', 0)
                st.metric(
                    label="Solution Rate",
                    value=f"{solution_rate:.1f}%",
                    delta=None
                )
            
            with col4:
                st.metric(
                    label="Active Teams",
                    value=len(stats.get('team_stats', [])),
                    delta=None
                )
            
            # Charts
            col1, col2 = st.columns(2)
            
            # Team distribution chart
            if stats.get('team_stats'):
                with col1:
                    st.subheader("👥 Logs by Team")
                    team_df = pd.DataFrame(stats['team_stats'])
                    fig = px.pie(team_df, values='count', names='team', title="Distribution by Team")
                    st.plotly_chart(fig, use_container_width=True)
            
            # Module distribution chart
            if stats.get('module_stats'):
                with col2:
                    st.subheader("🔧 Logs by Module")
                    module_df = pd.DataFrame(stats['module_stats'])
                    fig = px.bar(module_df, x='module', y='count', title="Distribution by Module")
                    fig.update_xaxes(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Solution rate visualization
            st.subheader("📈 Solution Analysis")
            solution_data = {
                'Category': ['With Solutions', 'Without Solutions'],
                'Count': [stats.get('logs_with_solutions', 0), 
                         stats.get('total_logs', 0) - stats.get('logs_with_solutions', 0)]
            }
            solution_df = pd.DataFrame(solution_data)
            
            fig = go.Figure(data=[
                go.Bar(name='Logs', x=solution_df['Category'], y=solution_df['Count'])
            ])
            fig.update_layout(title="Logs by Solution Status")
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            display_error_message("Failed to load dashboard data")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        <p>BugSeek v1.0 - Professional Error Log Management System</p>
        <p>Built with ❤️ using Streamlit and Flask</p>
    </div>
    """,
    unsafe_allow_html=True
)
