"""Test script for monthly reports"""
from app import app, db_manager, FixedEmailSender
from app import ExcelGenerator  # Import ExcelGenerator
import sqlite3

def get_all_pilots():
    """Retrieve all non-admin pilots from the database"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT id, name, personal_email, work_email, base_rate, is_admin
            FROM pilots
            WHERE is_admin = FALSE
            ORDER BY name
        ''')
        pilots = cursor.fetchall()
        return [{
            'id': p[0],
            'name': p[1],
            'personal_email': p[2],
            'work_email': p[3],
            'base_rate': p[4],
            'is_admin': bool(p[5])
        } for p in pilots]
    finally:
        conn.close()

def get_pilot_flights(pilot_id, year, month):
    """Get all flights for a pilot (both as main and other pilot) for a specific month"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    try:
        # Get flights where pilot is the main pilot
        cursor.execute('''
            SELECT fe.id, fe.flight_date, a.registration, fe.logsheet_number, 
                   fe.q_number, fe.flight_type, fe.airtime, fe.rate_applied, 
                   fe.amount_earned, fe.short_notice, NULL as other_pilot_name
            FROM flight_entries fe
            JOIN aircraft a ON fe.aircraft_id = a.id
            WHERE fe.pilot_id = ? 
              AND strftime('%Y', fe.flight_date) = ?
              AND strftime('%m', fe.flight_date) = ?
            
            UNION ALL
            
            -- Get flights where pilot is the other pilot
            SELECT fe.id, fe.flight_date, a.registration, fe.logsheet_number, 
                   fe.q_number, fe.flight_type, fe.airtime, fe.rate_applied, 
                   fe.amount_earned, fe.short_notice, p.name as other_pilot_name
            FROM flight_entries fe
            JOIN aircraft a ON fe.aircraft_id = a.id
            JOIN pilots p ON fe.pilot_id = p.id
            WHERE fe.other_pilot_id = ?
              AND strftime('%Y', fe.flight_date) = ?
              AND strftime('%m', fe.flight_date) = ?
            
            ORDER BY flight_date
        ''', (pilot_id, str(year), f"{month:02d}", 
              pilot_id, str(year), f"{month:02d}"))
        
        return cursor.fetchall()
    finally:
        conn.close()

def list_pilots():
    """List all pilots in the database"""
    with app.app_context():
        pilots = get_all_pilots()
        if not pilots:
            print("No pilots found in the database.")
            return
        
        print("\n=== PILOTS IN DATABASE ===")
        for idx, pilot in enumerate(pilots, 1):
            print(f"{idx}. {pilot['name']} (ID: {pilot['id']}, Email: {pilot['personal_email']})")

def send_monthly_report(year, month, pilot_id=None):
    """Send monthly report for a specific pilot or all pilots"""
    with app.app_context():
        pilots = get_all_pilots()
        
        if pilot_id:
            # Filter for specific pilot if ID is provided
            pilots = [p for p in pilots if p['id'] == pilot_id]
            if not pilots:
                print(f"Error: Pilot with ID {pilot_id} not found.")
                return
        
        if not pilots:
            print("No pilots found in the database.")
            return
        
        email_sender = FixedEmailSender()
        success_count = 0
        
        print(f"\n=== SENDING MONTHLY REPORTS FOR {month}/{year} ===")
        for pilot in pilots:
            try:
                # Get all flights for this pilot (as both main and other pilot)
                flights = get_pilot_flights(pilot['id'], year, month)
                
                if not flights:
                    print(f"No flights found for {pilot['name']} in {month}/{year}")
                    continue
                
                # Generate and send the report
                excel_generator = ExcelGenerator()
                filepath = excel_generator.generate_monthly_excel(pilot['id'], year, month)
                
                if not filepath:
                    print(f"Failed to generate report for {pilot['name']}")
                    continue
                
                # Prepare email details
                subject = f"Monthly Flight Report - {month}/{year}"
                body = f"""Dear {pilot['name']},
                
Please find attached your monthly flight report for {month}/{year}.

This report includes all flights where you were listed as either the primary pilot or the other pilot.

Best regards,
Flight Operations Team"""
                
                # Send the email
                if email_sender._send_email_with_attachment(
                    to_email=pilot['personal_email'],
                    subject=subject,
                    body=body,
                    attachment_path=filepath
                ):
                    print(f"✓ Report sent to {pilot['name']} ({pilot['personal_email']})")
                    success_count += 1
                    
                    # Print summary of flights included
                    print(f"   - Included {len(flights)} flight(s) in the report:")
                    for flight in flights:
                        flight_type = f"{flight[5]} (Other Pilot: {flight[10]})" if flight[10] else flight[5]
                        print(f"     • {flight[1]} - {flight[2]} - {flight[3]} - {flight_type}")
                else:
                    print(f"✗ Failed to send report to {pilot['name']}")
                
            except Exception as e:
                import traceback
                print(f"Error processing {pilot['name']}: {str(e)}")
                traceback.print_exc()
        
        print(f"\n=== COMPLETED ===\nSent {success_count} out of {len(pilots)} reports successfully.")

def test_monthly_reports():
    """Test sending monthly reports"""
    with app.app_context():
        # 1. List all pilots
        pilots = get_all_pilots()
        print("\n=== Pilots in Database ===")
        for pilot in pilots:
            print(f"- {pilot['name']} <{pilot['personal_email']}>")
        
        # 2. Test sending reports
        print("\n=== Sending Test Reports ===")
        sender = FixedEmailSender()
        sender.send_monthly_reports(2025, 5)
        print("\n=== Test Complete ===")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2 or (len(sys.argv) < 3 and sys.argv[1].lower() != 'list'):
        print("Usage: python test_monthly_report.py [YEAR] [MONTH] [PILOT_ID (optional)]")
        print("\nExamples:")
        print("  python test_monthly_report.py 2023 11       # Send to all pilots for Nov 2023")
        print("  python test_monthly_report.py 2023 11 5    # Send only to pilot with ID 5")
        print("  python test_monthly_report.py list         # List all pilots")
        sys.exit(1)
    
    if sys.argv[1].lower() == 'list':
        list_pilots()
        sys.exit(0)
    
    try:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        pilot_id = int(sys.argv[3]) if len(sys.argv) > 3 else None
        
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")
        if year < 2000 or year > 2100:
            raise ValueError("Year must be between 2000 and 2100")
        
        send_monthly_report(year, month, pilot_id)
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    else:
        test_monthly_reports()
