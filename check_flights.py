from app import app, db_manager
from datetime import datetime

def list_all_flights():
    """List all flight entries in the database"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT fe.id, p.name, a.registration, fe.flight_date, fe.logsheet_number, fe.q_number, fe.flight_type
            FROM flight_entries fe
            JOIN pilots p ON fe.pilot_id = p.id
            JOIN aircraft a ON fe.aircraft_id = a.id
            ORDER BY fe.flight_date DESC
        ''')
        flights = cursor.fetchall()
        
        if not flights:
            print("No flight entries found in the database.")
            return
        
        print("\n=== FLIGHT ENTRIES ===")
        print(f"{'ID':<5} {'Pilot':<10} {'Aircraft':<10} {'Date':<12} {'Logsheet':<10} {'Q Number':<10} {'Type'}")
        print("-" * 70)
        for flight in flights:
            print(f"{flight[0]:<5} {flight[1]:<10} {flight[2]:<10} {flight[3]:<12} {flight[4]:<10} {flight[5]:<10} {flight[6]}")
            
    except Exception as e:
        print(f"Error fetching flight entries: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    with app.app_context():
        list_all_flights()
