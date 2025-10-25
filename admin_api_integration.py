#!/usr/bin/env python3
"""
Admin API integration - hooks into existing API to log detailed data
"""

import sqlite3
import json
import time
from datetime import datetime
from typing import Dict, Any

class AdminLogger:
    def __init__(self, db_path='admin_auth_logs.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize admin database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced enrollment tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                num_trials INTEGER,
                trial_files TEXT,
                enrollment_success BOOLEAN,
                prototype_strength REAL,
                enrollment_confidence REAL,
                error_message TEXT,
                ip_address TEXT,
                user_agent TEXT,
                processing_time_ms REAL
            )
        ''')
        
        # Enhanced authentication tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_authentications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                authenticated BOOLEAN,
                similarity_score REAL,
                calibrated_probability REAL,
                spoof_detected BOOLEAN,
                spoof_score REAL,
                decision_reason TEXT,
                confidence_level TEXT,
                trial_quality REAL,
                embedding_distance REAL,
                threshold_used REAL,
                processing_time_ms REAL,
                explain_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                raw_response TEXT
            )
        ''')
        
        # Impostor detection analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_impostor_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                auth_id INTEGER,
                username TEXT,
                is_genuine_user BOOLEAN,
                impostor_type TEXT,
                detection_confidence REAL,
                behavioral_anomalies TEXT,
                neural_pattern_analysis TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (auth_id) REFERENCES admin_authentications (id)
            )
        ''')
        
        # System performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_users INTEGER,
                total_authentications INTEGER,
                success_rate REAL,
                average_processing_time REAL,
                system_load REAL,
                memory_usage REAL,
                active_sessions INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Admin database initialized")
    
    def log_enrollment_attempt(self, enrollment_data: Dict[str, Any]) -> int:
        """Log detailed enrollment attempt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generate detailed analysis
        decision_reason = self._analyze_enrollment(enrollment_data)
        confidence_level = self._determine_enrollment_confidence(enrollment_data)
        
        cursor.execute('''
            INSERT INTO admin_enrollments (
                username, num_trials, trial_files, enrollment_success,
                prototype_strength, enrollment_confidence, error_message,
                ip_address, user_agent, processing_time_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            enrollment_data.get('username', ''),
            enrollment_data.get('num_trials', 0),
            json.dumps(enrollment_data.get('trial_files', [])),
            enrollment_data.get('success', False),
            enrollment_data.get('prototype_strength', 0.0),
            confidence_level,
            enrollment_data.get('error_message', ''),
            enrollment_data.get('ip_address', ''),
            enrollment_data.get('user_agent', ''),
            enrollment_data.get('processing_time_ms', 0.0)
        ))
        
        enrollment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"📝 Logged enrollment: {enrollment_data.get('username')} - {'✅ Success' if enrollment_data.get('success') else '❌ Failed'}")
        return enrollment_id
    
    def log_authentication_attempt(self, auth_data: Dict[str, Any]) -> int:
        """Log detailed authentication attempt with reasoning"""
        start_time = time.time()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generate detailed decision reasoning
        decision_reason = self._analyze_authentication_decision(auth_data)
        confidence_level = self._determine_confidence_level(auth_data)
        
        cursor.execute('''
            INSERT INTO admin_authentications (
                username, authenticated, similarity_score, calibrated_probability,
                spoof_detected, spoof_score, decision_reason, confidence_level,
                trial_quality, embedding_distance, threshold_used, processing_time_ms,
                explain_id, ip_address, user_agent, raw_response
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            auth_data.get('username', ''),
            auth_data.get('authenticated', False),
            auth_data.get('similarity_score', 0.0),
            auth_data.get('calibrated_probability', 0.0),
            auth_data.get('spoof_detected', False),
            auth_data.get('spoof_score', 0.0),
            decision_reason,
            confidence_level,
            auth_data.get('trial_quality', 1.0),
            auth_data.get('embedding_distance', 0.0),
            auth_data.get('threshold_used', 0.5),
            (time.time() - start_time) * 1000,
            auth_data.get('explain_id', ''),
            auth_data.get('ip_address', ''),
            auth_data.get('user_agent', ''),
            json.dumps(auth_data)
        ))
        
        auth_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Log impostor analysis if rejected
        if not auth_data.get('authenticated', False):
            self._log_impostor_analysis(auth_id, auth_data)
        
        status = "✅ AUTHENTICATED" if auth_data.get('authenticated') else "❌ REJECTED"
        print(f"🔐 Logged authentication: {auth_data.get('username')} - {status}")
        return auth_id
    
    def _analyze_enrollment(self, enrollment_data: Dict[str, Any]) -> str:
        """Analyze enrollment attempt and provide reasoning"""
        if not enrollment_data.get('success', False):
            return f"ENROLLMENT FAILED: {enrollment_data.get('error_message', 'Unknown error')}"
        
        num_trials = enrollment_data.get('num_trials', 0)
        prototype_strength = enrollment_data.get('prototype_strength', 0.0)
        
        if num_trials < 3:
            return f"ENROLLMENT SUCCESS: Limited trials ({num_trials}) - May affect authentication accuracy"
        elif prototype_strength > 0.8:
            return f"ENROLLMENT SUCCESS: Strong prototype created ({prototype_strength:.3f}) - Excellent quality"
        elif prototype_strength > 0.6:
            return f"ENROLLMENT SUCCESS: Good prototype created ({prototype_strength:.3f}) - Good quality"
        else:
            return f"ENROLLMENT SUCCESS: Weak prototype created ({prototype_strength:.3f}) - May need re-enrollment"
    
    def _determine_enrollment_confidence(self, enrollment_data: Dict[str, Any]) -> float:
        """Determine enrollment confidence based on data quality"""
        if not enrollment_data.get('success', False):
            return 0.0
        
        num_trials = enrollment_data.get('num_trials', 0)
        prototype_strength = enrollment_data.get('prototype_strength', 0.0)
        
        # Base confidence on number of trials and prototype strength
        trial_confidence = min(num_trials / 5.0, 1.0)  # Optimal is 5 trials
        strength_confidence = prototype_strength
        
        return (trial_confidence + strength_confidence) / 2.0
    
    def _analyze_authentication_decision(self, auth_data: Dict[str, Any]) -> str:
        """Generate detailed reasoning for authentication decision"""
        authenticated = auth_data.get('authenticated', False)
        similarity = auth_data.get('similarity_score', 0.0)
        probability = auth_data.get('calibrated_probability', 0.0)
        spoof_detected = auth_data.get('spoof_detected', False)
        
        if spoof_detected:
            spoof_score = auth_data.get('spoof_score', 0.0)
            return f"🚨 REJECTED: Spoof/replay attack detected (spoof_score={spoof_score:.6f}). Signal appears synthetic or replayed."
        
        if authenticated:
            if probability > 0.9:
                return f"✅ AUTHENTICATED: Excellent match (prob={probability:.3f}, sim={similarity:.3f}). Brain patterns strongly match enrolled prototype."
            elif probability > 0.7:
                return f"✅ AUTHENTICATED: Good match (prob={probability:.3f}, sim={similarity:.3f}). Brain patterns match enrolled prototype."
            elif probability > 0.5:
                return f"✅ AUTHENTICATED: Acceptable match (prob={probability:.3f}, sim={similarity:.3f}). Brain patterns sufficiently match prototype."
            else:
                return f"✅ AUTHENTICATED: Weak match (prob={probability:.3f}, sim={similarity:.3f}). Consider re-enrollment for better accuracy."
        else:
            if probability < 0.1:
                return f"❌ REJECTED: Very poor match (prob={probability:.3f}, sim={similarity:.3f}). Brain patterns completely different - likely impostor."
            elif probability < 0.3:
                return f"❌ REJECTED: Poor match (prob={probability:.3f}, sim={similarity:.3f}). Brain patterns significantly different - possible impostor."
            elif probability < 0.5:
                return f"❌ REJECTED: Below threshold (prob={probability:.3f}, sim={similarity:.3f}). Brain patterns don't match sufficiently."
            else:
                return f"❌ REJECTED: Uncertain identity (prob={probability:.3f}, sim={similarity:.3f}). Patterns similar but not confident enough."
    
    def _determine_confidence_level(self, auth_data: Dict[str, Any]) -> str:
        """Determine confidence level of authentication decision"""
        probability = auth_data.get('calibrated_probability', 0.0)
        spoof_detected = auth_data.get('spoof_detected', False)
        
        if spoof_detected:
            return "HIGH"  # High confidence in spoof detection
        
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
        
        similarity = auth_data.get('similarity_score', 0.0)
        probability = auth_data.get('calibrated_probability', 0.0)
        spoof_detected = auth_data.get('spoof_detected', False)
        
        # Determine impostor type and confidence
        if spoof_detected:
            impostor_type = "REPLAY_ATTACK"
            detection_confidence = 0.95
            anomalies = ["Synthetic signal detected", "Replay attack pattern"]
        elif probability < 0.05:
            impostor_type = "RANDOM_IMPOSTOR"
            detection_confidence = 0.95
            anomalies = ["Completely different neural patterns", "No similarity to enrolled user"]
        elif probability < 0.2:
            impostor_type = "TARGETED_IMPOSTOR"
            detection_confidence = 0.85
            anomalies = ["Different neural patterns", "Some similarity but clearly different user"]
        else:
            impostor_type = "SOPHISTICATED_IMPOSTOR"
            detection_confidence = 0.65
            anomalies = ["Similar neural patterns", "Difficult to distinguish", "May be related individual"]
        
        neural_analysis = f"Similarity: {similarity:.3f}, Probability: {probability:.3f}, Expected genuine: >0.7"
        
        cursor.execute('''
            INSERT INTO admin_impostor_analysis (
                auth_id, username, is_genuine_user, impostor_type, detection_confidence,
                behavioral_anomalies, neural_pattern_analysis
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            auth_id,
            auth_data.get('username', ''),
            False,
            impostor_type,
            detection_confidence,
            json.dumps(anomalies),
            neural_analysis
        ))
        
        conn.commit()
        conn.close()
        
        print(f"🚫 Impostor detected: {impostor_type} ({detection_confidence*100:.1f}% confidence)")
    
    def get_admin_stats(self) -> Dict[str, Any]:
        """Get comprehensive admin statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Basic counts
        cursor.execute('SELECT COUNT(*) FROM admin_enrollments')
        total_enrollments = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM admin_authentications')
        total_authentications = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM admin_authentications WHERE authenticated = 1')
        successful_auths = cursor.fetchone()[0]
        
        # Success rates
        success_rate = (successful_auths / total_authentications * 100) if total_authentications > 0 else 0
        
        # Average scores
        cursor.execute('SELECT AVG(similarity_score), AVG(calibrated_probability) FROM admin_authentications')
        avg_scores = cursor.fetchone()
        
        # Impostor statistics
        cursor.execute('SELECT COUNT(*) FROM admin_impostor_analysis')
        total_impostors = cursor.fetchone()[0]
        
        cursor.execute('SELECT impostor_type, COUNT(*) FROM admin_impostor_analysis GROUP BY impostor_type')
        impostor_types = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_enrollments': total_enrollments,
            'total_authentications': total_authentications,
            'successful_authentications': successful_auths,
            'failed_authentications': total_authentications - successful_auths,
            'success_rate_percent': success_rate,
            'average_similarity_score': avg_scores[0] or 0,
            'average_probability': avg_scores[1] or 0,
            'total_impostors_detected': total_impostors,
            'impostor_types': impostor_types
        }

# Global admin logger instance
admin_logger = AdminLogger()

# Test function to populate sample data
def populate_sample_data():
    """Populate sample data for testing"""
    print("📊 Populating sample admin data...")
    
    # Sample enrollments
    sample_enrollments = [
        {'username': 'user_1', 'num_trials': 5, 'success': True, 'prototype_strength': 0.89, 'processing_time_ms': 1250},
        {'username': 'user_2', 'num_trials': 4, 'success': True, 'prototype_strength': 0.76, 'processing_time_ms': 1100},
        {'username': 'user_3', 'num_trials': 3, 'success': False, 'prototype_strength': 0.45, 'error_message': 'Insufficient trial quality', 'processing_time_ms': 890}
    ]
    
    for enrollment in sample_enrollments:
        admin_logger.log_enrollment_attempt(enrollment)
    
    # Sample authentications
    sample_auths = [
        {'username': 'user_1', 'authenticated': True, 'similarity_score': 0.87, 'calibrated_probability': 0.92, 'spoof_detected': False},
        {'username': 'user_1', 'authenticated': True, 'similarity_score': 0.82, 'calibrated_probability': 0.88, 'spoof_detected': False},
        {'username': 'user_2', 'authenticated': False, 'similarity_score': 0.23, 'calibrated_probability': 0.15, 'spoof_detected': False},
        {'username': 'user_1', 'authenticated': False, 'similarity_score': 0.45, 'calibrated_probability': 0.38, 'spoof_detected': True, 'spoof_score': 0.0045},
        {'username': 'impostor_test', 'authenticated': False, 'similarity_score': 0.12, 'calibrated_probability': 0.08, 'spoof_detected': False}
    ]
    
    for auth in sample_auths:
        admin_logger.log_authentication_attempt(auth)
    
    print("✅ Sample data populated successfully!")

if __name__ == '__main__':
    populate_sample_data()
    stats = admin_logger.get_admin_stats()
    print("\n📈 Admin Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
