import sqlite3
import os
from datetime import datetime

def check_ops_emails():
    db_path = os.path.join('data', 'pilot_portal.db')
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check ops_emails table
        print("\n=== Ops Emails ===")
        cursor.execute('''
            SELECT id, email, is_active, description, created_at 
            FROM ops_emails 
            ORDER BY created_at DESC
        ''')
        ops_emails = cursor.fetchall()
        
        if not ops_emails:
            print("No ops emails found in the database!")
        else:
            print(f"Found {len(ops_emails)} ops emails:")
            for email in ops_emails:
                print(f"- ID: {email[0]}, Email: {email[1]}, Active: {email[2]}, Description: {email[3]}, Added: {email[4]}")
        
        # Check recent flight entries and email status
        print("\n=== Recent Flight Entries ===")
        cursor.execute('''
            SELECT id, logsheet_number, q_number, flight_date, email_sent_at
            FROM flight_entries
            ORDER BY submitted_at DESC
            LIMIT 5
        ''')
        recent_flights = cursor.fetchall()
        
        if not recent_flights:
            print("No recent flight entries found.")
        else:
            print(f"Most recent flight entries (max 5):")
            for flight in recent_flights:
                email_status = "✅ Sent" if flight[4] else "❌ Pending"
                print(f"- {flight[1]} (Q{flight[2]}) on {flight[3]}: {email_status} ({flight[4] or 'Never'})")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    print(f"Pilot Portal Email Configuration Check - {datetime.now()}")
    print("=" * 50)
    check_ops_emails()
    print("\nCheck complete. Review the output above for any issues.")
