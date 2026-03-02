"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: get_project_structure.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
import os
from pathlib import Path
from datetime import datetime

PROJECT_DIR = "."
OUTPUT_FILE = "project_snapshot.txt"

# File extensions to include
INCLUDE_EXTENSIONS = {'.py', '.txt', '.md', '.json', '.yaml', '.yml', '.toml', '.cfg', '.ini'}

def get_directory_tree(path, prefix=""):
    """Generate directory tree structure"""
    lines = []
    try:
        items = sorted(Path(path).iterdir(), key=lambda x: (not x.is_dir(), x.name))
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            next_prefix = "    " if is_last else "│   "
            
            if item.is_dir():
                lines.append(f"{prefix}{current_prefix}{item.name}/")
                lines.extend(get_directory_tree(item, prefix + next_prefix))
            else:
                lines.append(f"{prefix}{current_prefix}{item.name}")
    except PermissionError:
        pass
    return lines

def main():
    project_name = Path.cwd().name
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # Header
        f.write("=" * 80 + "\n")
        f.write(f"PROJECT STRUCTURE: {project_name}\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write("=" * 80 + "\n\n")
        
        # Directory tree
        f.write("DIRECTORY STRUCTURE:\n")
        f.write("-" * 80 + "\n")
        f.write(f"{project_name}/\n")
        tree_lines = get_directory_tree(PROJECT_DIR)
        f.write("\n".join(tree_lines))
        f.write("\n\n")
        
        # File contents
        f.write("=" * 80 + "\n")
        f.write("FILE CONTENTS:\n")
        f.write("=" * 80 + "\n")
        
        project_path = Path(PROJECT_DIR)
        for file_path in sorted(project_path.rglob('*')):
            if file_path.is_file() and file_path.suffix in INCLUDE_EXTENSIONS:
                try:
                    f.write(f"\n\n{'-' * 80}\n")
                    f.write(f"FILE: {file_path}\n")
                    f.write(f"{'-' * 80}\n")
                    
                    with open(file_path, 'r', encoding='utf-8') as source_file:
                        f.write(source_file.read())
                except Exception as e:
                    f.write(f"[Error reading file: {e}]\n")
    
    print(f"Project snapshot saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

