#!/usr/bin/env python3
"""
Simple test script to verify database initialization and basic operations.
Run this to test the database setup before starting the bot.
"""

import os
import sys
from db import Database


def test_database():
    """Test database initialization and basic operations."""
    print("🧪 Testing database initialization...")
    
    # Use test database
    test_db_path = "test_bot_database.db"
    
    try:
        # Initialize database
        db = Database(test_db_path)
        db.init_db()
        print("✅ Database initialized successfully")
        
        # Test getting events
        events = db.get_events()
        print(f"✅ Found {len(events)} events")
        
        # Test getting events by category
        concerts = db.get_events("concert")
        print(f"✅ Found {len(concerts)} concerts")
        
        # Test getting all events (admin)
        all_events = db.get_all_events()
        print(f"✅ Found {len(all_events)} total events")
        
        # Test getting bookings (should have sample data)
        recent_bookings = db.get_recent_bookings(10)
        print(f"✅ Found {len(recent_bookings)} recent bookings")
        
        # Test getting user bookings
        user_bookings = db.get_bookings_by_user(123456789)
        print(f"✅ Found {len(user_bookings)} bookings for sample user")
        
        # Test getting attended events
        attended = db.get_user_attended_events(123456789)
        print(f"✅ Found {len(attended)} attended events for sample user")
        
        print("\n🎉 All database tests passed!")
        
        # Show sample data
        print("\n📋 Sample Events:")
        for event in events[:3]:
            print(f"  - {event['title']} ({event['date']}) - {event['base_ticket_price']}₽")
        
        print("\n📋 Sample Bookings:")
        for booking in recent_bookings[:2]:
            print(f"  - Booking #{booking['id']}: {booking['customer_name']} - {booking['status']}")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    finally:
        # Clean up test database
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            print(f"\n🧹 Cleaned up test database: {test_db_path}")
    
    return True


if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)