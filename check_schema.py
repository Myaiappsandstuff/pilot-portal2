import sqlite3

def check_schema():
    conn = sqlite3.connect('data/pilot_portal.db')
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("PRAGMA table_info(flight_entries)")
    columns = cursor.fetchall()
    
    print("\nFlight Entries Table Schema:")
    print("ID | Name             | Type     | NotNull | Default | PK")
    print("-" * 60)
    for col in columns:
        print(f"{col[0]:2} | {col[1]:<16} | {col[2]:<8} | {col[3]:^7} | {str(col[4] or ''):<7} | {col[5]}")
    
    # Check for sample data
    cursor.execute("SELECT id, airtime, flight_time FROM flight_entries LIMIT 5")
    sample = cursor.fetchall()
    
    print("\nSample Data (ID, Airtime, Flight Time):")
    for row in sample:
        print(f"ID {row[0]}: AT={row[1]} FT={row[2]} (Types: AT={type(row[1]).__name__}, FT={type(row[2]).__name__})")
    
    conn.close()

if __name__ == "__main__":
    check_schema()
