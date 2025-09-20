#!/usr/bin/env python3
"""
CSS Namespace Script - Tạo namespace cho tất cả CSS files để tránh xung đột
"""

import os
import re

# Mapping các CSS files với namespace tương ứng
CSS_NAMESPACES = {
    'users.css': 'users-page',
    'checkin.css': 'checkin-page', 
    'dashboard.css': 'dashboard-page',
    'auth.css': 'auth-page',
    'area_management.css': 'area-management-page',
    'home.css': 'home-page'
}

def namespace_css_file(file_path, namespace):
    """Thêm namespace cho một CSS file"""
    print(f"Processing {file_path} with namespace .{namespace}")
    
    # Đọc file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tìm tất cả CSS selectors (class và id)
    # Pattern để match CSS selectors: .class-name hoặc #id-name
    pattern = r'^(\s*)(\.[\w-]+\s*\{|#[\w-]+\s*\{|@media[^{]*\{)'
    
    lines = content.split('\n')
    new_lines = []
    in_media_query = False
    media_query_indent = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Kiểm tra nếu là @media query
        if stripped.startswith('@media'):
            in_media_query = True
            media_query_indent = len(line) - len(line.lstrip())
            new_lines.append(line)
            continue
        
        # Kiểm tra nếu kết thúc media query
        if in_media_query and stripped == '}' and len(line) - len(line.lstrip()) == media_query_indent:
            in_media_query = False
            new_lines.append(line)
            continue
        
        # Nếu trong media query, không namespace
        if in_media_query:
            new_lines.append(line)
            continue
        
        # Kiểm tra nếu là CSS selector
        if re.match(r'^\s*\.[\w-]+\s*\{', line) or re.match(r'^\s*#[\w-]+\s*\{', line):
            # Thêm namespace
            indent = len(line) - len(line.lstrip())
            selector = line.lstrip()
            
            # Bỏ dấu { ở cuối
            if selector.endswith(' {'):
                selector = selector[:-2]
                new_line = ' ' * indent + f'.{namespace} {selector} {{'
            else:
                new_line = ' ' * indent + f'.{namespace} {selector}'
            
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    
    # Ghi lại file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"✅ Namespaced {file_path}")

def main():
    """Main function"""
    css_dir = 'static/css'
    
    print("🚀 Starting CSS namespacing...")
    
    for filename, namespace in CSS_NAMESPACES.items():
        file_path = os.path.join(css_dir, filename)
        
        if os.path.exists(file_path):
            namespace_css_file(file_path, namespace)
        else:
            print(f"❌ File not found: {file_path}")
    
    print("✅ CSS namespacing completed!")

if __name__ == '__main__':
    main()
