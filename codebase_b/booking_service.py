"""
Application Orchestration Service for Campus Booking System (Codebase B).
Coordinates use cases via Dependency Injection and raises domain-specific exceptions.
"""

import random
import string
from datetime import datetime, time
from typing import List, Optional

try:
    from conflict_detector import ConflictDetector
    from exceptions import (
        BookingStateError,
        InactiveResourceError,
        InvalidTimeRangeError,
        OperatingHoursExceededError,
        QuotaExceededError,
        ResourceNotFoundError,
        SlotConflictError,
    )
    from models import Reservation, ReservationStatus, Room, User, UserRole
    from notification_service import NotificationService
    from pricing_service import PricingService
    from repository import BookingRepository, RoomRepository, UserRepository
except ImportError:
    from .conflict_detector import ConflictDetector
    from .exceptions import (
        BookingStateError,
        InactiveResourceError,
        InvalidTimeRangeError,
        OperatingHoursExceededError,
        QuotaExceededError,
        ResourceNotFoundError,
        SlotConflictError,
    )
    from .models import Reservation, ReservationStatus, Room, User, UserRole
    from .notification_service import NotificationService
    from .pricing_service import PricingService
    from .repository import BookingRepository, RoomRepository, UserRepository


class BookingService:
    """
    Application service that coordinates the booking workflow.
    Adheres strictly to Dependency Inversion: all dependencies are injected.
    """

    OPERATING_START: time = time(8, 0)
    OPERATING_END: time = time(22, 0)
    STUDENT_MAX_DAILY_HOURS: float = 2.0

    def __init__(
        self,
        booking_repo: BookingRepository,
        room_repo: RoomRepository,
        user_repo: UserRepository,
        conflict_detector: ConflictDetector,
        pricing_service: PricingService,
        notification_service: NotificationService,
    ) -> None:
        self._booking_repo = booking_repo
        self._room_repo = room_repo
        self._user_repo = user_repo
        self._conflict_detector = conflict_detector
        self._pricing_service = pricing_service
        self._notification_service = notification_service

    def create_booking(
        self,
        user_id: str,
        room_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> Reservation:
        """
        Coordinates full booking reservation flow:
        - Validates entities, status, and operating bounds.
        - Checks room collision and user quota constraints.
        - Calculates itemized pricing.
        - Persists reservation record and issues confirmation notification.
        """
        # 1. Validate User
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise ResourceNotFoundError(f"User with ID '{user_id}' does not exist.")
        if not user.is_active:
            raise InactiveResourceError(f"User account '{user_id}' is deactivated.")

        # 2. Validate Room
        room = self._room_repo.find_by_id(room_id)
        if not room:
            raise ResourceNotFoundError(f"Room with ID '{room_id}' does not exist.")
        if not room.is_active:
            raise InactiveResourceError(f"Room '{room_id}' is currently inactive.")

        # 3. Validate Time Bounds
        self._validate_operating_bounds(start_time, end_time)

        # 4. Check for Room Overlap Collisions
        booking_date = start_time.date()
        room_reservations = self._booking_repo.find_by_room_and_date(room_id, booking_date)
        if self._conflict_detector.has_overlap(room_reservations, start_time, end_time):
            raise SlotConflictError(
                f"Room '{room.name}' ({room_id}) is already reserved during the requested interval "
                f"({start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')})."
            )

        # 5. Check Student Daily Quota Limit
        duration_hours = (end_time - start_time).total_seconds() / 3600.0
        if user.is_student():
            user_reservations = self._booking_repo.find_by_user_and_date(user_id, booking_date)
            if self._conflict_detector.exceeds_daily_quota(
                user_reservations,
                new_duration_hours=duration_hours,
                max_daily_hours=self.STUDENT_MAX_DAILY_HOURS
            ):
                raise QuotaExceededError(
                    f"Student daily limit exceeded: User '{user.name}' ({user_id}) cannot book "
                    f"more than {self.STUDENT_MAX_DAILY_HOURS} hours per day."
                )

        # 6. Calculate Financials
        pricing_breakdown = self._pricing_service.calculate_total(room, user, start_time, end_time)

        # 7. Create & Persist Reservation
        confirmation_token = self._generate_token(booking_date)
        reservation = Reservation(
            id=0,  # Will be assigned by repository
            confirmation_token=confirmation_token,
            user_id=user_id,
            room_id=room_id,
            start_time=start_time,
            end_time=end_time,
            total_cost=pricing_breakdown.total_cost,
            status=ReservationStatus.CONFIRMED,
            created_at=datetime.now()
        )
        saved_reservation = self._booking_repo.save(reservation)

        # 8. Dispatch Notification Receipt
        self._notification_service.send_confirmation(
            reservation=saved_reservation,
            user=user,
            room=room,
            breakdown=pricing_breakdown
        )

        return saved_reservation

    def cancel_booking(self, reservation_id: int) -> Reservation:
        """
        Cancels an existing reservation and issues a cancellation notice.
        """
        reservation = self._booking_repo.find_by_id(reservation_id)
        if not reservation:
            raise ResourceNotFoundError(f"Reservation #{reservation_id} not found.")

        if reservation.status == ReservationStatus.CANCELLED:
            raise BookingStateError(f"Reservation #{reservation_id} has already been cancelled.")

        reservation.status = ReservationStatus.CANCELLED
        reservation.cancelled_at = datetime.now()
        saved = self._booking_repo.save(reservation)

        user = self._user_repo.find_by_id(reservation.user_id)
        room = self._room_repo.find_by_id(reservation.room_id)
        if user and room:
            self._notification_service.send_cancellation(saved, user, room)

        return saved

    def get_reservation(self, reservation_id: int) -> Optional[Reservation]:
        """Retrieves a reservation by ID."""
        return self._booking_repo.find_by_id(reservation_id)

    def list_all_reservations(self) -> List[Reservation]:
        """Lists all recorded reservations."""
        return self._booking_repo.find_all()

    def _validate_operating_bounds(self, start_time: datetime, end_time: datetime) -> None:
        """Validates that requested intervals are logically consistent and within facility hours."""
        if start_time.date() != end_time.date():
            raise InvalidTimeRangeError("Bookings must start and end on the same calendar day.")

        if start_time >= end_time:
            raise InvalidTimeRangeError(
                f"Start time ({start_time.strftime('%H:%M')}) must precede end time ({end_time.strftime('%H:%M')})."
            )

        if start_time.time() < self.OPERATING_START or end_time.time() > self.OPERATING_END:
            raise OperatingHoursExceededError(
                f"Requested interval ({start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}) "
                f"is outside campus facility operating hours (08:00 - 22:00)."
            )

    @staticmethod
    def _generate_token(booking_date) -> str:
        """Generates a structured human-readable confirmation token."""
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"SKD-{booking_date.strftime('%Y%m%d')}-{suffix}"
