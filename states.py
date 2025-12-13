"""State management for user conversations."""

from enum import Enum
from typing import Dict, Optional, Any
from dataclasses import dataclass, field


class UserState(Enum):
    """Enumeration of possible user conversation states."""
    IDLE = "idle"
    BOOKING_SELECT_EVENT = "booking_select_event"
    BOOKING_ENTER_TICKETS = "booking_enter_tickets"
    BOOKING_ENTER_NOTES = "booking_enter_notes"
    BOOKING_ENTER_NAME = "booking_enter_name"
    BOOKING_ENTER_PHONE = "booking_enter_phone"
    BOOKING_SELECT_PAYMENT = "booking_select_payment"
    FEEDBACK_SELECT_EVENT = "feedback_select_event"
    FEEDBACK_ENTER_TEXT = "feedback_enter_text"
    FEEDBACK_ENTER_RATING = "feedback_enter_rating"


@dataclass
class BookingData:
    """Data structure for booking in progress."""
    event_id: Optional[int] = None
    tickets_count: Optional[int] = None
    notes: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    payment_method: Optional[str] = None


@dataclass
class FeedbackData:
    """Data structure for feedback in progress."""
    event_id: Optional[int] = None
    text: Optional[str] = None
    rating: Optional[int] = None


@dataclass
class UserSession:
    """User session data including state and temporary data."""
    state: UserState = UserState.IDLE
    booking_data: BookingData = field(default_factory=BookingData)
    feedback_data: FeedbackData = field(default_factory=FeedbackData)


class StateManager:
    """Manages user conversation states and temporary data."""
    
    def __init__(self):
        """Initialize state manager with empty user sessions."""
        self._sessions: Dict[int, UserSession] = {}
    
    def get_session(self, user_id: int) -> UserSession:
        """Get or create user session."""
        if user_id not in self._sessions:
            self._sessions[user_id] = UserSession()
        return self._sessions[user_id]
    
    def set_state(self, user_id: int, state: UserState) -> None:
        """Set user conversation state."""
        session = self.get_session(user_id)
        session.state = state
    
    def get_state(self, user_id: int) -> UserState:
        """Get current user conversation state."""
        return self.get_session(user_id).state
    
    def clear_session(self, user_id: int) -> None:
        """Clear user session data and reset to idle state."""
        if user_id in self._sessions:
            self._sessions[user_id] = UserSession()
    
    def get_booking_data(self, user_id: int) -> BookingData:
        """Get booking data for user."""
        return self.get_session(user_id).booking_data
    
    def get_feedback_data(self, user_id: int) -> FeedbackData:
        """Get feedback data for user."""
        return self.get_session(user_id).feedback_data