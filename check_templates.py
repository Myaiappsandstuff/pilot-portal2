#!/usr/bin/env python3
"""
Quick Template Syntax Checker for Frosty's Pilot Portal
Run this to check all your templates for syntax errors before starting the app
"""

import os
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError

def check_template_syntax():
    """Check all templates for syntax errors"""
    
    template_dirs = [
        'templates',
        'templates/admin', 
        'templates/logsheet'
    ]
    
    errors_found = []
    templates_checked = 0
    
    print("🔍 Checking Jinja2 template syntax...")
    print("=" * 50)
    
    for template_dir in template_dirs:
        if not os.path.exists(template_dir):
            print(f"⚠️  Directory not found: {template_dir}")
            continue
            
        try:
            env = Environment(loader=FileSystemLoader(template_dir))
            
            for filename in os.listdir(template_dir):
                if filename.endswith('.html'):
                    templates_checked += 1
                    try:
                        template = env.get_template(filename)
                        # Try to parse the template
                        template.render()
                        print(f"✅ {template_dir}/{filename}")
                        
                    except TemplateSyntaxError as e:
                        error_msg = f"❌ {template_dir}/{filename}: {e.message} (line {e.lineno})"
                        print(error_msg)
                        errors_found.append(error_msg)
                        
                    except Exception as e:
                        # Skip render errors, we only care about syntax
                        if "is undefined" not in str(e):
                            error_msg = f"⚠️  {template_dir}/{filename}: {e}"
                            print(error_msg)
                            
        except Exception as e:
            print(f"❌ Error checking {template_dir}: {e}")
    
    print("=" * 50)
    print(f"📊 Templates checked: {templates_checked}")
    
    if errors_found:
        print(f"❌ Syntax errors found: {len(errors_found)}")
        print("\n🔧 ERRORS TO FIX:")
        for error in errors_found:
            print(f"   {error}")
        return False
    else:
        print("✅ All templates have valid syntax!")
        return True

if __name__ == "__main__":
    print("🛠️  Frosty's Template Syntax Checker")
    print("=" * 40)
    
    success = check_template_syntax()
    
    if success:
        print("\n🎉 All clear! Your templates are ready to go.")
    else:
        print("\n💥 Fix the syntax errors above before starting your app.")
        exit(1)