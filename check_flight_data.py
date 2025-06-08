import sqlite3
import os

print("Checking flight entries in the database...")

try:
    conn = sqlite3.connect('data/pilot_portal.db')
    cursor = conn.cursor()
    
    # Get all flight entries with airtime and flight_time
    cursor.execute('''
        SELECT id, flight_date, airtime, flight_time, airtime = flight_time as same_values
        FROM flight_entries 
        ORDER BY flight_date DESC
    ''')
    
    entries = cursor.fetchall()
    
    if entries:
        print("\nFlight entries (ID, Date, Airtime, Flight Time, Same?):")
        print("-" * 80)
        for entry in entries:
            print(f"ID: {entry[0]}, Date: {entry[1]}, AT: {entry[2]}, FT: {entry[3]}, Same: {bool(entry[4])}")
    else:
        print("\nNo flight entries found in the database.")
    
    # Get column info
    cursor.execute("PRAGMA table_info(flight_entries)")
    columns = cursor.fetchall()
    print("\nFlight entries columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
except Exception as e:
    print(f"\nError: {e}")
    
finally:
    if 'conn' in locals():
        conn.close()
