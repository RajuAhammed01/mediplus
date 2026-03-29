#!/usr/bin/env python
"""
MySQL Connection Test for MediPlus
"""

import os
import sys

# Add the project root directory to Python path
# This is the key fix!
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediplus.settings')

try:
    import django
    django.setup()
    from django.db import connection
    from django.db.utils import OperationalError
except ImportError as e:
    print(f" Failed to import Django: {e}")
    print(f"Current Python path: {sys.path}")
    print(f"Project root: {project_root}")
    sys.exit(1)

print("=" * 50)
print("Testing MySQL Connection for MediPlus")
print("=" * 50)

# Print debug info
print(f"Project Root: {project_root}")
print(f"Python Path: {sys.path[0]}")
print("-" * 50)

try:
    # Test the connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f" SUCCESS: Connected to MySQL!")
        print(f" MySQL Version: {version}")
        
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f" Database: {db_name}")
        
        cursor.execute("SELECT CURRENT_USER()")
        user = cursor.fetchone()[0]
        print(f" User: {user}")
        
except OperationalError as e:
    print(f" FAILED: Could not connect to MySQL database")
    print(f"Error: {e}")
    
    print("\n Troubleshooting Tips:")
    print("1. Make sure MySQL is running")
    print("2. Check your .env file has correct database credentials")
    print("3. Try creating the database manually:")
    print("   mysql -u root -p -e 'CREATE DATABASE mediplus_db;'")
    print("4. Test MySQL connection directly:")
    print("   mysql -u root -p -e 'SHOW DATABASES;'")