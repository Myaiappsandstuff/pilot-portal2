#!/usr/bin/env python3
"""
Template Block Fixer Script
Fixes common Jinja2 template block issues
"""

import os
import re

def fix_template_blocks(file_path):
    """Fix template block issues in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Check if template extends base but doesn't have {% block content %}
        if '{% extends "base.html" %}' in content:
            # Check if it has {% block content %}
            if '{% block content %}' not in content:
                # Add {% block content %} after extends
                content = content.replace(
                    '{% extends "base.html" %}',
                    '{% extends "base.html" %}\n\n{% block content %}'
                )
                
                # Make sure there's an {% endblock %} at the end
                if '{% endblock %}' not in content:
                    content += '\n{% endblock %}'
        
        # Fix malformed endblock tags
        # Replace standalone {% endblock %} with proper closing
        content = re.sub(r'{% endblock %}$', '{% endblock %}', content, flags=re.MULTILINE)
        
        # If content was changed, write it back
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"🔧 FIXED: {file_path}"
        else:
            return f"✅ OK: {file_path} (no changes needed)"
            
    except Exception as e:
        return f"❌ ERROR: {file_path} - {str(e)}"

def main():
    """Fix the specific problematic templates"""
    problematic_files = [
        "templates/admin/aircraft.html",
        "templates/admin/dashboard.html", 
        "templates/logsheet/logsheet.html",
        "templates/logsheet/photo.html"
    ]
    
    print("🔧 Template Block Fixer")
    print("=" * 40)
    
    for file_path in problematic_files:
        if os.path.exists(file_path):
            result = fix_template_blocks(file_path)
            print(result)
        else:
            print(f"⚠️  SKIP: {file_path} (file not found)")
    
    print("\n🎯 Manual fixes needed:")
    print("Some templates may need manual attention. Check these:")
    print("1. Make sure every template that extends base.html has {% block content %}")
    print("2. Make sure every {% block content %} has a matching {% endblock %}")
    print("3. Remove any stray {% endblock %} tags without opening blocks")

if __name__ == "__main__":
    main()