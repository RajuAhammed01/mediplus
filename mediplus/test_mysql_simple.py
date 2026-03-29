#!/usr/bin/env python
"""
Simple MySQL Connection Test for MediPlus
Run this from the project root directory
"""

import os
import sys
import pymysql

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediplus.settings')

# Try to import Django
try:
    import django
    django.setup()
    from django.db import connection
except ImportError as e:
    print(f"❌ Django import error: {e}")
    print("Make sure you're in the right directory and virtualenv is activated")
    sys.exit(1)

print("=" * 50)
print("Testing MySQL Connection for MediPlus")
print("=" * 50)

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"✅ Connected to MySQL!")
        print(f"📊 MySQL Version: {version}")
        
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f"🗄️  Database: {db_name}")
        
        cursor.execute("SELECT CURRENT_USER()")
        user = cursor.fetchone()[0]
        print(f"👤 User: {user}")
        
        # Test a simple query
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📋 Tables found: {len(tables)}")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
    
    # Provide helpful troubleshooting
    print("\n🔧 Troubleshooting Tips:")
    print("1. Make sure MySQL is running")
    print("2. Check your .env file has correct database credentials")
    print("3. Try creating the database manually:")
    print("   mysql -u root -p -e 'CREATE DATABASE mediplus_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'")
    print("4. Check if mysqlclient is installed: pip install mysqlclient")