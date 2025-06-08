#!/usr/bin/env python3
"""
Complete Database Migration Script for Pilot Portal
This script adds ALL missing columns to existing databases
"""

import sqlite3
import os
import sys

def migrate_database():
    """Add all missing columns to flight_entries table"""
    
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
        
        # Check current columns
        cursor.execute("PRAGMA table_info(flight_entries)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Current columns: {', '.join(existing_columns)}")
        
        # Define all required columns with their types
        required_columns = {
            'photo_filename': 'TEXT',
            'email_sent_at': 'TIMESTAMP',
            'submitted_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }
        
        migrations_needed = []
        
        # Check which columns are missing
        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                migrations_needed.append((column_name, column_type))
        
        if not migrations_needed:
            print("✅ All required columns already exist. No migration needed.")
            conn.close()
            return True
        
        print(f"🔄 Need to add {len(migrations_needed)} columns...")
        
        # Add missing columns one by one
        for column_name, column_type in migrations_needed:
            print(f"  Adding {column_name} ({column_type})...")
            
            try:
                # Add the column
                cursor.execute(f'ALTER TABLE flight_entries ADD COLUMN {column_name} {column_type}')
                
                # Set default values for existing records
                if column_name == 'photo_filename':
                    cursor.execute('UPDATE flight_entries SET photo_filename = "legacy_no_photo.jpg" WHERE photo_filename IS NULL')
                elif column_name == 'email_sent_at':
                    # Leave as NULL for existing records (indicates email not sent)
                    pass
                elif column_name == 'submitted_at':
                    # Set to current timestamp for existing records
                    cursor.execute('UPDATE flight_entries SET submitted_at = CURRENT_TIMESTAMP WHERE submitted_at IS NULL')
                
                print(f"  ✅ Successfully added {column_name}")
                
            except sqlite3.OperationalError as e:
                print(f"  ❌ Failed to add {column_name}: {e}")
                return False
        
        conn.commit()
        print("✅ All migrations completed successfully!")
        
        # Verify all columns were added
        cursor.execute("PRAGMA table_info(flight_entries)")
        final_columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📊 Final columns: {', '.join(final_columns)}")
        
        # Check that all required columns are now present
        missing = [col for col in required_columns.keys() if col not in final_columns]
        if missing:
            print(f"❌ Still missing columns: {', '.join(missing)}")
            return False
        
        # Count existing records
        cursor.execute("SELECT COUNT(*) FROM flight_entries")
        count = cursor.fetchone()[0]
        print(f"📊 Total flight entries: {count}")
        
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
            default_val = f" DEFAULT {col[4]}" if col[4] else ""
            print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}{default_val}")
        
        # Count existing records
        cursor.execute("SELECT COUNT(*) FROM flight_entries")
        count = cursor.fetchone()[0]
        print(f"\n📊 Current flight entries: {count}")
        
        # Show sample data if any exists
        if count > 0:
            print("\n📄 Sample record structure:")
            cursor.execute("SELECT * FROM flight_entries LIMIT 1")
            sample = cursor.fetchone()
            if sample:
                cursor.execute("PRAGMA table_info(flight_entries)")
                column_names = [col[1] for col in cursor.fetchall()]
                for i, value in enumerate(sample):
                    print(f"  {column_names[i]}: {value}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading table info: {e}")

def reset_database():
    """Completely recreate the flight_entries table with correct structure"""
    db_path = os.path.join('data', 'pilot_portal.db')
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist.")
        return False
    
    response = input("⚠️  This will DELETE all flight entries! Are you sure? (type 'YES' to confirm): ")
    if response != 'YES':
        print("❌ Reset cancelled.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🗑️  Dropping existing flight_entries table...")
        cursor.execute('DROP TABLE IF EXISTS flight_entries')
        
        print("🏗️  Creating new flight_entries table with correct structure...")
        cursor.execute('''
            CREATE TABLE flight_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pilot_id INTEGER,
                aircraft_id INTEGER,
                other_pilot_id INTEGER,
                logsheet_number TEXT NOT NULL,
                q_number TEXT NOT NULL,
                flight_date DATE NOT NULL,
                flight_type TEXT NOT NULL CHECK(flight_type IN ('604', '704')),
                airtime REAL NOT NULL,
                flight_time REAL NOT NULL,
                short_notice BOOLEAN DEFAULT FALSE,
                rate_applied REAL NOT NULL,
                amount_earned REAL NOT NULL,
                photo_filename TEXT NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                email_sent_at TIMESTAMP,
                FOREIGN KEY (pilot_id) REFERENCES pilots (id),
                FOREIGN KEY (aircraft_id) REFERENCES aircraft (id),
                FOREIGN KEY (other_pilot_id) REFERENCES pilots (id),
                UNIQUE(logsheet_number, q_number)
            )
        ''')
        
        conn.commit()
        print("✅ Successfully recreated flight_entries table!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Reset failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🛠️  Pilot Portal Complete Database Migration")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--info":
            show_table_info()
        elif sys.argv[1] == "--reset":
            print("⚠️  RESET MODE: This will delete all flight entries!")
            success = reset_database()
            if success:
                print("✅ Database reset complete!")
            else:
                print("❌ Reset failed!")
        else:
            print("Usage:")
            print("  python migrate_db_complete.py          # Run migration")
            print("  python migrate_db_complete.py --info   # Show table info")
            print("  python migrate_db_complete.py --reset  # Reset table (DANGER!)")
    else:
        # Show current state
        show_table_info()
        
        # Run migration
        print("\n🚀 Starting complete migration...")
        success = migrate_database()
        
        if success:
            print("\n🎉 Migration completed! You can now run the app.")
        else:
            print("\n💥 Migration failed. Check the error messages above.")
            print("\n🔧 If issues persist, you can reset the table with:")
            print("   python migrate_db_complete.py --reset")
            sys.exit(1)