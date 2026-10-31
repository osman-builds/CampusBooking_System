"""
Campus Facility & Room Booking System — CR-01 (Corrective Maintenance)
Module: services.py - Corrected Input Boundary Validation & Canonical Date Normalization

Resolves Three Defects Identified in Codebase B:
1. Canonical Date Normalization ('YYYY-MM-DD'): Prevents double-booking and 4x student daily
   quota bypasses caused by non-zero-padded date strings (e.g., '2026-1-5' vs '2026-01-05'),
   and guarantees strict 8-digit date segments in 'SKD-YYYYMMDD-XXXXXX' confirmation tokens.
2. Domain Exception Containment: Wraps invalid calendar dates (e.g., '2026-02-30') in
   InvalidDateError(BookingException) at the service entry boundary rather than leaking
   raw ValueError/TypeError from PricingService.
3. Strict Integer Hour Enforcement: Rejects floats (e.g., 10.5) and booleans (True/False,
   which subclass int in Python) upfront via InvalidTimeSlotError before persisting state.
"""

import datetime
import secrets
import string
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    from .models import (
        BookingException,
        InvalidDateError,
        InvalidTimeSlotError,
        OperatingHoursExceededError,
        QuotaExceededError,
        Reservation,
        ReservationStatus,
        ResourceNotFoundError,
        Room,
        SlotConflictError,
        User,
        UserRole,
    )
except ImportError:
    from models import (
        BookingException,
        InvalidDateError,
        InvalidTimeSlotError,
        OperatingHoursExceededError,
        QuotaExceededError,
        Reservation,
        ReservationStatus,
        ResourceNotFoundError,
        Room,
        SlotConflictError,
        User,
        UserRole,
    )


def parse_and_normalize_date(date_str: str) -> datetime.date:
    """
    Validates calendar date input and returns a datetime.date object.
    Raises InvalidDateError (a BookingException subclass) on malformed or non-string inputs.
    """
    if not isinstance(date_str, str) or not date_str.strip():
        raise InvalidDateError(f"Invalid date input '{date_str}'. Expected non-empty 'YYYY-MM-DD' string.")
    cleaned = date_str.strip()
    try:
        return datetime.datetime.strptime(cleaned, "%Y-%m-%d").date()
    except ValueError as exc:
        raise InvalidDateError(
            f"Invalid calendar date '{date_str}'. Expected valid Gregorian date in 'YYYY-MM-DD' format."
        ) from exc


@dataclass(frozen=True)
class PricingBreakdown:
    duration: int
    hourly_rate: float
    base_cost: float
    discount: float
    surcharge: float
    total_cost: float


class PricingService:
    """Encapsulates all financial and rate calculation rules with domain-safe date parsing."""

    STUDENT_DISCOUNT: float = 0.15
    WEEKEND_SURCHARGE: float = 0.20

    def calculate(self, room: Room, user: User, date_str: str, duration: int) -> PricingBreakdown:
        booking_date = parse_and_normalize_date(date_str)
        is_weekend = booking_date.weekday() >= 5

        base_cost = round(duration * room.hourly_rate, 2)
        discount = round(base_cost * self.STUDENT_DISCOUNT, 2) if user.is_student() else 0.0
        subtotal = round(base_cost - discount, 2)
        surcharge = round(subtotal * self.WEEKEND_SURCHARGE, 2) if is_weekend else 0.0
        total_cost = round(subtotal + surcharge, 2)

        return PricingBreakdown(
            duration=duration,
            hourly_rate=room.hourly_rate,
            base_cost=base_cost,
            discount=discount,
            surcharge=surcharge,
            total_cost=total_cost,
        )


class ConflictDetector:
    """Encapsulates schedule collision and quota validation rules."""

    @staticmethod
    def has_overlap(existing_reservations: List[Reservation], start: int, end: int) -> bool:
        """Determines if [start, end) intersects with any active reservation."""
        for r in existing_reservations:
            if r.is_active and max(start, r.start_hour) < min(end, r.end_hour):
                return True
        return False

    @staticmethod
    def exceeds_daily_quota(user_reservations: List[Reservation], new_duration: int, limit: int = 2) -> bool:
        """Checks if active bookings for user on that day + new_duration exceed the daily limit."""
        booked = sum(r.duration for r in user_reservations if r.is_active)
        return (booked + new_duration) > limit


class BookingRepository:
    """In-memory data access layer for users, rooms, and reservations."""

    def __init__(self):
        self._users: Dict[str, User] = {}
        self._rooms: Dict[str, Room] = {}
        self._reservations: Dict[int, Reservation] = {}
        self._seq = 1

    def add_user(self, user: User) -> None:
        self._users[user.user_id] = user

    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def add_room(self, room: Room) -> None:
        self._rooms[room.room_id] = room

    def get_room(self, room_id: str) -> Optional[Room]:
        return self._rooms.get(room_id)

    def save_reservation(self, res: Reservation) -> Reservation:
        if res.booking_id <= 0:
            res.booking_id = self._seq
            self._seq += 1
        self._reservations[res.booking_id] = res
        return res

    def get_reservation(self, booking_id: int) -> Optional[Reservation]:
        return self._reservations.get(booking_id)

    def find_by_room_and_date(self, room_id: str, date_str: str) -> List[Reservation]:
        canonical = parse_and_normalize_date(date_str).isoformat()
        return [r for r in self._reservations.values() if r.room_id == room_id and r.date_str == canonical]

    def find_by_user_and_date(self, user_id: str, date_str: str) -> List[Reservation]:
        canonical = parse_and_normalize_date(date_str).isoformat()
        return [r for r in self._reservations.values() if r.user_id == user_id and r.date_str == canonical]


class BookingService:
    """Orchestrates room reservation workflows with corrected upfront input normalization."""

    OPERATING_START: int = 8
    OPERATING_END: int = 22
    STUDENT_DAILY_LIMIT: int = 2

    def __init__(
        self,
        repo: BookingRepository,
        pricing: PricingService,
        conflict: ConflictDetector,
    ):
        self.repo = repo
        self.pricing = pricing
        self.conflict = conflict

    @staticmethod
    def _validate_strict_integer_hours(start_hour: int, end_hour: int) -> None:
        """Rejects booleans (bool subclasses int in Python), floats, and non-numeric hour types."""
        if type(start_hour) is not int or type(end_hour) is not int:
            raise InvalidTimeSlotError(
                f"Booking hours must be strict integers (received start_hour={start_hour!r}, end_hour={end_hour!r})."
            )

    def create_booking(self, user_id: str, room_id: str, date_str: str, start_hour: int, end_hour: int) -> Reservation:
        # 1. User & Room validation
        user = self.repo.get_user(user_id)
        if not user or not user.is_active:
            raise ResourceNotFoundError(f"Active user '{user_id}' not found.")

        room = self.repo.get_room(room_id)
        if not room or not room.is_active:
            raise ResourceNotFoundError(f"Active room '{room_id}' not found.")

        # 2. Corrective Fix: Upfront canonical date validation & strict integer-hour verification
        canonical_date = parse_and_normalize_date(date_str).isoformat()
        self._validate_strict_integer_hours(start_hour, end_hour)

        # 3. Operating hours validation
        if start_hour < self.OPERATING_START or end_hour > self.OPERATING_END or start_hour >= end_hour:
            raise OperatingHoursExceededError(
                f"Booking {start_hour}:00-{end_hour}:00 is outside operating window (08:00-22:00)."
            )

        # 4. Collision validation using canonical ISO-8601 date
        existing_room_bookings = self.repo.find_by_room_and_date(room_id, canonical_date)
        if self.conflict.has_overlap(existing_room_bookings, start_hour, end_hour):
            raise SlotConflictError(f"Room '{room.name}' is already reserved for requested time on {canonical_date}.")

        # 5. Student quota validation using canonical ISO-8601 date
        duration = end_hour - start_hour
        if user.is_student():
            user_bookings = self.repo.find_by_user_and_date(user_id, canonical_date)
            if self.conflict.exceeds_daily_quota(user_bookings, duration, limit=self.STUDENT_DAILY_LIMIT):
                raise QuotaExceededError(
                    f"Student '{user.name}' exceeded daily quota of {self.STUDENT_DAILY_LIMIT} hours."
                )

        # 6. Pricing calculation via PricingService
        breakdown = self.pricing.calculate(room, user, canonical_date, duration)

        # 7. Generate strictly formatted 19-char confirmation token (SKD-YYYYMMDD-XXXXXX) & persist
        clean_date = canonical_date.replace("-", "")
        suffix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        token = f"SKD-{clean_date}-{suffix}"
        reservation = Reservation(
            booking_id=0,
            token=token,
            user_id=user_id,
            room_id=room_id,
            date_str=canonical_date,
            start_hour=start_hour,
            end_hour=end_hour,
            base_cost=breakdown.base_cost,
            discount=breakdown.discount,
            surcharge=breakdown.surcharge,
            total_cost=breakdown.total_cost,
            status=ReservationStatus.CONFIRMED,
        )
        saved = self.repo.save_reservation(reservation)

        print(f"[RECEIPT] Booking #{saved.booking_id} | Token: {token}")
        print(f"  User: {user.name} ({user.role.value.title()}) | Room: {room.name} ({room.room_type.value.title()})")
        print(f"  Slot: {canonical_date} {start_hour:02d}:00-{end_hour:02d}:00 ({duration} hrs)")
        print(
            f"  Cost: Base ${breakdown.base_cost:.2f} - Disc ${breakdown.discount:.2f}"
            f" + Surch ${breakdown.surcharge:.2f} = Total ${breakdown.total_cost:.2f}\n"
        )
        return saved

    def cancel_booking(self, booking_id: int) -> bool:
        res = self.repo.get_reservation(booking_id)
        if not res:
            raise ResourceNotFoundError(f"Booking #{booking_id} not found.")
        if not res.is_active:
            return False
        res.status = ReservationStatus.CANCELLED
        print(f"[CANCELLED] Booking #{booking_id} (Token: {res.token}) cancelled successfully.")
        return True
