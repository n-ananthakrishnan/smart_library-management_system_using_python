#!/usr/bin/env python
"""Reset database to match current schema"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Set environment before importing app
os.environ['FLASK_ENV'] = 'development'

from app import app, db
from models import User, Book, Borrowing, Reservation, Review, ActivityLog, Notification

with app.app_context():
    try:
        print("🔄 Resetting database...")
        print()
        
        # Drop all tables
        print("1️⃣  Dropping existing tables...")
        db.drop_all()
        print("   ✓ Tables dropped")
        
        # Create all tables with new schema
        print("2️⃣  Creating new tables with updated schema...")
        db.create_all()
        print("   ✓ Tables created")
        
        # Verify Book table has all columns
        print("3️⃣  Verifying Book table schema...")
        inspector = db.inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('book')]
        print(f"   Book columns: {', '.join(columns[:8])}...")
        
        required_columns = ['id', 'title', 'author', 'isbn', 'barcode', 'genre', 'total_copies']
        missing = [col for col in required_columns if col not in columns]
        
        if missing:
            print(f"   ✗ Missing columns: {missing}")
        else:
            print("   ✓ All required columns present")
        
        print()
        print("✨ Database reset successful!")
        print("   You can now run: python app.py")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
