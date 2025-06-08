from app import app, db_manager

def list_flight_date_range():
    """List the date range of all flight entries in the database"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    try:
        # Get the date range
        cursor.execute('''
            SELECT 
                MIN(flight_date) as first_flight,
                MAX(flight_date) as last_flight,
                COUNT(*) as total_flights
            FROM flight_entries
        ''')
        
        result = cursor.fetchone()
        first_flight, last_flight, total_flights = result
        
        print("\n=== FLIGHT DATE RANGE ===")
        print(f"First flight: {first_flight}")
        print(f"Last flight:  {last_flight}")
        print(f"Total flights: {total_flights}")
        
        # Get flight count by month
        print("\n=== FLIGHTS BY MONTH ===")
        cursor.execute('''
            SELECT 
                strftime('%Y-%m', flight_date) as month,
                COUNT(*) as flight_count
            FROM flight_entries
            GROUP BY month
            ORDER BY month
        ''')
        
        print(f"{'Month':<10} {'Flights':>8}")
        print("-" * 20)
        for month, count in cursor.fetchall():
            print(f"{month:<10} {count:>8}")
        
    except Exception as e:
        print(f"Error fetching flight dates: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    with app.app_context():
        list_flight_date_range()
