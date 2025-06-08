#!/usr/bin/env python3
"""
Database Structure Checker for Frosty's Pilot Portal
Run this to check your database structure and recent entries
"""

import sqlite3
import os
from datetime import datetime

def check_database():
    """Check database structure and recent entries"""
    
    db_path = os.path.join('data', 'pilot_portal.db')
    
    if not os.path.exists(db_path):
        print("❌ Database file not found at data/pilot_portal.db")
        return False
    
    print("🔍 Checking database structure...")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check flight_entries table structure
        print("📋 flight_entries table structure:")
        cursor.execute("PRAGMA table_info(flight_entries)")
        columns = cursor.fetchall()
        
        expected_columns = [
            'id', 'pilot_id', 'aircraft_id', 'other_pilot_id', 
            'logsheet_number', 'q_number', 'flight_date', 'flight_type',
            'airtime', 'flight_time', 'short_notice', 'rate_applied', 
            'amount_earned', 'photo_filename', 'submitted_at', 'email_sent_at'
        ]
        
        existing_columns = [col[1] for col in columns]
        
        for col in columns:
            status = "✅" if col[1] in expected_columns else "⚠️"
            print(f"  {status} {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        # Check for missing columns
        missing_columns = [col for col in expected_columns if col not in existing_columns]
        if missing_columns:
            print(f"\n❌ Missing columns: {missing_columns}")
        else:
            print("\n✅ All required columns present")
        
        # Check recent entries
        print(f"\n📊 Recent flight entries:")
        cursor.execute('''
            SELECT id, pilot_id, logsheet_number, q_number, flight_date, 
                   submitted_at, email_sent_at, photo_filename
            FROM flight_entries 
            ORDER BY id DESC 
            LIMIT 5
        ''')
        
        recent_entries = cursor.fetchall()
        if recent_entries:
            for entry in recent_entries:
                email_status = "✅ Sent" if entry[6] else "❌ Pending"
                photo_status = "✅ Has photo" if entry[7] else "❌ No photo"
                print(f"  ID {entry[0]}: Pilot {entry[1]}, {entry[2]}/Q{entry[3]}, {entry[4]}")
                print(f"    {email_status}, {photo_status}")
        else:
            print("  No entries found")
        
        # Check pilots table
        print(f"\n👥 Pilots:")
        cursor.execute("SELECT id, name, is_admin FROM pilots ORDER BY name")
        pilots = cursor.fetchall()
        for pilot in pilots:
            role = "Admin" if pilot[2] else "Pilot"
            print(f"  {pilot[0]}: {pilot[1]} ({role})")
        
        # Check aircraft table  
        print(f"\n✈️  Aircraft:")
        cursor.execute("SELECT id, registration, model FROM aircraft ORDER BY registration")
        aircraft = cursor.fetchall()
        for plane in aircraft:
            model = plane[2] if plane[2] else "No model"
            print(f"  {plane[0]}: {plane[1]} ({model})")
        
        # Check ops emails
        print(f"\n📧 Operations Emails:")
        cursor.execute("SELECT id, email, is_active FROM ops_emails ORDER BY email")
        ops_emails = cursor.fetchall()
        if ops_emails:
            for email in ops_emails:
                status = "✅ Active" if email[2] else "❌ Inactive"
                print(f"  {email[1]} ({status})")
        else:
            print("  ❌ No operations emails configured!")
            print("  This will cause logsheet submission to fail!")
        
        # Check file uploads directory
        print(f"\n📁 File Upload Directory:")
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            files = os.listdir(uploads_dir)
            print(f"  ✅ {uploads_dir}/ exists with {len(files)} files")
            if len(files) > 0:
                print(f"  Recent files: {files[-3:] if len(files) >= 3 else files}")
        else:
            print(f"  ❌ {uploads_dir}/ directory missing!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_session_flow():
    """Check logsheet submission flow"""
    print(f"\n🔄 Logsheet Submission Flow Check:")
    print("=" * 40)
    
    # Check if required directories exist
    required_dirs = ['data', 'uploads', 'monthly_reports']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing - creating...")
            try:
                os.makedirs(dir_name, exist_ok=True)
                print(f"✅ Created {dir_name}/ directory")
            except Exception as e:
                print(f"❌ Failed to create {dir_name}/: {e}")
    
    # Check file permissions
    try:
        test_file = os.path.join('uploads', 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✅ File write permissions OK")
    except Exception as e:
        print(f"❌ File write permission issue: {e}")

if __name__ == "__main__":
    print("🛠️  Frosty's Database Structure Checker")
    print("=" * 50)
    
    success = check_database()
    check_session_flow()
    
    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. Replace logsheet_submit route with debug version")
        print("2. Submit a test logsheet")
        print("3. Check Flask console logs for DEBUG messages")
        print("4. If no ops emails: Add one via Admin → Ops Emails")
    else:
        print("\n💥 Fix database issues before testing logsheet submission")