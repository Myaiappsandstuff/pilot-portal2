#!/usr/bin/env python3
"""
Email Configuration Diagnostic Script
Tests your email configuration for Frosty's Pilot Portal
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed, checking OS environment variables only")

def check_environment_variables():
    """Check if all required email environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = {
        'GMAIL_USER': 'Gmail username/email address',
        'GMAIL_PASSWORD': 'Gmail app password (not regular password)',
        'OPS_EMAIL': 'Operations email address (where logsheets are sent)'
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var == 'GMAIL_PASSWORD':
                print(f"✅ {var}: {'*' * len(value)} (hidden)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET - {description}")
            missing_vars.append(var)
    
    return missing_vars

def test_gmail_connection():
    """Test connection to Gmail SMTP"""
    print("\n📧 Testing Gmail SMTP connection...")
    
    gmail_user = os.getenv('GMAIL_USER')
    gmail_password = os.getenv('GMAIL_PASSWORD')
    
    if not gmail_user or not gmail_password:
        print("❌ Cannot test - GMAIL_USER or GMAIL_PASSWORD not set")
        return False
    
    try:
        print(f"   Connecting to smtp.gmail.com:587...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        print("   ✅ Connected to SMTP server")
        
        print(f"   Starting TLS encryption...")
        server.starttls()
        print("   ✅ TLS encryption started")
        
        print(f"   Logging in as {gmail_user}...")
        server.login(gmail_user, gmail_password)
        print("   ✅ Login successful")
        
        server.quit()
        print("   ✅ Connection closed properly")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ Authentication failed: {e}")
        print("   💡 Check your app password - regular Gmail passwords don't work!")
        print("   💡 Make sure 2-factor authentication is enabled on your Gmail account")
        return False
    except smtplib.SMTPException as e:
        print(f"   ❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False

def test_send_email():
    """Test sending a simple email"""
    print("\n📤 Testing email sending...")
    
    gmail_user = os.getenv('GMAIL_USER')
    gmail_password = os.getenv('GMAIL_PASSWORD')
    ops_email = os.getenv('OPS_EMAIL', gmail_user)  # Default to gmail_user if OPS_EMAIL not set
    
    if not gmail_user or not gmail_password:
        print("❌ Cannot test - GMAIL_USER or GMAIL_PASSWORD not set")
        return False
    
    try:
        # Create test email
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = ops_email
        msg['Subject'] = f"Frosty's Portal Email Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        body = f"""This is a test email from Frosty's Pilot Portal.

Email configuration is working correctly!

Sent at: {datetime.now()}
From: {gmail_user}
To: {ops_email}

---
Frosty's Operations
Professional Flight Services
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, ops_email, text)
        server.quit()
        
        print(f"   ✅ Test email sent successfully to {ops_email}")
        print(f"   📬 Check {ops_email} for the test message")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to send test email: {e}")
        return False

def check_database_ops_emails():
    """Check if there are any operations emails configured in the database"""
    print("\n🗄️  Checking database operations emails...")
    
    try:
        import sqlite3
        
        db_path = os.path.join('data', 'pilot_portal.db')
        if not os.path.exists(db_path):
            print("   ⚠️  Database not found - run the app first to create it")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT email, is_active, description FROM ops_emails")
        ops_emails = cursor.fetchall()
        
        if not ops_emails:
            print("   ⚠️  No operations emails configured in database")
            print("   💡 Use the admin panel to add operations email addresses")
            return False
        
        print(f"   📧 Found {len(ops_emails)} operations email(s):")
        for email, is_active, description in ops_emails:
            status = "✅ Active" if is_active else "❌ Inactive"
            desc_text = f" ({description})" if description else ""
            print(f"      {email} - {status}{desc_text}")
        
        active_count = sum(1 for _, is_active, _ in ops_emails if is_active)
        if active_count == 0:
            print("   ⚠️  No ACTIVE operations emails found")
            print("   💡 Activate at least one operations email in the admin panel")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking database: {e}")
        return False

def show_gmail_setup_instructions():
    """Show instructions for setting up Gmail app passwords"""
    print("\n📋 Gmail App Password Setup Instructions:")
    print("=" * 50)
    print("1. Go to your Google Account settings")
    print("2. Security → 2-Step Verification (must be enabled)")
    print("3. Security → App passwords")
    print("4. Select app: Mail")
    print("5. Select device: Other (Custom name)")
    print("6. Enter name: 'Frosty Pilot Portal'")
    print("7. Copy the 16-character password (like: abcd efgh ijkl mnop)")
    print("8. Use this password in your .env file as GMAIL_PASSWORD")
    print()
    print("⚠️  DO NOT use your regular Gmail password!")
    print("⚠️  App passwords only work with 2-factor authentication enabled!")

def main():
    """Main diagnostic function"""
    print("🔧 Frosty's Email Configuration Diagnostic")
    print("=" * 50)
    
    # Check environment variables
    missing_vars = check_environment_variables()
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\n💡 Create/update your .env file with:")
        for var in missing_vars:
            print(f"   {var}=your_value_here")
        show_gmail_setup_instructions()
        return
    
    # Test Gmail connection
    if not test_gmail_connection():
        show_gmail_setup_instructions()
        return
    
    # Check database configuration
    check_database_ops_emails()
    
    # Test sending email
    print("\n❓ Do you want to send a test email? (y/n): ", end="")
    if input().lower().startswith('y'):
        test_send_email()
    
    print("\n" + "=" * 50)
    print("🎉 Email diagnostic complete!")
    print("\nIf all tests passed, your email configuration should work.")
    print("If you're still having issues, check the Flask app logs for specific errors.")

if __name__ == "__main__":
    main()