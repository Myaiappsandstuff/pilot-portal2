import sqlite3
import os

def check_database():
    db_path = os.path.join('data', 'pilot_portal.db')
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\nTables in database:")
        for table in tables:
            print(f"- {table[0]}")
        
        # Check pilots table structure
        if 'pilots' in [t[0] for t in tables]:
            print("\nPilots table structure:")
            cursor.execute("PRAGMA table_info(pilots)")
            for col in cursor.fetchall():
                print(f"- {col[1]}: {col[2]}")
            
            # Check pilot count
            cursor.execute("SELECT COUNT(*) FROM pilots")
            count = cursor.fetchone()[0]
            print(f"\nNumber of pilots: {count}")
            
            # List pilots (without sensitive data)
            if count > 0:
                print("\nPilots (showing first 5):")
                cursor.execute("SELECT id, name, is_admin FROM pilots LIMIT 5")
                for pilot in cursor.fetchall():
                    print(f"- ID: {pilot[0]}, Name: {pilot[1]}, Admin: {pilot[2]}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    check_database()
