#!/usr/bin/env python3
"""
EMAIL SYSTEM AUTO-FIX SCRIPT for Frosty's Pilot Portal
This script automatically fixes common email system issues

Run this after the diagnostic script identifies problems!
"""

import os
import sqlite3
import glob
import re
from pathlib import Path

class EmailAutoFix:
    def __init__(self):
        self.fixes_applied = []
        self.backup_created = False
    
    def log_fix(self, fix):
        """Log a fix that was applied"""
        self.fixes_applied.append(fix)
        print(f"🔧 FIXED: {fix}")
    
    def create_backup(self):
        """Create backup of important files before making changes"""
        if self.backup_created:
            return
        
        from datetime import datetime
        backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup database if exists
            if os.path.exists('data/pilot_portal.db'):
                import shutil
                shutil.copy2('data/pilot_portal.db', f'{backup_dir}/pilot_portal.db')
                print(f"📦 Created database backup: {backup_dir}/pilot_portal.db")
            
            # Backup .env if exists
            if os.path.exists('.env'):
                import shutil
                shutil.copy2('.env', f'{backup_dir}/.env')
                print(f"📦 Created .env backup: {backup_dir}/.env")
            
            self.backup_created = True
            
        except Exception as e:
            print(f"⚠️  Could not create backup: {e}")
    
    def fix_directories(self):
        """Create missing directories with proper permissions"""
        print("\n📁 FIXING DIRECTORY STRUCTURE")
        print("=" * 40)
        
        required_dirs = {
            'data': 'Database storage',
            'uploads': 'Logsheet photo uploads', 
            'monthly_reports': 'Generated Excel reports',
            'templates': 'HTML templates',
            'templates/admin': 'Admin templates',
            'templates/logsheet': 'Logsheet form templates'
        }
        
        for dir_name, description in required_dirs.items():
            if not os.path.exists(dir_name):
                try:
                    os.makedirs(dir_name, exist_ok=True)
                    self.log_fix(f"Created {dir_name}/ directory ({description})")
                except Exception as e:
                    print(f"❌ Failed to create {dir_name}/: {e}")
            else:
                print(f"✅ {dir_name}/ already exists")
    
    def fix_database_schema(self):
        """Fix missing database columns for email tracking"""
        print("\n🗄️  FIXING DATABASE SCHEMA")
        print("=" * 40)
        
        db_path = os.path.join('data', 'pilot_portal.db')
        
        if not os.path.exists(db_path):
            print("⚠️  Database not found - will be created when app starts")
            return
        
        self.create_backup()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check flight_entries table structure
            cursor.execute("PRAGMA table_info(flight_entries)")
            existing_columns = [column[1] for column in cursor.fetchall()]
            
            # Define required columns
            required_columns = {
                'photo_filename': 'TEXT',
                'email_sent_at': 'TIMESTAMP',
                'submitted_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            }
            
            # Add missing columns
            for column_name, column_type in required_columns.items():
                if column_name not in existing_columns:
                    try:
                        cursor.execute(f'ALTER TABLE flight_entries ADD COLUMN {column_name} {column_type}')
                        self.log_fix(f"Added {column_name} column to flight_entries table")
                        
                        # Set default values for existing records
                        if column_name == 'photo_filename':
                            cursor.execute('UPDATE flight_entries SET photo_filename = "legacy_no_photo.jpg" WHERE photo_filename IS NULL')
                        elif column_name == 'submitted_at':
                            cursor.execute('UPDATE flight_entries SET submitted_at = CURRENT_TIMESTAMP WHERE submitted_at IS NULL')
                        
                    except sqlite3.OperationalError as e:
                        print(f"❌ Failed to add {column_name}: {e}")
                else:
                    print(f"✅ {column_name} column already exists")
            
            # Ensure ops_emails table exists
            try:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ops_emails (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT NOT NULL UNIQUE,
                        is_active BOOLEAN DEFAULT TRUE,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                print("✅ ops_emails table ensured")
            except Exception as e:
                print(f"❌ Error with ops_emails table: {e}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Database schema fix failed: {e}")
    
    def fix_csrf_tokens(self):
        """Add CSRF tokens to forms that need them"""
        print("\n🔒 FIXING CSRF TOKENS IN TEMPLATES")
        print("=" * 40)
        
        # Find all template files
        template_files = []
        for pattern in ['templates/**/*.html', 'templates/*.html']:
            template_files.extend(glob.glob(pattern, recursive=True))
        
        if not template_files:
            print("⚠️  No template files found")
            return
        
        for template_file in template_files:
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file has POST forms
                if not re.search(r'<form[^>]*method\s*=\s*["\']POST["\']', content, re.IGNORECASE):
                    continue
                
                # Check if already has CSRF token
                if re.search(r'csrf_token\(\)|name\s*=\s*["\']csrf_token["\']', content, re.IGNORECASE):
                    print(f"✅ {template_file} already has CSRF token")
                    continue
                
                # Add CSRF token to POST forms
                def add_csrf_to_form(match):
                    form_tag = match.group(1)
                    csrf_line = '\n            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>'
                    return form_tag + csrf_line
                
                updated_content = re.sub(
                    r'(<form[^>]*method\s*=\s*["\']POST["\'][^>]*>)',
                    add_csrf_to_form,
                    content,
                    flags=re.IGNORECASE
                )
                
                if updated_content != content:
                    # Create backup before modifying
                    if not self.backup_created:
                        self.create_backup()
                    
                    with open(template_file, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    self.log_fix(f"Added CSRF token to {template_file}")
                else:
                    print(f"✅ {template_file} already OK")
                    
            except Exception as e:
                print(f"❌ Error fixing {template_file}: {e}")
    
    def fix_env_file(self):
        """Create or fix .env file"""
        print("\n⚙️  FIXING ENVIRONMENT CONFIGURATION")
        print("=" * 40)
        
        env_template = {
            'GMAIL_USER': 'your-email@gmail.com',
            'GMAIL_PASSWORD': 'your-16-char-app-password-here',
            'ADMIN_EMAIL': 'admin@your-company.com',
            'SECRET_KEY': 'your-very-long-secret-key-minimum-32-chars',
            'FLASK_ENV': 'development',
            'DEBUG': 'true',
            'DATA_DIR': 'data',
            'UPLOAD_FOLDER': 'uploads',
            'MAX_FILE_SIZE_MB': '16',
            'SESSION_TIMEOUT_HOURS': '2',
            'PORT': '5000',
            'EMAIL_RETRY_ATTEMPTS': '3',
            'EMAIL_TIMEOUT_SECONDS': '30',
            'LOG_LEVEL': 'INFO'
        }
        
        env_exists = os.path.exists('.env')
        
        if env_exists:
            # Read existing .env
            existing_vars = {}
            try:
                with open('.env', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            existing_vars[key.strip()] = value.strip()
                print("✅ .env file exists, checking for missing variables...")
            except Exception as e:
                print(f"❌ Error reading .env: {e}")
                existing_vars = {}
        else:
            existing_vars = {}
            print("📝 Creating new .env file...")
        
        # Add missing variables
        missing_vars = []
        for key, default_value in env_template.items():
            if key not in existing_vars:
                missing_vars.append(key)
        
        if missing_vars or not env_exists:
            self.create_backup()
            
            try:
                # Create complete .env content
                env_content = "# Email Configuration for Frosty's Pilot Portal\n"
                env_content += "# IMPORTANT: Replace these with your actual values!\n\n"
                
                for key, default_value in env_template.items():
                    if key in existing_vars:
                        value = existing_vars[key]
                    else:
                        value = default_value
                    
                    # Add comments for important variables
                    if key == 'GMAIL_PASSWORD':
                        env_content += "# Get this from Gmail App Passwords (16 characters)\n"
                    elif key == 'SECRET_KEY':
                        env_content += "# Generate with: python -c 'import secrets; print(secrets.token_hex(32))'\n"
                    
                    env_content += f"{key}={value}\n"
                    
                    if key in ['ADMIN_EMAIL', 'SECRET_KEY', 'PORT']:
                        env_content += "\n"
                
                with open('.env', 'w') as f:
                    f.write(env_content)
                
                if env_exists:
                    self.log_fix(f"Updated .env file with {len(missing_vars)} missing variables")
                else:
                    self.log_fix("Created complete .env file template")
                
                print("📝 IMPORTANT: Edit .env file with your actual values!")
                
            except Exception as e:
                print(f"❌ Failed to create/update .env: {e}")
        else:
            print("✅ .env file has all required variables")
    
    def fix_app_imports(self):
        """Fix common import and configuration issues in app.py"""
        print("\n🐍 CHECKING APP.PY CONFIGURATION")
        print("=" * 40)
        
        app_files = ['app.py', 'app - Copy.py']
        app_file = None
        
        for filename in app_files:
            if os.path.exists(filename):
                app_file = filename
                break
        
        if not app_file:
            print("❌ app.py file not found!")
            return
        
        print(f"✅ Found app file: {app_file}")
        
        try:
            with open(app_file, 'r') as f:
                content = f.read()
            
            # Check for required components
            checks = {
                'from dotenv import load_dotenv': 'Environment variable loading',
                'class ImprovedEmailSender': 'Email sender class',
                'def send_logsheet_to_ops': 'Logsheet email function',
                'CSRFProtect(app)': 'CSRF protection',
                'os.makedirs(UPLOAD_FOLDER': 'Upload folder creation'
            }
            
            for check, description in checks.items():
                if check in content:
                    print(f"✅ {description}: Found")
                else:
                    print(f"⚠️  {description}: Missing or different")
            
        except Exception as e:
            print(f"❌ Error checking app.py: {e}")
    
    def create_test_ops_email(self):
        """Create a test operations email entry if none exist"""
        print("\n📧 CHECKING OPERATIONS EMAILS")
        print("=" * 40)
        
        db_path = os.path.join('data', 'pilot_portal.db')
        
        if not os.path.exists(db_path):
            print("⚠️  Database not found - will be created when app starts")
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if ops_emails table exists and has entries
            cursor.execute("SELECT COUNT(*) FROM ops_emails WHERE is_active = TRUE")
            active_count = cursor.fetchone()[0]
            
            if active_count == 0:
                # Get admin email from environment for test
                admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
                
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO ops_emails (email, is_active, description)
                        VALUES (?, ?, ?)
                    ''', (admin_email, True, 'Auto-created test email'))
                    
                    if cursor.rowcount > 0:
                        conn.commit()
                        self.log_fix(f"Created test operations email: {admin_email}")
                        print("⚠️  IMPORTANT: Replace with actual operations email in admin panel!")
                    else:
                        print(f"✅ Operations email already exists: {admin_email}")
                        
                except sqlite3.IntegrityError:
                    print(f"✅ Operations email already exists: {admin_email}")
            else:
                print(f"✅ Found {active_count} active operations email(s)")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error with operations emails: {e}")
    
    def show_post_fix_instructions(self):
        """Show instructions for what to do after fixes are applied"""
        print("\n🎯 POST-FIX INSTRUCTIONS")
        print("=" * 40)
        
        print("1. 📧 CONFIGURE GMAIL:")
        print("   - Edit .env file with your Gmail credentials")
        print("   - Use Gmail App Password (16 characters)")
        print("   - Enable 2-factor authentication first")
        print()
        
        print("2. 🔑 SET SECRET KEY:")
        print("   - Generate secure key: python -c 'import secrets; print(secrets.token_hex(32))'")
        print("   - Update SECRET_KEY in .env file")
        print()
        
        print("3. 📬 CONFIGURE OPERATIONS EMAILS:")
        print("   - Start app: python app.py")
        print("   - Login as admin (check console for PIN)")
        print("   - Go to Admin → Ops Emails")
        print("   - Add real operations email addresses")
        print()
        
        print("4. 🧪 TEST SYSTEM:")
        print("   - Run: python email_diagnostic.py")
        print("   - Test in admin panel: Admin → Test Email")
        print("   - Submit test logsheet as pilot")
        print()
        
        print("5. 🚀 DEPLOY:")
        print("   - All tests passing? You're ready to go!")
    
    def run_all_fixes(self):
        """Run all automated fixes"""
        print("🔧 FROSTY'S EMAIL SYSTEM AUTO-FIX")
        print("=" * 50)
        print("Automatically fixing common email issues...")
        print()
        
        # Run all fixes
        self.fix_directories()
        self.fix_env_file()
        self.fix_database_schema()
        self.fix_csrf_tokens()
        self.fix_app_imports()
        self.create_test_ops_email()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 AUTO-FIX SUMMARY")
        print("=" * 50)
        
        if self.fixes_applied:
            print(f"🔧 FIXES APPLIED ({len(self.fixes_applied)}):")
            for fix in self.fixes_applied:
                print(f"   ✅ {fix}")
            
            print(f"\n🎉 Applied {len(self.fixes_applied)} automatic fixes!")
            
            if self.backup_created:
                print("📦 Backups created before making changes")
            
            self.show_post_fix_instructions()
            
        else:
            print("✅ No fixes needed - system appears to be configured correctly!")
            print("\n🧪 RECOMMENDED NEXT STEP:")
            print("   Run: python email_diagnostic.py")
        
        print("\n" + "=" * 50)

def main():
    """Main fix function"""
    auto_fix = EmailAutoFix()
    
    print("⚠️  This script will modify your files and database!")
    print("   Backups will be created automatically")
    print()
    
    response = input("Continue with automatic fixes? (type 'yes' to proceed): ").lower()
    if response == 'yes':
        auto_fix.run_all_fixes()
    else:
        print("❌ Auto-fix cancelled. No changes made.")
        print("   Run 'python email_diagnostic.py' to identify issues manually")

if __name__ == "__main__":
    main()