"""
Campus Facility & Room Booking System — CR-01 (Corrective Maintenance)
Module: models.py - Domain Entities, Enums, and Corrected Domain Exception Hierarchy

Corrective Additions over Codebase B Baseline:
- InvalidDateError: Domain exception for malformed or nonexistent calendar dates.
- InvalidTimeSlotError: Domain exception for non-integer (float/boolean/string) hour inputs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# --- Enums ---
class UserRole(str, Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    STAFF = "staff"
    ADMIN = "admin"


class RoomType(str, Enum):
    STANDARD = "standard"
    LAB = "lab"
    STUDIO = "studio"


class ReservationStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


# --- Domain Exceptions ---
class BookingException(Exception):
    """Base exception for booking domain errors."""
    pass


class ResourceNotFoundError(BookingException):
    """Raised when user or room does not exist."""
    pass


class InvalidDateError(BookingException):
    """Raised when booking date string is not a valid calendar date in YYYY-MM-DD format."""
    pass


class InvalidTimeSlotError(BookingException):
    """Raised when start_hour or end_hour is not a strict integer (e.g., float, bool, str)."""
    pass


class OperatingHoursExceededError(BookingException):
    """Raised when booking is outside 08:00 - 22:00 operating window."""
    pass


class SlotConflictError(BookingException):
    """Raised when room is already reserved for the requested slot."""
    pass


class QuotaExceededError(BookingException):
    """Raised when student exceeds max 2 hours daily allowance."""
    pass


# --- Domain Entities ---
@dataclass(frozen=True)
class User:
    user_id: str
    name: str
    role: UserRole
    email: str = ""
    is_active: bool = True

    def is_student(self) -> bool:
        return self.role == UserRole.STUDENT


@dataclass(frozen=True)
class Room:
    room_id: str
    name: str
    room_type: RoomType
    capacity: int
    hourly_rate: float
    is_active: bool = True


@dataclass
class Reservation:
    booking_id: int
    token: str
    user_id: str
    room_id: str
    date_str: str
    start_hour: int
    end_hour: int
    base_cost: float
    discount: float
    surcharge: float
    total_cost: float
    status: ReservationStatus = ReservationStatus.CONFIRMED
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def duration(self) -> int:
        return self.end_hour - self.start_hour

    @property
    def is_active(self) -> bool:
        return self.status == ReservationStatus.CONFIRMED
