#!/usr/bin/env python3
"""
View Authentication Results
Shows registered users, authentication logs, and statistics
"""

import sqlite3
from datetime import datetime
from pathlib import Path

def view_registered_users():
    """View all registered users"""
    conn = sqlite3.connect('data/users.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, created_at FROM users')
    users = cursor.fetchall()
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                    REGISTERED USERS                        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    if users:
        for user in users:
            print(f"  {user[0]}. {user[1]}")
            print(f"     Registered: {user[2]}")
            print()
        print(f"Total Users: {len(users)}")
    else:
        print("  No users registered yet.")
    
    conn.close()
    print()

def view_auth_logs():
    """View authentication logs"""
    conn = sqlite3.connect('data/users.db')
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_logs'")
    if not cursor.fetchone():
        print("╔════════════════════════════════════════════════════════════╗")
        print("║              AUTHENTICATION LOGS (Not Available)          ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()
        print("  Auth logs table not created yet.")
        print("  Restart the backend API to create the table.")
        conn.close()
        return
    
    cursor.execute('SELECT * FROM auth_logs ORDER BY timestamp DESC LIMIT 20')
    logs = cursor.fetchall()
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║              RECENT AUTHENTICATION ATTEMPTS                ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    if logs:
        for log in logs:
            status = "✅ SUCCESS" if log[2] else "❌ FAILED"
            score = f"{log[3]:.3f}" if log[3] else "N/A"
            prob = f"{log[4]:.3f}" if log[4] else "N/A"
            spoof = "🚨 SPOOF" if log[5] else "Clean"
            
            print(f"  {status} - {log[1]}")
            print(f"     Score: {score}, Probability: {prob}, Spoof: {spoof}")
            print(f"     Time: {log[6]}")
            print()
        print(f"Total Attempts: {len(logs)}")
    else:
        print("  No authentication attempts logged yet.")
    
    conn.close()
    print()

def view_statistics():
    """View authentication statistics"""
    conn = sqlite3.connect('data/users.db')
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_logs'")
    if not cursor.fetchone():
        conn.close()
        return
    
    cursor.execute('SELECT COUNT(*) FROM auth_logs')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM auth_logs WHERE authenticated = 1')
    successful = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM auth_logs WHERE authenticated = 0')
    failed = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM auth_logs WHERE is_spoof = 1')
    spoofs = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(score) FROM auth_logs WHERE authenticated = 1')
    avg_genuine_score = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(score) FROM auth_logs WHERE authenticated = 0')
    avg_impostor_score = cursor.fetchone()[0]
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                  AUTHENTICATION STATISTICS                 ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print(f"  Total Attempts:        {total}")
    print(f"  ✅ Successful:         {successful}")
    print(f"  ❌ Failed:             {failed}")
    print(f"  🚨 Spoof Detected:     {spoofs}")
    print()
    
    if total > 0:
        success_rate = (successful / total) * 100
        print(f"  Success Rate:          {success_rate:.1f}%")
    
    if avg_genuine_score:
        print(f"  Avg Genuine Score:     {avg_genuine_score:.3f}")
    
    if avg_impostor_score:
        print(f"  Avg Impostor Score:    {avg_impostor_score:.3f}")
    
    conn.close()
    print()

def view_user_prototypes():
    """View user prototype files"""
    proto_dir = Path('data/user_prototypes')
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                    USER PROTOTYPES                         ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    if proto_dir.exists():
        proto_files = list(proto_dir.glob('*_prototypes.npy'))
        if proto_files:
            for proto_file in proto_files:
                username = proto_file.stem.replace('_prototypes', '')
                size = proto_file.stat().st_size / 1024
                print(f"  {username}: {size:.1f} KB")
            print(f"\nTotal Prototypes: {len(proto_files)}")
        else:
            print("  No user prototypes found.")
    else:
        print("  Prototypes directory not found.")
    
    print()

if __name__ == "__main__":
    print()
    view_registered_users()
    view_auth_logs()
    view_statistics()
    view_user_prototypes()
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                    VIEW COMPLETE! ✨                       ║")
    print("╚════════════════════════════════════════════════════════════╝")
