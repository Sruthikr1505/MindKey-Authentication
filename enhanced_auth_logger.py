#!/usr/bin/env python3
"""
Enhanced authentication logger with detailed tracking and reasoning
"""

import sqlite3
import json
import datetime
import os
from typing import Dict, Any, Optional

class EnhancedAuthLogger:
    def __init__(self, db_path: str = 'enhanced_auth_logs.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize enhanced database with detailed tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced enrollment table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                num_trials INTEGER,
                trial_quality_scores TEXT,  -- JSON array of quality scores
                enrollment_success BOOLEAN,
                prototype_strength REAL,    -- How strong the prototype is
                enrollment_confidence REAL, -- Confidence in enrollment quality
                notes TEXT,
                ip_address TEXT,
                user_agent TEXT
            )
        ''')
        
        # Enhanced authentication table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authentications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                authenticated BOOLEAN,
                similarity_score REAL,
                calibrated_probability REAL,
                spoof_detected BOOLEAN,
                spoof_score REAL,
                decision_reason TEXT,       -- Why authenticated/rejected
                confidence_level TEXT,      -- HIGH/MEDIUM/LOW
                trial_quality REAL,        -- Quality of probe trial
                embedding_distance REAL,   -- Distance from prototype
                threshold_used REAL,       -- Authentication threshold
                processing_time_ms REAL,   -- Time taken for authentication
                ip_address TEXT,
                user_agent TEXT,
                explain_id TEXT,           -- For explainability
                additional_data TEXT       -- JSON for extra info
            )
        ''')
        
        # Impostor analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS impostor_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                auth_id INTEGER,
                is_genuine_user BOOLEAN,
                actual_user_if_known TEXT,
                impostor_type TEXT,        -- RANDOM, TARGETED, REPLAY
                detection_confidence REAL,
                behavioral_anomalies TEXT, -- JSON array of anomalies detected
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (auth_id) REFERENCES authentications (id)
            )
        ''')
        
        # System performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_enrollments INTEGER,
                total_authentications INTEGER,
                genuine_acceptance_rate REAL,
                false_acceptance_rate REAL,
                false_rejection_rate REAL,
                average_processing_time REAL,
                system_load REAL,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_enrollment(self, username: str, enrollment_data: Dict[str, Any]) -> int:
        """Log detailed enrollment information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO enrollments (
                username, num_trials, trial_quality_scores, enrollment_success,
                prototype_strength, enrollment_confidence, notes, ip_address, user_agent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            enrollment_data.get('num_trials', 0),
            json.dumps(enrollment_data.get('trial_quality_scores', [])),
            enrollment_data.get('success', False),
            enrollment_data.get('prototype_strength', 0.0),
            enrollment_data.get('enrollment_confidence', 0.0),
            enrollment_data.get('notes', ''),
            enrollment_data.get('ip_address', ''),
            enrollment_data.get('user_agent', '')
        ))
        
        enrollment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return enrollment_id
    
    def log_authentication(self, username: str, auth_data: Dict[str, Any]) -> int:
        """Log detailed authentication attempt with reasoning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Determine decision reason
        decision_reason = self._generate_decision_reason(auth_data)
        confidence_level = self._determine_confidence_level(auth_data)
        
        cursor.execute('''
            INSERT INTO authentications (
                username, authenticated, similarity_score, calibrated_probability,
                spoof_detected, spoof_score, decision_reason, confidence_level,
                trial_quality, embedding_distance, threshold_used, processing_time_ms,
                ip_address, user_agent, explain_id, additional_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            auth_data.get('authenticated', False),
            auth_data.get('similarity_score', 0.0),
            auth_data.get('calibrated_probability', 0.0),
            auth_data.get('spoof_detected', False),
            auth_data.get('spoof_score', 0.0),
            decision_reason,
            confidence_level,
            auth_data.get('trial_quality', 0.0),
            auth_data.get('embedding_distance', 0.0),
            auth_data.get('threshold_used', 0.5),
            auth_data.get('processing_time_ms', 0.0),
            auth_data.get('ip_address', ''),
            auth_data.get('user_agent', ''),
            auth_data.get('explain_id', ''),
            json.dumps(auth_data.get('additional_data', {}))
        ))
        
        auth_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Log impostor analysis if needed
        if not auth_data.get('authenticated', False):
            self._log_impostor_analysis(auth_id, auth_data)
        
        return auth_id
    
    def _generate_decision_reason(self, auth_data: Dict[str, Any]) -> str:
        """Generate human-readable reason for authentication decision"""
        authenticated = auth_data.get('authenticated', False)
        similarity = auth_data.get('similarity_score', 0.0)
        probability = auth_data.get('calibrated_probability', 0.0)
        spoof_detected = auth_data.get('spoof_detected', False)
        
        if spoof_detected:
            return f"REJECTED: Spoof detected (spoof_score={auth_data.get('spoof_score', 0):.4f})"
        
        if authenticated:
            if probability > 0.9:
                return f"AUTHENTICATED: Very high confidence (prob={probability:.3f}, sim={similarity:.3f})"
            elif probability > 0.7:
                return f"AUTHENTICATED: High confidence (prob={probability:.3f}, sim={similarity:.3f})"
            else:
                return f"AUTHENTICATED: Medium confidence (prob={probability:.3f}, sim={similarity:.3f})"
        else:
            if probability < 0.1:
                return f"REJECTED: Very low similarity (prob={probability:.3f}, sim={similarity:.3f}) - Likely impostor"
            elif probability < 0.3:
                return f"REJECTED: Low similarity (prob={probability:.3f}, sim={similarity:.3f}) - Possible impostor"
            else:
                return f"REJECTED: Below threshold (prob={probability:.3f}, sim={similarity:.3f}) - Uncertain identity"
    
    def _determine_confidence_level(self, auth_data: Dict[str, Any]) -> str:
        """Determine confidence level of the decision"""
        probability = auth_data.get('calibrated_probability', 0.0)
        
        if probability > 0.8 or probability < 0.2:
            return "HIGH"
        elif probability > 0.6 or probability < 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _log_impostor_analysis(self, auth_id: int, auth_data: Dict[str, Any]):
        """Log detailed impostor analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analyze impostor type
        similarity = auth_data.get('similarity_score', 0.0)
        probability = auth_data.get('calibrated_probability', 0.0)
        
        if probability < 0.05:
            impostor_type = "RANDOM"  # Very different brain patterns
            detection_confidence = 0.95
        elif probability < 0.2:
            impostor_type = "TARGETED"  # Some similarity but still different
            detection_confidence = 0.85
        else:
            impostor_type = "SOPHISTICATED"  # High similarity, harder to detect
            detection_confidence = 0.65
        
        behavioral_anomalies = []
        if auth_data.get('spoof_detected', False):
            behavioral_anomalies.append("Synthetic signal detected")
        if similarity < 0.3:
            behavioral_anomalies.append("Very different neural patterns")
        if auth_data.get('trial_quality', 1.0) < 0.5:
            behavioral_anomalies.append("Poor signal quality")
        
        cursor.execute('''
            INSERT INTO impostor_analysis (
                auth_id, is_genuine_user, impostor_type, detection_confidence,
                behavioral_anomalies
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            auth_id,
            False,  # This is called only for rejected attempts
            impostor_type,
            detection_confidence,
            json.dumps(behavioral_anomalies)
        ))
        
        conn.commit()
        conn.close()
    
    def get_user_history(self, username: str) -> Dict[str, Any]:
        """Get complete history for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get enrollment history
        cursor.execute('''
            SELECT * FROM enrollments WHERE username = ? ORDER BY timestamp DESC
        ''', (username,))
        enrollments = [dict(zip([col[0] for col in cursor.description], row)) 
                      for row in cursor.fetchall()]
        
        # Get authentication history
        cursor.execute('''
            SELECT * FROM authentications WHERE username = ? ORDER BY timestamp DESC
        ''', (username,))
        authentications = [dict(zip([col[0] for col in cursor.description], row)) 
                          for row in cursor.fetchall()]
        
        # Get impostor analysis
        auth_ids = [auth['id'] for auth in authentications]
        impostor_analyses = []
        if auth_ids:
            placeholders = ','.join(['?' for _ in auth_ids])
            cursor.execute(f'''
                SELECT * FROM impostor_analysis WHERE auth_id IN ({placeholders})
                ORDER BY timestamp DESC
            ''', auth_ids)
            impostor_analyses = [dict(zip([col[0] for col in cursor.description], row)) 
                               for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'username': username,
            'enrollments': enrollments,
            'authentications': authentications,
            'impostor_analyses': impostor_analyses,
            'total_attempts': len(authentications),
            'successful_auths': len([a for a in authentications if a['authenticated']]),
            'failed_auths': len([a for a in authentications if not a['authenticated']])
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total counts
        cursor.execute('SELECT COUNT(*) FROM enrollments')
        total_enrollments = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM authentications')
        total_authentications = cursor.fetchone()[0]
        
        # Success rates
        cursor.execute('SELECT COUNT(*) FROM authentications WHERE authenticated = 1')
        successful_auths = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM authentications WHERE authenticated = 0')
        failed_auths = cursor.fetchone()[0]
        
        # Average scores
        cursor.execute('SELECT AVG(similarity_score), AVG(calibrated_probability) FROM authentications')
        avg_scores = cursor.fetchone()
        
        conn.close()
        
        success_rate = (successful_auths / total_authentications * 100) if total_authentications > 0 else 0
        failure_rate = (failed_auths / total_authentications * 100) if total_authentications > 0 else 0
        
        return {
            'total_enrollments': total_enrollments,
            'total_authentications': total_authentications,
            'successful_authentications': successful_auths,
            'failed_authentications': failed_auths,
            'success_rate_percent': success_rate,
            'failure_rate_percent': failure_rate,
            'average_similarity_score': avg_scores[0] or 0,
            'average_probability': avg_scores[1] or 0
        }

# Global logger instance
enhanced_logger = EnhancedAuthLogger()
