"""
Domain Models for Campus Facility & Room Booking System (Codebase B)
Adheres to Single Responsibility Principle (SRP) by encapsulating domain state.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class UserRole(str, Enum):
    """Enumeration of user roles within the campus ecosystem."""
    STUDENT = "STUDENT"
    STAFF = "STAFF"
    ADMIN = "ADMIN"


class RoomType(str, Enum):
    """Enumeration of facility/room categories."""
    STANDARD = "STANDARD"
    LAB = "LAB"
    STUDIO = "STUDIO"


class ReservationStatus(str, Enum):
    """Lifecycle states of a reservation."""
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class User:
    """Represents an authorized system user."""
    user_id: str
    name: str
    role: UserRole
    email: str = ""
    is_active: bool = True

    def is_student(self) -> bool:
        """Convenience method checking student role."""
        return self.role == UserRole.STUDENT


@dataclass(frozen=True)
class Room:
    """Represents a reservable campus space."""
    room_id: str
    name: str
    room_type: RoomType
    capacity: int
    base_hourly_rate: float
    is_active: bool = True


@dataclass
class Reservation:
    """Represents a finalized booking for a room."""
    id: int
    confirmation_token: str
    user_id: str
    room_id: str
    start_time: datetime
    end_time: datetime
    total_cost: float
    status: ReservationStatus = ReservationStatus.CONFIRMED
    created_at: datetime = field(default_factory=datetime.now)
    cancelled_at: Optional[datetime] = None

    @property
    def duration_hours(self) -> float:
        """Calculates reservation duration in decimal hours."""
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 3600.0

    @property
    def is_active(self) -> bool:
        """Returns True if the reservation is actively confirmed."""
        return self.status == ReservationStatus.CONFIRMED
