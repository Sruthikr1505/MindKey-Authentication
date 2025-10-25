#!/usr/bin/env python3
"""
Web dashboard to view all enrollment and authentication data
"""

from flask import Flask, render_template_string, jsonify, request
import sqlite3
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Create enhanced logger if it doesn't exist
class SimpleAuthLogger:
    def __init__(self, db_path='enhanced_auth_logs.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                num_trials INTEGER,
                enrollment_success BOOLEAN,
                prototype_strength REAL,
                enrollment_confidence REAL,
                notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authentications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                authenticated BOOLEAN,
                similarity_score REAL,
                calibrated_probability REAL,
                spoof_detected BOOLEAN,
                decision_reason TEXT,
                confidence_level TEXT,
                processing_time_ms REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS impostor_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                auth_id INTEGER,
                impostor_type TEXT,
                detection_confidence REAL,
                behavioral_anomalies TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (auth_id) REFERENCES authentications (id)
            )
        ''')
        
        conn.commit()
        conn.close()

enhanced_logger = SimpleAuthLogger()

# HTML Template for the dashboard
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>EEG Authentication Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .stat-box { background: #007bff; color: white; padding: 15px; border-radius: 5px; text-align: center; }
        .success { background: #28a745; }
        .danger { background: #dc3545; }
        .warning { background: #ffc107; color: black; }
        .table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .table th, .table td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        .table th { background: #f8f9fa; }
        .authenticated { color: #28a745; font-weight: bold; }
        .rejected { color: #dc3545; font-weight: bold; }
        .high-conf { background: #d4edda; }
        .medium-conf { background: #fff3cd; }
        .low-conf { background: #f8d7da; }
        .search-box { padding: 10px; margin: 10px 0; width: 300px; border: 1px solid #ddd; border-radius: 4px; }
        .filter-buttons { margin: 10px 0; }
        .filter-btn { padding: 8px 15px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }
        .active { background: #007bff; color: white; }
        .refresh-btn { background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 EEG Authentication Dashboard</h1>
        
        <!-- System Statistics -->
        <div class="card">
            <h2>📊 System Statistics</h2>
            <div class="stats" id="stats">
                <!-- Stats will be loaded here -->
            </div>
        </div>
        
        <!-- Controls -->
        <div class="card">
            <h2>🔍 Filters & Search</h2>
            <input type="text" id="searchUser" class="search-box" placeholder="Search by username...">
            <div class="filter-buttons">
                <button class="filter-btn active" onclick="filterData('all')">All</button>
                <button class="filter-btn" onclick="filterData('authenticated')">Authenticated</button>
                <button class="filter-btn" onclick="filterData('rejected')">Rejected</button>
                <button class="filter-btn" onclick="filterData('impostors')">Impostors</button>
                <button class="filter-btn" onclick="filterData('high-conf')">High Confidence</button>
            </div>
            <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
        </div>
        
        <!-- Recent Authentications -->
        <div class="card">
            <h2>🔐 Recent Authentication Attempts</h2>
            <div id="authTable">
                <!-- Authentication table will be loaded here -->
            </div>
        </div>
        
        <!-- Enrollments -->
        <div class="card">
            <h2>📝 User Enrollments</h2>
            <div id="enrollTable">
                <!-- Enrollment table will be loaded here -->
            </div>
        </div>
        
        <!-- Impostor Analysis -->
        <div class="card">
            <h2>🚫 Impostor Detection Analysis</h2>
            <div id="impostorTable">
                <!-- Impostor analysis will be loaded here -->
            </div>
        </div>
    </div>

    <script>
        let allData = {};
        let currentFilter = 'all';
        
        async function loadData() {
            try {
                const response = await fetch('/api/dashboard-data');
                allData = await response.json();
                updateStats(allData.stats);
                updateTables();
            } catch (error) {
                console.error('Error loading data:', error);
            }
        }
        
        function updateStats(stats) {
            const statsHtml = `
                <div class="stat-box">
                    <h3>${stats.total_enrollments}</h3>
                    <p>Total Enrollments</p>
                </div>
                <div class="stat-box">
                    <h3>${stats.total_authentications}</h3>
                    <p>Total Attempts</p>
                </div>
                <div class="stat-box success">
                    <h3>${stats.successful_authentications}</h3>
                    <p>Successful Auths</p>
                </div>
                <div class="stat-box danger">
                    <h3>${stats.failed_authentications}</h3>
                    <p>Failed Auths</p>
                </div>
                <div class="stat-box warning">
                    <h3>${stats.success_rate_percent.toFixed(1)}%</h3>
                    <p>Success Rate</p>
                </div>
                <div class="stat-box">
                    <h3>${stats.average_similarity_score.toFixed(3)}</h3>
                    <p>Avg Similarity</p>
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
                            <th>Timestamp</th>
                            <th>Username</th>
                            <th>Result</th>
                            <th>Similarity</th>
                            <th>Probability</th>
                            <th>Confidence</th>
                            <th>Reason</th>
                            <th>Spoof</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${auths.map(auth => `
                            <tr class="${auth.confidence_level.toLowerCase()}-conf">
                                <td>${new Date(auth.timestamp).toLocaleString()}</td>
                                <td>${auth.username}</td>
                                <td class="${auth.authenticated ? 'authenticated' : 'rejected'}">
                                    ${auth.authenticated ? '✅ AUTH' : '❌ REJECT'}
                                </td>
                                <td>${auth.similarity_score.toFixed(3)}</td>
                                <td>${auth.calibrated_probability.toFixed(3)}</td>
                                <td>${auth.confidence_level}</td>
                                <td>${auth.decision_reason}</td>
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
                            <th>Timestamp</th>
                            <th>Username</th>
                            <th>Success</th>
                            <th>Trials</th>
                            <th>Prototype Strength</th>
                            <th>Confidence</th>
                            <th>Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${enrolls.map(enroll => `
                            <tr>
                                <td>${new Date(enroll.timestamp).toLocaleString()}</td>
                                <td>${enroll.username}</td>
                                <td class="${enroll.enrollment_success ? 'authenticated' : 'rejected'}">
                                    ${enroll.enrollment_success ? '✅ SUCCESS' : '❌ FAILED'}
                                </td>
                                <td>${enroll.num_trials}</td>
                                <td>${enroll.prototype_strength.toFixed(3)}</td>
                                <td>${enroll.enrollment_confidence.toFixed(3)}</td>
                                <td>${enroll.notes || 'N/A'}</td>
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
                            <th>Timestamp</th>
                            <th>Auth ID</th>
                            <th>Impostor Type</th>
                            <th>Detection Confidence</th>
                            <th>Behavioral Anomalies</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${impostors.map(imp => `
                            <tr>
                                <td>${new Date(imp.timestamp).toLocaleString()}</td>
                                <td>${imp.auth_id}</td>
                                <td>${imp.impostor_type}</td>
                                <td>${(imp.detection_confidence * 100).toFixed(1)}%</td>
                                <td>${JSON.parse(imp.behavioral_anomalies).join(', ')}</td>
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
                // Search filter
                if (searchTerm && !auth.username.toLowerCase().includes(searchTerm)) {
                    return false;
                }
                
                // Category filter
                switch (currentFilter) {
                    case 'authenticated':
                        return auth.authenticated;
                    case 'rejected':
                        return !auth.authenticated;
                    case 'impostors':
                        return !auth.authenticated && auth.calibrated_probability < 0.3;
                    case 'high-conf':
                        return auth.confidence_level === 'HIGH';
                    default:
                        return true;
                }
            });
        }
        
        function filterData(filter) {
            currentFilter = filter;
            
            // Update button states
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            updateTables();
        }
        
        // Search functionality
        document.getElementById('searchUser').addEventListener('input', updateTables);
        
        // Load data on page load
        loadData();
        
        // Auto-refresh every 30 seconds
        setInterval(loadData, 30000);
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """Get all dashboard data"""
    try:
        conn = sqlite3.connect('enhanced_auth_logs.db')
        cursor = conn.cursor()
        
        # Get recent authentications
        cursor.execute('''
            SELECT * FROM authentications 
            ORDER BY timestamp DESC 
            LIMIT 100
        ''')
        authentications = [dict(zip([col[0] for col in cursor.description], row)) 
                          for row in cursor.fetchall()]
        
        # Get enrollments
        cursor.execute('''
            SELECT * FROM enrollments 
            ORDER BY timestamp DESC 
            LIMIT 50
        ''')
        enrollments = [dict(zip([col[0] for col in cursor.description], row)) 
                      for row in cursor.fetchall()]
        
        # Get impostor analyses
        cursor.execute('''
            SELECT * FROM impostor_analysis 
            ORDER BY timestamp DESC 
            LIMIT 50
        ''')
        impostor_analyses = [dict(zip([col[0] for col in cursor.description], row)) 
                           for row in cursor.fetchall()]
        
        conn.close()
        
        # Get system stats
        stats = enhanced_logger.get_system_stats()
        
        return jsonify({
            'stats': stats,
            'authentications': authentications,
            'enrollments': enrollments,
            'impostor_analyses': impostor_analyses
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting EEG Authentication Dashboard...")
    print("📊 Dashboard URL: http://localhost:5000")
    print("🔄 Auto-refreshes every 30 seconds")
    app.run(debug=True, port=5000)
