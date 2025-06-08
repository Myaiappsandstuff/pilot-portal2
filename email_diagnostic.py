#!/usr/bin/env python3
"""
COMPLETE EMAIL DIAGNOSTIC & FIX TOOL for Frosty's Pilot Portal
This script will identify and help fix ALL email-related issues

Run this before testing your email system!
"""

import os
import sqlite3
import smtplib
import sys
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import glob

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, using OS environment variables only")

class EmailDiagnostic:
    def __init__(self):
        self.gmail_user = os.getenv('GMAIL_USER')
        self.gmail_password = os.getenv('GMAIL_PASSWORD')
        self.admin_email = os.getenv('ADMIN_EMAIL')
        self.issues_found = []
        self.fixes_applied = []
        
    def log_issue(self, issue):
        """Log an issue found"""
        self.issues_found.append(issue)
        print(f"❌ ISSUE: {issue}")
    
    def log_fix(self, fix):
        """Log a fix applied"""
        self.fixes_applied.append(fix)
        print(f"🔧 FIXED: {fix}")
    
    def check_environment_variables(self):
        """Check all email-related environment variables"""
        print("\n🔍 CHECKING ENVIRONMENT VARIABLES")
        print("=" * 50)
        
        # Check Gmail credentials
        if not self.gmail_user:
            self.log_issue("GMAIL_USER not set in environment variables")
        else:
            print(f"✅ GMAIL_USER: {self.gmail_user}")
        
        if not self.gmail_password:
            self.log_issue("GMAIL_PASSWORD not set in environment variables")
        else:
            if len(self.gmail_password) < 16:
                self.log_issue("GMAIL_PASSWORD seems too short - should be 16-char app password")
            else:
                print(f"✅ GMAIL_PASSWORD: {'*' * len(self.gmail_password)} (length: {len(self.gmail_password)})")
        
        if not self.admin_email:
            self.log_issue("ADMIN_EMAIL not set - admin notifications will fail")
        else:
            print(f"✅ ADMIN_EMAIL: {self.admin_email}")
    
    def check_gmail_connection(self):
        """Test Gmail SMTP connection"""
        print("\n📧 TESTING GMAIL SMTP CONNECTION")
        print("=" * 50)
        
        if not self.gmail_user or not self.gmail_password:
            self.log_issue("Cannot test Gmail - credentials missing")
            return False
        
        try:
            print("   🔗 Connecting to smtp.gmail.com:587...")
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
            print("   ✅ Connected to SMTP server")
            
            print("   🔒 Starting TLS encryption...")
            server.starttls()
            print("   ✅ TLS encryption started")
            
            print(f"   🔑 Authenticating as {self.gmail_user}...")
            server.login(self.gmail_user, self.gmail_password)
            print("   ✅ Authentication successful")
            
            server.quit()
            print("   ✅ Connection closed properly")
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            self.log_issue(f"Gmail authentication failed: {e}")
            print("   💡 SOLUTION: Use Gmail App Password, not regular password")
            print("   💡 Enable 2-factor authentication first")
            return False
        except smtplib.SMTPException as e:
            self.log_issue(f"SMTP error: {e}")
            return False
        except Exception as e:
            self.log_issue(f"Connection error: {e}")
            return False
    
    def check_database_structure(self):
        """Check database structure for email-related tables"""
        print("\n🗄️  CHECKING DATABASE STRUCTURE")
        print("=" * 50)
        
        db_path = os.path.join('data', 'pilot_portal.db')
        
        if not os.path.exists('data'):
            os.makedirs('data', exist_ok=True)
            self.log_fix("Created data/ directory")
        
        if not os.path.exists(db_path):
            self.log_issue("Database file not found - run app.py first to create it")
            return False
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check flight_entries table structure
            cursor.execute("PRAGMA table_info(flight_entries)")
            columns = [col[1] for col in cursor.fetchall()]
            
            required_columns = ['email_sent_at', 'photo_filename', 'submitted_at']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                self.log_issue(f"Missing columns in flight_entries: {missing_columns}")
                print("   💡 Run migrate_db_complete.py to fix this")
            else:
                print("   ✅ flight_entries table has all required columns")
            
            # Check ops_emails table
            try:
                cursor.execute("SELECT COUNT(*) FROM ops_emails")
                print("   ✅ ops_emails table exists")
            except sqlite3.OperationalError:
                self.log_issue("ops_emails table missing")
                print("   💡 Run app.py once to create all tables")
            
            conn.close()
            return len(missing_columns) == 0
            
        except Exception as e:
            self.log_issue(f"Database error: {e}")
            return False
    
    def check_operations_emails(self):
        """Check operations email configuration"""
        print("\n📬 CHECKING OPERATIONS EMAILS")
        print("=" * 50)
        
        db_path = os.path.join('data', 'pilot_portal.db')
        
        if not os.path.exists(db_path):
            self.log_issue("Database not found - cannot check ops emails")
            return False
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT email, is_active, description FROM ops_emails")
            ops_emails = cursor.fetchall()
            
            if not ops_emails:
                self.log_issue("NO operations emails configured!")
                print("   💡 CRITICAL: Add operations emails via admin panel")
                print("   💡 Logsheet submissions will FAIL without ops emails")
                return False
            
            active_emails = [email for email, is_active, desc in ops_emails if is_active]
            
            print(f"   📧 Found {len(ops_emails)} operations email(s):")
            for email, is_active, description in ops_emails:
                status = "✅ Active" if is_active else "❌ Inactive"
                desc_text = f" ({description})" if description else ""
                print(f"      {email} - {status}{desc_text}")
            
            if not active_emails:
                self.log_issue("NO ACTIVE operations emails found!")
                print("   💡 Activate at least one operations email")
                return False
            
            print(f"   ✅ {len(active_emails)} active operations email(s)")
            conn.close()
            return True
            
        except Exception as e:
            self.log_issue(f"Error checking operations emails: {e}")
            return False
    
    def check_file_system(self):
        """Check file system setup for emails"""
        print("\n📁 CHECKING FILE SYSTEM")
        print("=" * 50)
        
        # Check required directories
        required_dirs = ['uploads', 'data', 'monthly_reports']
        
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                try:
                    os.makedirs(dir_name, exist_ok=True)
                    self.log_fix(f"Created {dir_name}/ directory")
                except Exception as e:
                    self.log_issue(f"Cannot create {dir_name}/ directory: {e}")
            else:
                print(f"   ✅ {dir_name}/ directory exists")
        
        # Test file write permissions
        try:
            test_file = os.path.join('uploads', 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print("   ✅ File write permissions OK")
        except Exception as e:
            self.log_issue(f"File write permission issue: {e}")
        
        # Check uploads directory contents
        uploads_dir = 'uploads'
        if os.path.exists(uploads_dir):
            files = os.listdir(uploads_dir)
            print(f"   📄 uploads/ contains {len(files)} files")
            
            # Check for recent files
            if files:
                recent_files = sorted(files)[-3:]
                print(f"   📄 Recent files: {recent_files}")
        
        return True
    
    def check_app_configuration(self):
        """Check app.py configuration for email"""
        print("\n⚙️  CHECKING APP CONFIGURATION")
        print("=" * 50)
        
        app_files = ['app.py', 'app - Copy.py']
        app_file = None
        
        for filename in app_files:
            if os.path.exists(filename):
                app_file = filename
                break
        
        if not app_file:
            self.log_issue("app.py file not found")
            return False
        
        print(f"   📄 Found app file: {app_file}")
        
        try:
            with open(app_file, 'r') as f:
                content = f.read()
            
            # Check for ImprovedEmailSender
            if 'class ImprovedEmailSender' in content:
                print("   ✅ ImprovedEmailSender class found")
            else:
                self.log_issue("ImprovedEmailSender class missing from app.py")
            
            # Check for email routes
            email_routes = [
                'send_logsheet_to_ops',
                'admin_test_email',
                'admin_resend_logsheet'
            ]
            
            for route in email_routes:
                if route in content:
                    print(f"   ✅ {route} function found")
                else:
                    self.log_issue(f"{route} function missing")
            
            # Check for environment variable usage
            if 'GMAIL_USER' in content and 'GMAIL_PASSWORD' in content:
                print("   ✅ Email environment variables referenced")
            else:
                self.log_issue("Email environment variables not properly referenced")
            
            return True
            
        except Exception as e:
            self.log_issue(f"Error reading app file: {e}")
            return False
    
    def test_email_sending(self):
        """Test actual email sending"""
        print("\n📤 TESTING EMAIL SENDING")
        print("=" * 50)
        
        if not self.gmail_user or not self.gmail_password:
            print("   ⏭️  Skipping email test - credentials not configured")
            return False
        
        test_to = self.admin_email or self.gmail_user
        
        print(f"   📧 Sending test email to {test_to}...")
        
        try:
            # Create test email
            msg = MIMEMultipart()
            msg['From'] = self.gmail_user
            msg['To'] = test_to
            msg['Subject'] = f"Frosty's Email System Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            body = f"""✅ EMAIL SYSTEM TEST SUCCESSFUL!

This email confirms that Frosty's Pilot Portal email system is working correctly.

Configuration Status:
✅ Gmail SMTP Connection: Working
✅ Authentication: Successful  
✅ Email Sending: Working

Test Details:
- Sent from: {self.gmail_user}
- Sent to: {test_to}
- Test time: {datetime.now()}
- Server: smtp.gmail.com:587

Your logsheet email system is ready for operations!

---
Frosty's Operations
Professional Flight Services
Automated System Test
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
            server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            text = msg.as_string()
            server.sendmail(self.gmail_user, test_to, text)
            server.quit()
            
            print(f"   ✅ Test email sent successfully!")
            print(f"   📬 Check {test_to} for the test message")
            return True
            
        except Exception as e:
            self.log_issue(f"Email sending test failed: {e}")
            return False
    
    def create_env_template(self):
        """Create .env template if it doesn't exist"""
        print("\n📝 CHECKING .ENV FILE")
        print("=" * 50)
        
        if os.path.exists('.env'):
            print("   ✅ .env file exists")
            return True
        
        env_template = """# Email Configuration for Frosty's Pilot Portal
GMAIL_USER=your-email@gmail.com
GMAIL_PASSWORD=your-16-char-app-password
ADMIN_EMAIL=admin@your-company.com

# Flask Configuration
SECRET_KEY=your-very-long-secret-key-here-32-chars-minimum
FLASK_ENV=development
DEBUG=true

# Application Settings
DATA_DIR=data
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE_MB=16
SESSION_TIMEOUT_HOURS=2
PORT=5000

# Email Processing Settings
EMAIL_RETRY_ATTEMPTS=3
EMAIL_TIMEOUT_SECONDS=30

# Logging Level (INFO, WARNING, ERROR)
LOG_LEVEL=INFO
"""
        
        try:
            with open('.env', 'w') as f:
                f.write(env_template)
            self.log_fix("Created .env template file")
            print("   📝 Please edit .env file with your actual values")
            return False
        except Exception as e:
            self.log_issue(f"Cannot create .env file: {e}")
            return False
    
    def show_gmail_setup_instructions(self):
        """Show detailed Gmail setup instructions"""
        print("\n📋 GMAIL APP PASSWORD SETUP INSTRUCTIONS")
        print("=" * 60)
        print("1. Go to https://myaccount.google.com/")
        print("2. Click 'Security' in the left sidebar")
        print("3. Under 'Signing in to Google', click '2-Step Verification'")
        print("4. Enable 2-Step Verification if not already enabled")
        print("5. Go back to Security, click 'App passwords'")
        print("6. Select 'Mail' for app type")
        print("7. Select 'Other (Custom name)' for device")
        print("8. Enter name: 'Frosty Pilot Portal'")
        print("9. Copy the 16-character password (format: abcd efgh ijkl mnop)")
        print("10. Use this password in your .env file as GMAIL_PASSWORD")
        print()
        print("⚠️  IMPORTANT:")
        print("   - Use the APP PASSWORD, not your regular Gmail password")
        print("   - 2-Factor Authentication MUST be enabled")
        print("   - The app password is 16 characters with spaces")
    
    def show_ops_email_setup(self):
        """Show how to set up operations emails"""
        print("\n📬 OPERATIONS EMAIL SETUP INSTRUCTIONS")
        print("=" * 60)
        print("1. Start your Flask app: python app.py")
        print("2. Login with admin PIN (check console output)")
        print("3. Go to Admin Dashboard")
        print("4. Click 'Ops Emails'")
        print("5. Click 'Add Operations Email'")
        print("6. Enter operations email address")
        print("7. Add description (optional)")
        print("8. Make sure 'Active' is checked")
        print("9. Click 'Add Operations Email'")
        print()
        print("💡 TIPS:")
        print("   - Add multiple ops emails for redundancy")
        print("   - Use dedicated operations email addresses")
        print("   - Test with your own email first")
    
    def run_complete_diagnostic(self):
        """Run all diagnostic checks"""
        print("🔧 FROSTY'S COMPLETE EMAIL DIAGNOSTIC")
        print("=" * 60)
        print("Checking all email system components...")
        print()
        
        # Run all checks
        self.create_env_template()
        self.check_environment_variables()
        self.check_file_system()
        self.check_database_structure()
        self.check_operations_emails()
        self.check_app_configuration()
        
        # Test connection if credentials available
        if self.gmail_user and self.gmail_password:
            gmail_ok = self.check_gmail_connection()
            if gmail_ok:
                self.test_email_sending()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 60)
        
        if self.fixes_applied:
            print(f"🔧 FIXES APPLIED ({len(self.fixes_applied)}):")
            for fix in self.fixes_applied:
                print(f"   ✅ {fix}")
        
        if self.issues_found:
            print(f"\n❌ ISSUES FOUND ({len(self.issues_found)}):")
            for issue in self.issues_found:
                print(f"   ❌ {issue}")
            
            print(f"\n🎯 NEXT STEPS TO FIX ISSUES:")
            
            # Categorize fixes needed
            if any('GMAIL_USER' in issue or 'GMAIL_PASSWORD' in issue for issue in self.issues_found):
                print("   1. 📧 SET UP GMAIL CREDENTIALS:")
                self.show_gmail_setup_instructions()
            
            if any('operations email' in issue.lower() for issue in self.issues_found):
                print("   2. 📬 SET UP OPERATIONS EMAILS:")
                self.show_ops_email_setup()
            
            if any('database' in issue.lower() or 'column' in issue.lower() for issue in self.issues_found):
                print("   3. 🗄️  FIX DATABASE:")
                print("      Run: python migrate_db_complete.py")
            
            print(f"\n   4. 🔄 RE-RUN THIS DIAGNOSTIC:")
            print("      python email_diagnostic.py")
            
        else:
            print("🎉 ALL CHECKS PASSED!")
            print("Your email system should be working correctly.")
            print()
            print("🚀 READY TO TEST:")
            print("   1. Start your app: python app.py")
            print("   2. Login as admin")
            print("   3. Go to Admin → Test Email")
            print("   4. Submit a test logsheet as a pilot")
        
        print("\n" + "=" * 60)
        return len(self.issues_found) == 0

def main():
    """Main diagnostic function"""
    diagnostic = EmailDiagnostic()
    success = diagnostic.run_complete_diagnostic()
    
    if not success:
        sys.exit(1)
    else:
        print("✅ Email system diagnostic completed successfully!")

if __name__ == "__main__":
    main()