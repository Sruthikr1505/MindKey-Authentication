#!/usr/bin/env python3
"""
Standalone Admin Dashboard Server - Completely separate from existing frontend
Runs on port 9000 to avoid conflicts
"""

from flask import Flask, render_template_string, jsonify, request
import sqlite3
import json
from datetime import datetime, timedelta
from admin_api_integration import admin_logger

app = Flask(__name__)

# Enhanced HTML Template for Admin Dashboard
ADMIN_DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔐 EEG Authentication Admin Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.15);
            padding: 25px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover { transform: translateY(-5px); }
        
        .stat-card h3 {
            font-size: 2.2rem;
            margin-bottom: 5px;
            color: #4ecdc4;
        }
        
        .stat-card p {
            color: rgba(255,255,255,0.8);
            font-size: 0.9rem;
        }
        
        .controls {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
        }
        
        .search-box {
            padding: 12px 15px;
            border: none;
            border-radius: 8px;
            background: rgba(255,255,255,0.2);
            color: white;
            font-size: 14px;
            min-width: 250px;
        }
        
        .search-box::placeholder { color: rgba(255,255,255,0.7); }
        
        .filter-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            background: rgba(255,255,255,0.2);
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .filter-btn:hover { background: rgba(255,255,255,0.3); }
        .filter-btn.active { background: #4ecdc4; color: #1e3c72; }
        
        .refresh-btn {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            color: white;
            cursor: pointer;
            font-weight: bold;
            transition: transform 0.3s ease;
        }
        
        .refresh-btn:hover { transform: scale(1.05); }
        
        .data-section {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        
        .section-title {
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: #4ecdc4;
            border-bottom: 2px solid rgba(78, 205, 196, 0.3);
            padding-bottom: 10px;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            overflow: hidden;
        }
        
        .table th {
            background: rgba(78, 205, 196, 0.2);
            padding: 15px 10px;
            text-align: left;
            font-weight: 600;
            color: #4ecdc4;
        }
        
        .table td {
            padding: 12px 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .table tr:hover {
            background: rgba(255,255,255,0.1);
        }
        
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-success { background: #00b894; color: white; }
        .status-danger { background: #e17055; color: white; }
        .status-warning { background: #fdcb6e; color: #2d3436; }
        
        .confidence-high { background: rgba(0, 184, 148, 0.2); }
        .confidence-medium { background: rgba(253, 203, 110, 0.2); }
        .confidence-low { background: rgba(225, 112, 85, 0.2); }
        
        .reason-cell {
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            cursor: pointer;
        }
        
        .reason-cell:hover {
            white-space: normal;
            word-wrap: break-word;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            font-size: 1.2rem;
            color: rgba(255,255,255,0.7);
        }
        
        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top: 4px solid #4ecdc4;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .export-btn {
            background: linear-gradient(45deg, #00b894, #00cec9);
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            color: white;
            cursor: pointer;
            font-weight: bold;
            margin-left: auto;
        }
        
        .impostor-analysis {
            background: rgba(225, 112, 85, 0.1);
            border-left: 4px solid #e17055;
        }
        
        @media (max-width: 768px) {
            .stats-grid { grid-template-columns: 1fr; }
            .controls { flex-direction: column; align-items: stretch; }
            .table { font-size: 0.8rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🧠 EEG Authentication Admin Dashboard</h1>
            <p>Complete enrollment and authentication analytics with detailed reasoning</p>
            <p><strong>Exclusive Admin Interface</strong> - Separate from user dashboard</p>
        </div>
        
        <!-- Statistics -->
        <div class="stats-grid" id="stats">
            <div class="loading">
                <div class="spinner"></div>
                Loading statistics...
            </div>
        </div>
        
        <!-- Controls -->
        <div class="controls">
            <input type="text" id="searchUser" class="search-box" placeholder="🔍 Search by username...">
            
            <button class="filter-btn active" onclick="setFilter('all')">All</button>
            <button class="filter-btn" onclick="setFilter('authenticated')">✅ Authenticated</button>
            <button class="filter-btn" onclick="setFilter('rejected')">❌ Rejected</button>
            <button class="filter-btn" onclick="setFilter('impostors')">🚫 Impostors</button>
            <button class="filter-btn" onclick="setFilter('high-conf')">🎯 High Confidence</button>
            <button class="filter-btn" onclick="setFilter('spoof')">🚨 Spoof Detected</button>
            
            <button class="refresh-btn" onclick="loadData()">🔄 Refresh</button>
            <button class="export-btn" onclick="exportData()">📥 Export Data</button>
        </div>
        
        <!-- Authentication Attempts -->
        <div class="data-section">
            <h2 class="section-title">🔐 Authentication Attempts with Detailed Reasoning</h2>
            <div id="authTable">
                <div class="loading">
                    <div class="spinner"></div>
                    Loading authentication data...
                </div>
            </div>
        </div>
        
        <!-- Enrollments -->
        <div class="data-section">
            <h2 class="section-title">📝 User Enrollments</h2>
            <div id="enrollTable">
                <div class="loading">Loading enrollment data...</div>
            </div>
        </div>
        
        <!-- Impostor Analysis -->
        <div class="data-section impostor-analysis">
            <h2 class="section-title">🚫 Impostor Detection Analysis</h2>
            <div id="impostorTable">
                <div class="loading">Loading impostor analysis...</div>
            </div>
        </div>
    </div>

    <script>
        let allData = {};
        let currentFilter = 'all';
        
        async function loadData() {
            try {
                console.log('Loading admin dashboard data...');
                const response = await fetch('/api/admin-data');
                allData = await response.json();
                
                updateStats(allData.stats);
                updateTables();
                
                console.log('Data loaded successfully:', allData);
            } catch (error) {
                console.error('Error loading data:', error);
                document.getElementById('stats').innerHTML = '<div class="loading">❌ Error loading data</div>';
            }
        }
        
        function updateStats(stats) {
            const statsHtml = `
                <div class="stat-card">
                    <h3>${stats.total_enrollments}</h3>
                    <p>👥 Total Enrollments</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.total_authentications}</h3>
                    <p>🔐 Total Attempts</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.successful_authentications}</h3>
                    <p>✅ Successful Auths</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.failed_authentications}</h3>
                    <p>❌ Failed Auths</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.success_rate_percent.toFixed(1)}%</h3>
                    <p>📈 Success Rate</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.total_impostors_detected}</h3>
                    <p>🚫 Impostors Detected</p>
                </div>
            `;
            document.getElementById('stats').innerHTML = statsHtml;
        }
        
        function updateTables() {
            updateAuthTable();
            updateEnrollTable();
            updateImpostorTable();
        }
        
        function updateAuthTable() {
            const auths = filterAuthentications(allData.authentications || []);
            const tableHtml = `
                <table class="table">
                    <thead>
                        <tr>
                            <th>⏰ Timestamp</th>
                            <th>👤 Username</th>
                            <th>🎯 Result</th>
                            <th>📊 Similarity</th>
                            <th>🎲 Probability</th>
                            <th>🔒 Confidence</th>
                            <th>💭 Detailed Reasoning</th>
                            <th>🚨 Spoof</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${auths.map(auth => `
                            <tr class="confidence-${auth.confidence_level?.toLowerCase() || 'medium'}">
                                <td>${new Date(auth.timestamp).toLocaleString()}</td>
                                <td><strong>${auth.username}</strong></td>
                                <td>
                                    <span class="status-badge ${auth.authenticated ? 'status-success' : 'status-danger'}">
                                        ${auth.authenticated ? '✅ AUTH' : '❌ REJECT'}
                                    </span>
                                </td>
                                <td>${auth.similarity_score?.toFixed(3) || 'N/A'}</td>
                                <td>${auth.calibrated_probability?.toFixed(3) || 'N/A'}</td>
                                <td>
                                    <span class="status-badge ${
                                        auth.confidence_level === 'HIGH' ? 'status-success' :
                                        auth.confidence_level === 'MEDIUM' ? 'status-warning' : 'status-danger'
                                    }">
                                        ${auth.confidence_level || 'MEDIUM'}
                                    </span>
                                </td>
                                <td class="reason-cell" title="${auth.decision_reason || 'No reason provided'}">
                                    ${auth.decision_reason || 'No detailed reasoning available'}
                                </td>
                                <td>${auth.spoof_detected ? '🚨 YES' : '✅ NO'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            document.getElementById('authTable').innerHTML = tableHtml;
        }
        
        function updateEnrollTable() {
            const enrolls = allData.enrollments || [];
            const tableHtml = `
                <table class="table">
                    <thead>
                        <tr>
                            <th>⏰ Timestamp</th>
                            <th>👤 Username</th>
                            <th>🎯 Success</th>
                            <th>📊 Trials</th>
                            <th>💪 Prototype Strength</th>
                            <th>🔒 Confidence</th>
                            <th>📝 Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${enrolls.map(enroll => `
                            <tr>
                                <td>${new Date(enroll.timestamp).toLocaleString()}</td>
                                <td><strong>${enroll.username}</strong></td>
                                <td>
                                    <span class="status-badge ${enroll.enrollment_success ? 'status-success' : 'status-danger'}">
                                        ${enroll.enrollment_success ? '✅ SUCCESS' : '❌ FAILED'}
                                    </span>
                                </td>
                                <td>${enroll.num_trials || 0}</td>
                                <td>${enroll.prototype_strength?.toFixed(3) || 'N/A'}</td>
                                <td>${enroll.enrollment_confidence?.toFixed(3) || 'N/A'}</td>
                                <td>${enroll.notes || enroll.error_message || 'N/A'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            document.getElementById('enrollTable').innerHTML = tableHtml;
        }
        
        function updateImpostorTable() {
            const impostors = allData.impostor_analyses || [];
            const tableHtml = `
                <table class="table">
                    <thead>
                        <tr>
                            <th>⏰ Timestamp</th>
                            <th>👤 Username</th>
                            <th>🎭 Impostor Type</th>
                            <th>🎯 Detection Confidence</th>
                            <th>🧠 Neural Analysis</th>
                            <th>⚠️ Behavioral Anomalies</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${impostors.map(imp => `
                            <tr>
                                <td>${new Date(imp.timestamp).toLocaleString()}</td>
                                <td><strong>${imp.username}</strong></td>
                                <td>
                                    <span class="status-badge status-danger">
                                        ${imp.impostor_type?.replace('_', ' ') || 'UNKNOWN'}
                                    </span>
                                </td>
                                <td>${(imp.detection_confidence * 100).toFixed(1)}%</td>
                                <td class="reason-cell" title="${imp.neural_pattern_analysis || 'No analysis'}">
                                    ${imp.neural_pattern_analysis || 'No neural analysis available'}
                                </td>
                                <td class="reason-cell" title="${imp.behavioral_anomalies || 'No anomalies'}">
                                    ${imp.behavioral_anomalies ? JSON.parse(imp.behavioral_anomalies).join(', ') : 'No anomalies detected'}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            document.getElementById('impostorTable').innerHTML = tableHtml;
        }
        
        function filterAuthentications(auths) {
            const searchTerm = document.getElementById('searchUser').value.toLowerCase();
            
            return auths.filter(auth => {
                if (searchTerm && !auth.username.toLowerCase().includes(searchTerm)) {
                    return false;
                }
                
                switch (currentFilter) {
                    case 'authenticated':
                        return auth.authenticated;
                    case 'rejected':
                        return !auth.authenticated;
                    case 'impostors':
                        return !auth.authenticated && auth.calibrated_probability < 0.3;
                    case 'high-conf':
                        return auth.confidence_level === 'HIGH';
                    case 'spoof':
                        return auth.spoof_detected;
                    default:
                        return true;
                }
            });
        }
        
        function setFilter(filter) {
            currentFilter = filter;
            
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            updateTables();
        }
        
        function exportData() {
            const dataToExport = {
                export_timestamp: new Date().toISOString(),
                stats: allData.stats,
                authentications: allData.authentications,
                enrollments: allData.enrollments,
                impostor_analyses: allData.impostor_analyses
            };
            
            const blob = new Blob([JSON.stringify(dataToExport, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `eeg_admin_data_${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            alert('📥 Admin data exported successfully!');
        }
        
        // Search functionality
        document.getElementById('searchUser').addEventListener('input', updateTables);
        
        // Load data on page load
        loadData();
        
        // Auto-refresh every 30 seconds
        setInterval(loadData, 30000);
        
        console.log('🚀 Admin Dashboard initialized');
    </script>
</body>
</html>
'''

@app.route('/')
def admin_dashboard():
    """Main admin dashboard page"""
    return render_template_string(ADMIN_DASHBOARD_HTML)

@app.route('/api/admin-data')
def get_admin_data():
    """Get all admin data"""
    try:
        conn = sqlite3.connect('admin_auth_logs.db')
        cursor = conn.cursor()
        
        # Get recent authentications
        cursor.execute('''
            SELECT * FROM admin_authentications 
            ORDER BY timestamp DESC 
            LIMIT 100
        ''')
        authentications = [dict(zip([col[0] for col in cursor.description], row)) 
                          for row in cursor.fetchall()]
        
        # Get enrollments
        cursor.execute('''
            SELECT * FROM admin_enrollments 
            ORDER BY timestamp DESC 
            LIMIT 50
        ''')
        enrollments = [dict(zip([col[0] for col in cursor.description], row)) 
                      for row in cursor.fetchall()]
        
        # Get impostor analyses
        cursor.execute('''
            SELECT * FROM admin_impostor_analysis 
            ORDER BY timestamp DESC 
            LIMIT 50
        ''')
        impostor_analyses = [dict(zip([col[0] for col in cursor.description], row)) 
                           for row in cursor.fetchall()]
        
        conn.close()
        
        # Get stats
        stats = admin_logger.get_admin_stats()
        
        return jsonify({
            'stats': stats,
            'authentications': authentications,
            'enrollments': enrollments,
            'impostor_analyses': impostor_analyses
        })
        
    except Exception as e:
        print(f"❌ Admin API Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user-details/<username>')
def get_user_details(username):
    """Get detailed information for a specific user"""
    try:
        conn = sqlite3.connect('admin_auth_logs.db')
        cursor = conn.cursor()
        
        # Get user authentications
        cursor.execute('''
            SELECT * FROM admin_authentications 
            WHERE username = ? 
            ORDER BY timestamp DESC
        ''', (username,))
        authentications = [dict(zip([col[0] for col in cursor.description], row)) 
                          for row in cursor.fetchall()]
        
        # Get user enrollments
        cursor.execute('''
            SELECT * FROM admin_enrollments 
            WHERE username = ? 
            ORDER BY timestamp DESC
        ''', (username,))
        enrollments = [dict(zip([col[0] for col in cursor.description], row)) 
                      for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'username': username,
            'authentications': authentications,
            'enrollments': enrollments,
            'total_attempts': len(authentications),
            'successful_auths': len([a for a in authentications if a['authenticated']]),
            'failed_auths': len([a for a in authentications if not a['authenticated']])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting EXCLUSIVE Admin Dashboard Server...")
    print("📊 Admin Dashboard: http://localhost:9000")
    print("🔒 Completely separate from existing user frontend")
    print("📈 Real-time authentication tracking with detailed reasoning")
    print("🚫 Advanced impostor detection analysis")
    print("=" * 60)
    
    # Initialize sample data if database is empty
    try:
        stats = admin_logger.get_admin_stats()
        if stats['total_authentications'] == 0:
            print("📊 No data found, populating sample data...")
            from admin_api_integration import populate_sample_data
            populate_sample_data()
    except:
        pass
    
    app.run(debug=True, port=9000, host='0.0.0.0')
