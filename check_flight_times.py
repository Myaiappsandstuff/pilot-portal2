import sqlite3
import os

print("Checking database at:", os.path.abspath('data/pilot_portal.db'))

# Connect to the database
db_path = os.path.join('data', 'pilot_portal.db')
if not os.path.exists(db_path):
    print("Error: Database file not found at", db_path)
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("\nTables in database:", [t[0] for t in tables])
    
    # Check pilots table
    cursor.execute("SELECT * FROM pilots LIMIT 1")
    pilot = cursor.fetchone()
    if pilot:
        print("\nPilot found:", pilot)
        pilot_id = pilot[0]
        
        # Check flight_entries table structure
        cursor.execute("PRAGMA table_info(flight_entries)")
        columns = cursor.fetchall()
        print("\nFlight entries columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Get flight entries
        cursor.execute('''
            SELECT id, flight_date, airtime, flight_time, logsheet_number
            FROM flight_entries 
            WHERE pilot_id = ? 
            ORDER BY flight_date DESC 
            LIMIT 5
        ''', (pilot_id,))
        
        entries = cursor.fetchall()
        if entries:
            print("\nRecent flight entries:")
            print("ID\tDate\t\tAirtime\tFlight Time\tLogsheet #")
            print("-" * 50)
            for row in entries:
                print(f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}\t\t{row[4]}")
        else:
            print("\nNo flight entries found for this pilot.")
    else:
        print("\nNo pilots found in the database.")
        
except Exception as e:
    print("\nError:", str(e))
    
finally:
    if 'conn' in locals():
        conn.close()
