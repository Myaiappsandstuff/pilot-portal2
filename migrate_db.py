#!/usr/bin/env python3
"""
Database Migration Script for Pilot Portal
This script adds the missing photo_filename column to existing databases
"""

import sqlite3
import os
import sys

def migrate_database():
    """Add missing photo_filename column to flight_entries table"""
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    db_path = os.path.join('data', 'pilot_portal.db')
    
    print(f"Checking database at: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist yet. Run the app first to create it.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if photo_filename column exists
        cursor.execute("PRAGMA table_info(flight_entries)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'photo_filename' in columns:
            print("✅ photo_filename column already exists. No migration needed.")
            conn.close()
            return True
        
        print("🔄 Adding photo_filename column to flight_entries table...")
        
        # Add the missing column
        cursor.execute('ALTER TABLE flight_entries ADD COLUMN photo_filename TEXT')
        
        # Update existing records with a default value (if any exist)
        cursor.execute('UPDATE flight_entries SET photo_filename = "legacy_no_photo.jpg" WHERE photo_filename IS NULL')
        
        conn.commit()
        print("✅ Successfully added photo_filename column!")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(flight_entries)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'photo_filename' in columns:
            print("✅ Migration completed successfully!")
            print(f"📊 Columns in flight_entries table: {', '.join(columns)}")
        else:
            print("❌ Migration failed - column not found after addition")
            return False
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed with error: {e}")
        return False

def show_table_info():
    """Show current table structure for debugging"""
    db_path = os.path.join('data', 'pilot_portal.db')
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n📋 Current flight_entries table structure:")
        cursor.execute("PRAGMA table_info(flight_entries)")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        # Count existing records
        cursor.execute("SELECT COUNT(*) FROM flight_entries")
        count = cursor.fetchone()[0]
        print(f"\n📊 Current flight entries: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading table info: {e}")

if __name__ == "__main__":
    print("🛠️  Pilot Portal Database Migration")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        show_table_info()
    else:
        # Show current state
        show_table_info()
        
        # Run migration
        print("\n🚀 Starting migration...")
        success = migrate_database()
        
        if success:
            print("\n🎉 Migration completed! You can now run the app.")
        else:
            print("\n💥 Migration failed. Check the error messages above.")
            sys.exit(1)