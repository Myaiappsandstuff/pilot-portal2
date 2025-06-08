import sqlite3
from datetime import datetime

def check_calculations():
    conn = sqlite3.connect('data/pilot_portal.db')
    cursor = conn.cursor()
    
    # Get current month start
    month_start = datetime.now().replace(day=1).date()
    
    # Get all flight entries for the current month
    cursor.execute('''
        SELECT id, flight_date, airtime, flight_time
        FROM flight_entries 
        WHERE flight_date >= ?
        ORDER BY flight_date
    ''', (month_start,))
    
    entries = cursor.fetchall()
    
    print("\nAll Flight Entries for Current Month:")
    print("ID\tDate\t\tAT\tFT")
    print("-" * 50)
    
    total_at = 0.0
    total_ft = 0.0
    
    for entry in entries:
        entry_id, date, at, ft = entry
        total_at += at
        total_ft += ft
        print(f"{entry_id}\t{date}\t{at}\t{ft}")
    
    print("-" * 50)
    print(f"Sum of AT: {total_at}")
    print(f"Sum of FT: {total_ft}")
    
    # Get the calculated sums from the database
    cursor.execute('''
        SELECT 
            SUM(airtime) as sum_at,
            SUM(flight_time) as sum_ft
        FROM flight_entries 
        WHERE flight_date >= ?
    ''', (month_start,))
    
    db_sum_at, db_sum_ft = cursor.fetchone()
    
    print("\nDatabase Calculated Sums:")
    print(f"SUM(airtime): {db_sum_at}")
    print(f"SUM(flight_time): {db_sum_ft}")
    
    conn.close()

if __name__ == "__main__":
    check_calculations()
