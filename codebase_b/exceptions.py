"""
Domain and Application Exceptions for Campus Booking System (Codebase B).
Replaces raw boolean flags and silent failures with explicit exception handling.
"""


class BookingException(Exception):
    """Base exception for all domain and service errors."""
    pass


class ResourceNotFoundError(BookingException):
    """Raised when an entity (User, Room, Reservation) does not exist."""
    pass


class InactiveResourceError(BookingException):
    """Raised when an operation targets a deactivated User or Room."""
    pass


class InvalidTimeRangeError(BookingException):
    """Raised when requested start/end times are logically invalid."""
    pass


class OperatingHoursExceededError(BookingException):
    """Raised when requested booking slot falls outside operating hours."""
    pass


class SlotConflictError(BookingException):
    """Raised when a room is already occupied during the requested interval."""
    pass


class QuotaExceededError(BookingException):
    """Raised when a user policy limit (e.g. daily hours cap) is violated."""
    pass


class BookingStateError(BookingException):
    """Raised when an invalid state transition is attempted on a booking."""
    pass
