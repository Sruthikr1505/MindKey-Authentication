"""
Admin routes for viewing enrollment and authentication data
"""

from fastapi import APIRouter, HTTPException
import sqlite3
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["admin"])

def get_db_connection():
    """Get database connection"""
    try:
        conn = sqlite3.connect('enhanced_auth_logs.db')
        return conn
    except:
        # Fallback to regular auth logs if enhanced doesn't exist
        conn = sqlite3.connect('auth_logs.db')
        return conn

@router.get("/dashboard-data")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Try enhanced database first
        try:
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
            
            # Calculate stats
            cursor.execute('SELECT COUNT(*) FROM enrollments')
            total_enrollments = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM authentications')
            total_authentications = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM authentications WHERE authenticated = 1')
            successful_auths = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM authentications WHERE authenticated = 0')
            failed_auths = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(similarity_score), AVG(calibrated_probability) FROM authentications')
            avg_scores = cursor.fetchone()
            
        except sqlite3.OperationalError:
            # Fallback to basic auth logs
            cursor.execute('SELECT * FROM auth_logs ORDER BY timestamp DESC LIMIT 100')
            basic_logs = cursor.fetchall()
            
            # Convert basic logs to enhanced format
            authentications = []
            for log in basic_logs:
                authentications.append({
                    'id': log[0],
                    'username': log[1],
                    'timestamp': log[2],
                    'authenticated': log[3] == 'SUCCESS',
                    'similarity_score': 0.5,  # Default values
                    'calibrated_probability': 0.5,
                    'spoof_detected': False,
                    'decision_reason': f"Basic log: {log[3]}",
                    'confidence_level': 'MEDIUM'
                })
            
            enrollments = []
            impostor_analyses = []
            total_enrollments = 0
            total_authentications = len(authentications)
            successful_auths = len([a for a in authentications if a['authenticated']])
            failed_auths = total_authentications - successful_auths
            avg_scores = (0.5, 0.5)
        
        conn.close()
        
        success_rate = (successful_auths / total_authentications * 100) if total_authentications > 0 else 0
        
        stats = {
            'total_enrollments': total_enrollments,
            'total_authentications': total_authentications,
            'successful_authentications': successful_auths,
            'failed_authentications': failed_auths,
            'success_rate_percent': success_rate,
            'failure_rate_percent': 100 - success_rate,
            'average_similarity_score': avg_scores[0] or 0,
            'average_probability': avg_scores[1] or 0
        }
        
        return {
            'stats': stats,
            'authentications': authentications,
            'enrollments': enrollments,
            'impostor_analyses': impostor_analyses
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/user-history/{username}")
async def get_user_history(username: str):
    """Get complete history for a specific user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user authentications
        cursor.execute('''
            SELECT * FROM authentications WHERE username = ? ORDER BY timestamp DESC
        ''', (username,))
        authentications = [dict(zip([col[0] for col in cursor.description], row)) 
                          for row in cursor.fetchall()]
        
        # Get user enrollments
        cursor.execute('''
            SELECT * FROM enrollments WHERE username = ? ORDER BY timestamp DESC
        ''', (username,))
        enrollments = [dict(zip([col[0] for col in cursor.description], row)) 
                      for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'username': username,
            'authentications': authentications,
            'enrollments': enrollments,
            'total_attempts': len(authentications),
            'successful_auths': len([a for a in authentications if a.get('authenticated', False)]),
            'failed_auths': len([a for a in authentications if not a.get('authenticated', False)])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/system-performance")
async def get_system_performance():
    """Get system performance metrics over time"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get performance over last 24 hours
        cursor.execute('''
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as total_attempts,
                SUM(CASE WHEN authenticated = 1 THEN 1 ELSE 0 END) as successful,
                AVG(similarity_score) as avg_similarity,
                AVG(calibrated_probability) as avg_probability
            FROM authentications 
            WHERE timestamp >= datetime('now', '-24 hours')
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''')
        
        performance_data = [dict(zip([col[0] for col in cursor.description], row)) 
                           for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'performance_data': performance_data,
            'period': '24_hours'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/impostor-analysis")
async def get_impostor_analysis():
    """Get detailed impostor detection analysis"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get impostor statistics
        cursor.execute('''
            SELECT 
                impostor_type,
                COUNT(*) as count,
                AVG(detection_confidence) as avg_confidence
            FROM impostor_analysis 
            GROUP BY impostor_type
        ''')
        
        impostor_stats = [dict(zip([col[0] for col in cursor.description], row)) 
                         for row in cursor.fetchall()]
        
        # Get recent impostor attempts
        cursor.execute('''
            SELECT ia.*, a.username, a.similarity_score, a.calibrated_probability
            FROM impostor_analysis ia
            JOIN authentications a ON ia.auth_id = a.id
            ORDER BY ia.timestamp DESC
            LIMIT 50
        ''')
        
        recent_impostors = [dict(zip([col[0] for col in cursor.description], row)) 
                           for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'impostor_statistics': impostor_stats,
            'recent_attempts': recent_impostors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/export-data")
async def export_data(date_range: Dict[str, str] = None):
    """Export authentication data for analysis"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query based on date range
        if date_range and 'start_date' in date_range and 'end_date' in date_range:
            cursor.execute('''
                SELECT * FROM authentications 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (date_range['start_date'], date_range['end_date']))
        else:
            cursor.execute('SELECT * FROM authentications ORDER BY timestamp DESC')
        
        authentications = [dict(zip([col[0] for col in cursor.description], row)) 
                          for row in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM enrollments ORDER BY timestamp DESC')
        enrollments = [dict(zip([col[0] for col in cursor.description], row)) 
                      for row in cursor.fetchall()]
        
        conn.close()
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'date_range': date_range,
            'total_authentications': len(authentications),
            'total_enrollments': len(enrollments),
            'authentications': authentications,
            'enrollments': enrollments
        }
        
        return export_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")
