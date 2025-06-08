#!/usr/bin/env python3
"""
CSRF Token Auto-Fixer for Flask Templates
This script finds HTML templates with POST forms and adds CSRF tokens where needed.
"""

import os
import re
import glob
from pathlib import Path

def find_templates(base_dir="templates"):
    """Find all HTML template files"""
    template_files = []
    
    # Look for .html files in templates directory and subdirectories
    patterns = [
        f"{base_dir}/**/*.html",
        f"{base_dir}/*.html"
    ]
    
    for pattern in patterns:
        template_files.extend(glob.glob(pattern, recursive=True))
    
    return template_files

def has_post_form(content):
    """Check if the file contains a POST form"""
    # Look for forms with method="POST" (case insensitive)
    post_form_pattern = r'<form[^>]*method\s*=\s*["\']POST["\'][^>]*>'
    return bool(re.search(post_form_pattern, content, re.IGNORECASE))

def has_csrf_token(content):
    """Check if the file already has a CSRF token"""
    # Look for csrf_token in various forms
    csrf_patterns = [
        r'csrf_token\(\)',
        r'name\s*=\s*["\']csrf_token["\']',
        r'{{ csrf_token\(\) }}'
    ]
    
    for pattern in csrf_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False

def add_csrf_token(content):
    """Add CSRF token to POST forms that don't have it"""
    # Pattern to find opening form tags with POST method
    form_pattern = r'(<form[^>]*method\s*=\s*["\']POST["\'][^>]*>)'
    
    def replace_form(match):
        form_tag = match.group(1)
        # Add CSRF token right after the form tag
        csrf_line = '\n            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>'
        return form_tag + csrf_line
    
    # Replace all POST forms
    updated_content = re.sub(form_pattern, replace_form, content, flags=re.IGNORECASE)
    return updated_content

def process_template(file_path):
    """Process a single template file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if this file needs processing
        if not has_post_form(content):
            return f"⏭️  SKIP: {file_path} (no POST forms)"
        
        if has_csrf_token(content):
            return f"✅ OK: {file_path} (already has CSRF token)"
        
        # Add CSRF token
        updated_content = add_csrf_token(content)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return f"🔧 FIXED: {file_path} (added CSRF token)"
        
    except Exception as e:
        return f"❌ ERROR: {file_path} - {str(e)}"

def main():
    """Main function to process all templates"""
    print("🔍 CSRF Token Auto-Fixer")
    print("=" * 50)
    
    # Check if templates directory exists
    if not os.path.exists("templates"):
        print("❌ Error: 'templates' directory not found!")
        print("   Make sure you're running this script from your Flask project root.")
        return
    
    # Find all template files
    template_files = find_templates()
    
    if not template_files:
        print("❌ No HTML template files found in 'templates' directory")
        return
    
    print(f"📁 Found {len(template_files)} template files")
    print()
    
    # Process each template
    results = []
    for template_file in sorted(template_files):
        result = process_template(template_file)
        results.append(result)
        print(result)
    
    print()
    print("=" * 50)
    
    # Summary
    fixed_count = len([r for r in results if "🔧 FIXED:" in r])
    ok_count = len([r for r in results if "✅ OK:" in r])
    skip_count = len([r for r in results if "⏭️  SKIP:" in r])
    error_count = len([r for r in results if "❌ ERROR:" in r])
    
    print(f"📊 SUMMARY:")
    print(f"   🔧 Fixed: {fixed_count} files")
    print(f"   ✅ Already OK: {ok_count} files")
    print(f"   ⏭️  Skipped: {skip_count} files (no forms)")
    print(f"   ❌ Errors: {error_count} files")
    
    if fixed_count > 0:
        print(f"\n🎉 Successfully added CSRF tokens to {fixed_count} template(s)!")
        print("   Your Flask app should now work without CSRF errors.")
    elif ok_count > 0:
        print(f"\n✨ All templates already have CSRF tokens!")
    
    if error_count > 0:
        print(f"\n⚠️  Please check the {error_count} files with errors manually.")

def dry_run():
    """Run without making changes to see what would be modified"""
    print("🔍 CSRF Token Checker (DRY RUN - No Changes Made)")
    print("=" * 60)
    
    if not os.path.exists("templates"):
        print("❌ Error: 'templates' directory not found!")
        return
    
    template_files = find_templates()
    
    for template_file in sorted(template_files):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not has_post_form(content):
                print(f"⏭️  SKIP: {template_file} (no POST forms)")
            elif has_csrf_token(content):
                print(f"✅ OK: {template_file} (already has CSRF token)")
            else:
                print(f"🔧 NEEDS FIX: {template_file} (missing CSRF token)")
                
        except Exception as e:
            print(f"❌ ERROR: {template_file} - {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        dry_run()
    else:
        print("🚨 This script will modify your template files!")
        print("   Run with --dry-run first to see what would be changed.")
        print()
        
        response = input("Continue and modify files? (type 'yes' to proceed): ").lower()
        if response == 'yes':
            main()
        else:
            print("❌ Cancelled. No files were modified.")
            print("   Run with --dry-run to see what would be changed.")