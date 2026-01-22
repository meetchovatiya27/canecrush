#!/usr/bin/env python
"""
Django Project Cleanup Script
This script helps identify and remove unused files safely.
Run with: python cleanup_script.py
"""

import os
import sys
from pathlib import Path

# Files and directories to delete (safe to remove)
FILES_TO_DELETE = [
    'cane_crush/templates/payment.html',
    'cane_crush/templates/thankyou.html',
    'cane_crush/templates/text.txt',
]

DIRECTORIES_TO_DELETE = [
    'cane_crush/static/images/blogs/ChatGPT_files',
    'cane_crush/static/images/blogs/ChatGPT.html',
]

def confirm_deletion(file_path):
    """Ask user for confirmation before deleting"""
    response = input(f"Delete {file_path}? (y/n): ").lower()
    return response == 'y'

def delete_file(file_path):
    """Safely delete a file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ Deleted: {file_path}")
            return True
        else:
            print(f"⚠️  File not found: {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error deleting {file_path}: {e}")
        return False

def delete_directory(dir_path):
    """Safely delete a directory and its contents"""
    try:
        if os.path.exists(dir_path):
            import shutil
            shutil.rmtree(dir_path)
            print(f"✅ Deleted directory: {dir_path}")
            return True
        else:
            print(f"⚠️  Directory not found: {dir_path}")
            return False
    except Exception as e:
        print(f"❌ Error deleting {dir_path}: {e}")
        return False

def main():
    """Main cleanup function"""
    print("=" * 60)
    print("Django Project Cleanup Script")
    print("=" * 60)
    print("\nThis script will help you remove unused files.")
    print("Please review PROJECT_CLEANUP_REPORT.md before proceeding.\n")
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Delete files
    print("\n📄 Files to delete:")
    print("-" * 60)
    deleted_files = 0
    for file_path in FILES_TO_DELETE:
        if confirm_deletion(file_path):
            if delete_file(file_path):
                deleted_files += 1
    
    # Delete directories
    print("\n📁 Directories to delete:")
    print("-" * 60)
    deleted_dirs = 0
    for dir_path in DIRECTORIES_TO_DELETE:
        if confirm_deletion(dir_path):
            if delete_directory(dir_path):
                deleted_dirs += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Cleanup Summary")
    print("=" * 60)
    print(f"Files deleted: {deleted_files}/{len(FILES_TO_DELETE)}")
    print(f"Directories deleted: {deleted_dirs}/{len(DIRECTORIES_TO_DELETE)}")
    print("\n✅ Cleanup complete!")
    print("\nNext steps:")
    print("1. Run: python manage.py check")
    print("2. Test your application")
    print("3. Run: python manage.py collectstatic (if needed)")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Auto mode - delete without confirmation (use with caution)
        print("⚠️  AUTO MODE: Deleting without confirmation")
        for file_path in FILES_TO_DELETE:
            delete_file(file_path)
        for dir_path in DIRECTORIES_TO_DELETE:
            delete_directory(dir_path)
    else:
        main()

