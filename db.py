"""Database module for SQLite operations."""

import sqlite3
import logging
from datetime import datetime, date
from typing import List, Dict, Optional, Any, Tuple
from contextlib import contextmanager


logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for the ticket booking bot."""
    
    def __init__(self, db_path: str):
        """Initialize database with given path."""
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def init_db(self) -> None:
        """Initialize database tables and populate with sample data."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    time TEXT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    base_ticket_price REAL NOT NULL
                )
            """)
            
            # Create bookings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    customer_name TEXT NOT NULL,
                    customer_phone TEXT NOT NULL,
                    tickets_count INTEGER NOT NULL,
                    notes TEXT,
                    payment_method TEXT NOT NULL,
                    total_price REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (event_id) REFERENCES events (id)
                )
            """)
            
            # Create feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    rating INTEGER,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (event_id) REFERENCES events (id)
                )
            """)
            
            conn.commit()
            
            # Populate with sample data if tables are empty
            self._populate_sample_data(cursor, conn)
            
        logger.info("Database initialized successfully")
    
    def _populate_sample_data(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> None:
        """Populate database with sample events and bookings."""
        # Check if events table is empty
        cursor.execute("SELECT COUNT(*) FROM events")
        if cursor.fetchone()[0] > 0:
            return  # Data already exists
        
        # Sample events
        sample_events = [
            ("2025-08-12", "19:00", "Французская классика: Бордо и Бургундия", "concert", 2500.0),
            ("2025-08-19", "20:00", "Вино и сыр: идеальные пары", "concert", 3000.0),
            ("2025-08-26", "18:30", "Новый Свет: вина Чили и Аргентины", "concert", 2800.0),
            ("2025-09-05", "19:30", "Классика кино: Касабланка", "movie", 800.0),
            ("2025-09-12", "20:00", "Гамлет", "play", 1500.0),
            ("2025-09-20", "19:00", "Джазовый вечер", "concert", 2200.0),
        ]
        
        cursor.executemany("""
            INSERT INTO events (date, time, title, category, base_ticket_price)
            VALUES (?, ?, ?, ?, ?)
        """, sample_events)
        
        # Sample bookings (for demonstration)
        now = datetime.now().isoformat()
        sample_bookings = [
            (1, 123456789, "user1", "Петр Соловьев", "+79990002233", 2, 
             "Предпочтение к сухим винам", "cash", 5000.0, "confirmed", now, now),
            (2, 987654321, "user2", "Анна Чистякова", "+79991113344", 4, 
             "Без пожеланий", "online_stub", 12000.0, "confirmed", now, now),
            (3, 555666777, "user3", "Ольга Иванова", "+79585116694", 3, 
             "Вегетарианские закуски", "cash", 8400.0, "pending", now, now),
        ]
        
        cursor.executemany("""
            INSERT INTO bookings (event_id, user_id, username, customer_name, customer_phone,
                                tickets_count, notes, payment_method, total_price, status,
                                created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_bookings)
        
        conn.commit()
        logger.info("Sample data populated successfully")
    
    # Event operations
    def get_events(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all events, optionally filtered by category."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if category:
                cursor.execute("""
                    SELECT * FROM events 
                    WHERE category = ? AND date >= date('now')
                    ORDER BY date, time
                """, (category,))
            else:
                cursor.execute("""
                    SELECT * FROM events 
                    WHERE date >= date('now')
                    ORDER BY date, time
                """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get event by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_events(self) -> List[Dict[str, Any]]:
        """Get all events (for admin)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events ORDER BY date, time")
            return [dict(row) for row in cursor.fetchall()]
    
    # Booking operations
    def create_booking(self, event_id: int, user_id: int, username: Optional[str],
                      customer_name: str, customer_phone: str, tickets_count: int,
                      notes: Optional[str], payment_method: str, total_price: float) -> int:
        """Create a new booking and return booking ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO bookings (event_id, user_id, username, customer_name, customer_phone,
                                    tickets_count, notes, payment_method, total_price, status,
                                    created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)
            """, (event_id, user_id, username, customer_name, customer_phone,
                  tickets_count, notes, payment_method, total_price, now, now))
            
            booking_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Created booking {booking_id} for user {user_id}")
            return booking_id
    
    def get_bookings_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all bookings for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.*, e.date, e.time, e.title, e.category
                FROM bookings b
                JOIN events e ON b.event_id = e.id
                WHERE b.user_id = ?
                ORDER BY b.created_at DESC
            """, (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_bookings(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent bookings for admin."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.*, e.date, e.time, e.title, e.category
                FROM bookings b
                JOIN events e ON b.event_id = e.id
                ORDER BY b.created_at DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_booking_status(self, booking_id: int, status: str) -> bool:
        """Update booking status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute("""
                UPDATE bookings 
                SET status = ?, updated_at = ?
                WHERE id = ?
            """, (status, now, booking_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            
            if success:
                logger.info(f"Updated booking {booking_id} status to {status}")
            
            return success
    
    def get_booking_by_id(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """Get booking by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.*, e.date, e.time, e.title, e.category
                FROM bookings b
                JOIN events e ON b.event_id = e.id
                WHERE b.id = ?
            """, (booking_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # Feedback operations
    def create_feedback(self, event_id: int, user_id: int, text: str, 
                       rating: Optional[int] = None) -> int:
        """Create feedback and return feedback ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO feedback (event_id, user_id, text, rating, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (event_id, user_id, text, rating, now))
            
            feedback_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Created feedback {feedback_id} for event {event_id}")
            return feedback_id
    
    def get_feedback_by_event(self, event_id: int) -> List[Dict[str, Any]]:
        """Get all feedback for an event."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT f.*, e.title, e.date
                FROM feedback f
                JOIN events e ON f.event_id = e.id
                WHERE f.event_id = ?
                ORDER BY f.created_at DESC
            """, (event_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_user_attended_events(self, user_id: int) -> List[Dict[str, Any]]:
        """Get events that user has confirmed bookings for or past events."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT e.*
                FROM events e
                JOIN bookings b ON e.id = b.event_id
                WHERE b.user_id = ? 
                AND (b.status = 'confirmed' OR e.date < date('now'))
                ORDER BY e.date DESC
            """, (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]