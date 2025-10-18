"""
View authentication and enrollment logs
"""
import sys
sys.path.append('src/api')
from auth_logger import AuthLogger
from tabulate import tabulate

def main():
    logger = AuthLogger('auth_logs.db')
    
    print("\n" + "=" * 100)
    print("ENROLLMENT HISTORY")
    print("=" * 100)
    
    enrollments = logger.get_enrollment_history()
    if enrollments:
        headers = ['ID', 'Username', 'Password Strength', 'Enrollment File', 'Timestamp', 'Success', 'User ID']
        print(tabulate(enrollments, headers=headers, tablefmt='grid'))
    else:
        print("No enrollment records found.")
    
    print("\n" + "=" * 100)
    print("AUTHENTICATION HISTORY")
    print("=" * 100)
    
    auths = logger.get_authentication_history()
    if auths:
        headers = ['ID', 'Username', 'Auth File', 'Score', 'Calibrated Prob', 
                   'Spoof Score', 'Is Spoof', 'Authenticated', 'Timestamp', 'Message']
        # Format for better display
        formatted_auths = []
        for row in auths:
            formatted_row = list(row)
            # Format scores to 4 decimal places
            if formatted_row[3]:  # score
                formatted_row[3] = f"{formatted_row[3]:.4f}"
            if formatted_row[4]:  # calibrated_prob
                formatted_row[4] = f"{formatted_row[4]:.4f}"
            if formatted_row[5]:  # spoof_score
                formatted_row[5] = f"{formatted_row[5]:.6f}"
            formatted_auths.append(formatted_row)
        
        print(tabulate(formatted_auths, headers=headers, tablefmt='grid'))
    else:
        print("No authentication records found.")
    
    # User-specific stats
    print("\n" + "=" * 100)
    print("USER STATISTICS")
    print("=" * 100)
    
    # Get unique usernames
    import sqlite3
    conn = sqlite3.connect('auth_logs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT username FROM enrollment_logs WHERE success = 1')
    usernames = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    for username in usernames:
        stats = logger.get_user_stats(username)
        print(f"\n👤 User: {username}")
        
        if stats['enrollment']:
            print(f"   Password Strength: {stats['enrollment'][0]}")
            print(f"   Enrollment File: {stats['enrollment'][1]}")
            print(f"   Enrolled: {stats['enrollment'][2]}")
        
        if stats['auth_stats'] and stats['auth_stats'][0] > 0:
            total, successful, avg_score, max_score, min_score = stats['auth_stats']
            success_rate = (successful / total * 100) if total > 0 else 0
            print(f"   Total Auth Attempts: {total}")
            print(f"   Successful: {successful} ({success_rate:.1f}%)")
            print(f"   Avg Score: {avg_score:.4f}")
            print(f"   Score Range: {min_score:.4f} - {max_score:.4f}")
    
    print("\n" + "=" * 100)
    
    # Export option
    export = input("\nExport to CSV? (y/n): ")
    if export.lower() == 'y':
        logger.export_to_csv('auth_logs.csv')
        print("✅ Exported to auth_logs.csv")

if __name__ == '__main__':
    try:
        main()
    except ImportError:
        print("Installing required package: tabulate")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'tabulate'])
        print("Please run the script again.")
