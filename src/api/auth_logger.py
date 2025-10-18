"""
Authentication logging system to track enrollment and authentication attempts.
"""
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
import re

class AuthLogger:
    def __init__(self, db_path='auth_logs.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the authentication logs database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enrollment logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrollment_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password_strength TEXT,
                enrollment_file TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN,
                user_id INTEGER
            )
        ''')
        
        # Authentication logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authentication_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                auth_file TEXT,
                score REAL,
                calibrated_prob REAL,
                spoof_score REAL,
                is_spoof BOOLEAN,
                authenticated BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def check_password_strength(self, password):
        """
        Check password strength and return rating.
        
        Returns:
            str: 'Weak', 'Medium', 'Strong', or 'Very Strong'
        """
        score = 0
        
        # Length check
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        # Character variety
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'[0-9]', password):
            score += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        
        if score <= 2:
            return 'Weak'
        elif score <= 4:
            return 'Medium'
        elif score <= 6:
            return 'Strong'
        else:
            return 'Very Strong'
    
    def log_enrollment(self, username, password, enrollment_file, success, user_id=None):
        """
        Log an enrollment attempt.
        
        Args:
            username: Username
            password: Plain password (for strength check only, not stored)
            enrollment_file: Name of the EEG file used
            success: Whether enrollment succeeded
            user_id: User ID if successful
        """
        strength = self.check_password_strength(password)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO enrollment_logs 
            (username, password_strength, enrollment_file, success, user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, strength, enrollment_file, success, user_id))
        
        conn.commit()
        conn.close()
    
    def log_authentication(self, username, auth_file, score, calibrated_prob, 
                          spoof_score, is_spoof, authenticated, message):
        """
        Log an authentication attempt.
        
        Args:
            username: Username attempting to authenticate
            auth_file: Name of the EEG file used
            score: Raw similarity score
            calibrated_prob: Calibrated probability
            spoof_score: Spoof detection score
            is_spoof: Whether spoof was detected
            authenticated: Whether authentication succeeded
            message: Result message
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO authentication_logs 
            (username, auth_file, score, calibrated_prob, spoof_score, 
             is_spoof, authenticated, message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, auth_file, score, calibrated_prob, spoof_score, 
              is_spoof, authenticated, message))
        
        conn.commit()
        conn.close()
    
    def get_enrollment_history(self, username=None):
        """Get enrollment history, optionally filtered by username."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if username:
            cursor.execute('''
                SELECT * FROM enrollment_logs 
                WHERE username = ?
                ORDER BY timestamp DESC
            ''', (username,))
        else:
            cursor.execute('''
                SELECT * FROM enrollment_logs 
                ORDER BY timestamp DESC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return rows
    
    def get_authentication_history(self, username=None):
        """Get authentication history, optionally filtered by username."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if username:
            cursor.execute('''
                SELECT * FROM authentication_logs 
                WHERE username = ?
                ORDER BY timestamp DESC
            ''', (username,))
        else:
            cursor.execute('''
                SELECT * FROM authentication_logs 
                ORDER BY timestamp DESC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return rows
    
    def get_user_stats(self, username):
        """Get statistics for a specific user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enrollment info
        cursor.execute('''
            SELECT password_strength, enrollment_file, timestamp
            FROM enrollment_logs
            WHERE username = ? AND success = 1
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (username,))
        enrollment = cursor.fetchone()
        
        # Authentication stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_attempts,
                SUM(CASE WHEN authenticated = 1 THEN 1 ELSE 0 END) as successful,
                AVG(score) as avg_score,
                MAX(score) as max_score,
                MIN(score) as min_score
            FROM authentication_logs
            WHERE username = ?
        ''', (username,))
        auth_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'enrollment': enrollment,
            'auth_stats': auth_stats
        }
    
    def export_to_csv(self, output_file='auth_logs.csv'):
        """Export all logs to CSV file."""
        import csv
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all authentication logs
        cursor.execute('''
            SELECT 
                a.username,
                e.password_strength,
                e.enrollment_file,
                a.auth_file,
                a.score,
                a.calibrated_prob,
                a.authenticated,
                a.timestamp
            FROM authentication_logs a
            LEFT JOIN enrollment_logs e ON a.username = e.username
            ORDER BY a.timestamp DESC
        ''')
        
        rows = cursor.fetchall()
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Username', 'Password Strength', 'Enrollment File', 
                'Auth File', 'Score', 'Calibrated Prob', 'Authenticated', 'Timestamp'
            ])
            writer.writerows(rows)
        
        conn.close()
        print(f"Exported {len(rows)} records to {output_file}")
