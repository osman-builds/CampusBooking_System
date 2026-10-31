"""
Campus Facility & Room Booking System - CR-02 (Adaptive Maintenance)
Module: models.py - Domain Entities Adapted for Timezone-Aware Server Environments

Adaptive Modifications over Codebase B Baseline:
- Replaces naive host-dependent datetime.now() with timezone-aware CAMPUS_TIMEZONE (UTC+08:00)
  so reservation audit timestamps remain deterministic across UTC Linux/Docker containers
  and local campus servers without external tzdata dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum

# Malaysian Campus Standard Time (MYT / Asia/Kuala_Lumpur = UTC+08:00, no DST)
CAMPUS_TIMEZONE = timezone(timedelta(hours=8), name="UTC+08:00")


def campus_now() -> datetime:
    """Returns a timezone-aware datetime anchored to campus local time (UTC+08:00)."""
    return datetime.now(CAMPUS_TIMEZONE)


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


class OperatingHoursExceededError(BookingException):
    """Raised when booking is outside 08:00 - 22:00 operating window."""
    pass


class SlotConflictError(BookingException):
    """Raised when room is already reserved for the requested slot."""
    pass


class QuotaExceededError(BookingException):
    """Raised when student exceeds max 2 hours daily allowance."""
    pass


class StoragePersistenceError(BookingException):
    """Raised when the underlying relational database environment encounters an I/O or constraint fault."""
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
    created_at: datetime = field(default_factory=campus_now)

    @property
    def duration(self) -> int:
        return self.end_hour - self.start_hour

    @property
    def is_active(self) -> bool:
        return self.status == ReservationStatus.CONFIRMED
