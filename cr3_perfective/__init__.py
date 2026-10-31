"""
CR-03 (Perfective Maintenance): Attendee Capacity Validation, Smart Space Discovery, O(1) Indexing & NotificationService.
"""

from .models import (
    BookingException,
    CapacityExceededError,
    OperatingHoursExceededError,
    QuotaExceededError,
    Reservation,
    ReservationStatus,
    ResourceNotFoundError,
    Room,
    RoomType,
    SlotConflictError,
    User,
    UserRole,
)
from .services import (
    AbstractNotificationService,
    BookingRepository,
    BookingService,
    ConflictDetector,
    ConsoleNotificationService,
    PricingBreakdown,
    PricingService,
    SilentNotificationService,
)

__all__ = [
    "UserRole",
    "RoomType",
    "ReservationStatus",
    "User",
    "Room",
    "Reservation",
    "BookingException",
    "ResourceNotFoundError",
    "OperatingHoursExceededError",
    "SlotConflictError",
    "QuotaExceededError",
    "CapacityExceededError",
    "PricingBreakdown",
    "PricingService",
    "ConflictDetector",
    "AbstractNotificationService",
    "ConsoleNotificationService",
    "SilentNotificationService",
    "BookingRepository",
    "BookingService",
]
