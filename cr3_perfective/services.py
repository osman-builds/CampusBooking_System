"""
Campus Facility & Room Booking System - CR-03 (Perfective Maintenance)
Module: services.py - Capacity Validation, Space Discovery, O(1) Indexing & Decoupled Notifications

Perfective Improvements over Codebase B Baseline:
1. Functional Enhancement: Enforces Room.capacity via attendees validation (CapacityExceededError)
   and introduces smart best-fit room discovery via find_available_rooms().
2. Performance Optimization: Replaces O(N) linear repository scans with O(1) composite-key
   secondary hash indexes (_idx_room_date and _idx_user_date).
3. Architectural Cohesion (SRP): Extracts hardcoded console print() statements out of
   BookingService into an injectable NotificationService hierarchy.
"""

import datetime
import secrets
import string
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

try:
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
except ImportError:
    from models import (
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


@dataclass(frozen=True)
class PricingBreakdown:
    duration: int
    hourly_rate: float
    base_cost: float
    discount: float
    surcharge: float
    total_cost: float


class PricingService:
    """Encapsulates all financial and rate calculation rules."""

    STUDENT_DISCOUNT: float = 0.15
    WEEKEND_SURCHARGE: float = 0.20

    def calculate(self, room: Room, user: User, date_str: str, duration: int) -> PricingBreakdown:
        booking_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
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


class AbstractNotificationService(ABC):
    """Decouples presentation/receipt I/O side effects from BookingService orchestration (SRP)."""

    @abstractmethod
    def notify_confirmed(self, res: Reservation, user: User, room: Room, breakdown: PricingBreakdown) -> None:
        pass

    @abstractmethod
    def notify_cancelled(self, res: Reservation) -> None:
        pass


class ConsoleNotificationService(AbstractNotificationService):
    """Formats and prints human-readable booking receipts to standard output."""

    def notify_confirmed(self, res: Reservation, user: User, room: Room, breakdown: PricingBreakdown) -> None:
        print(f"[RECEIPT] Booking #{res.booking_id} | Token: {res.token}")
        print(
            f"  User: {user.name} ({user.role.value.title()}) | Room: {room.name}"
            f" ({room.room_type.value.title()}, Seats: {res.attendees}/{room.capacity})"
        )
        print(f"  Slot: {res.date_str} {res.start_hour:02d}:00-{res.end_hour:02d}:00 ({res.duration} hrs)")
        print(
            f"  Cost: Base ${breakdown.base_cost:.2f} - Disc ${breakdown.discount:.2f}"
            f" + Surch ${breakdown.surcharge:.2f} = Total ${breakdown.total_cost:.2f}\n"
        )

    def notify_cancelled(self, res: Reservation) -> None:
        print(f"[CANCELLED] Booking #{res.booking_id} (Token: {res.token}) cancelled successfully.")


class SilentNotificationService(AbstractNotificationService):
    """No-op notification adapter for quiet automated testing and high-throughput benchmarks."""

    def notify_confirmed(self, res: Reservation, user: User, room: Room, breakdown: PricingBreakdown) -> None:
        # Intentionally empty: Null-Object pattern suppresses stdout during silent batch/test runs.
        pass

    def notify_cancelled(self, res: Reservation) -> None:
        # Intentionally empty: Null-Object pattern suppresses stdout during silent batch/test runs.
        pass


class BookingRepository:
    """
    In-memory data access layer optimized with O(1) composite secondary hash indexes
    on (room_id, date_str) and (user_id, date_str), eliminating O(N) full-table scans.
    """

    def __init__(self):
        self._users: Dict[str, User] = {}
        self._rooms: Dict[str, Room] = {}
        self._reservations: Dict[int, Reservation] = {}
        self._idx_room_date: Dict[Tuple[str, str], List[Reservation]] = defaultdict(list)
        self._idx_user_date: Dict[Tuple[str, str], List[Reservation]] = defaultdict(list)
        self._seq = 1

    def add_user(self, user: User) -> None:
        self._users[user.user_id] = user

    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def add_room(self, room: Room) -> None:
        self._rooms[room.room_id] = room

    def get_room(self, room_id: str) -> Optional[Room]:
        return self._rooms.get(room_id)

    def list_active_rooms(self) -> List[Room]:
        return [room for room in self._rooms.values() if room.is_active]

    def save_reservation(self, res: Reservation) -> Reservation:
        is_new = res.booking_id <= 0 or res.booking_id not in self._reservations
        if res.booking_id <= 0:
            res.booking_id = self._seq
            self._seq += 1
        self._reservations[res.booking_id] = res
        if is_new:
            self._idx_room_date[(res.room_id, res.date_str)].append(res)
            self._idx_user_date[(res.user_id, res.date_str)].append(res)
        return res

    def get_reservation(self, booking_id: int) -> Optional[Reservation]:
        return self._reservations.get(booking_id)

    def find_by_room_and_date(self, room_id: str, date_str: str) -> List[Reservation]:
        """O(1) composite-key bucket lookup instead of O(N) full-repository scan."""
        return list(self._idx_room_date.get((room_id, date_str), ()))

    def find_by_user_and_date(self, user_id: str, date_str: str) -> List[Reservation]:
        """O(1) composite-key bucket lookup instead of O(N) full-repository scan."""
        return list(self._idx_user_date.get((user_id, date_str), ()))


class BookingService:
    """Orchestrates room reservations, attendee capacity bounds, and best-fit space discovery."""

    OPERATING_START: int = 8
    OPERATING_END: int = 22
    STUDENT_DAILY_LIMIT: int = 2

    def __init__(
        self,
        repo: BookingRepository,
        pricing: PricingService,
        conflict: ConflictDetector,
        notifier: Optional[AbstractNotificationService] = None,
    ):
        self.repo = repo
        self.pricing = pricing
        self.conflict = conflict
        self.notifier = notifier if notifier is not None else ConsoleNotificationService()

    def _validate_operating_window(self, start_hour: int, end_hour: int) -> None:
        if start_hour < self.OPERATING_START or end_hour > self.OPERATING_END or start_hour >= end_hour:
            raise OperatingHoursExceededError(
                f"Booking {start_hour}:00-{end_hour}:00 is outside operating window (08:00-22:00)."
            )

    @staticmethod
    def _validate_capacity(room: Room, attendees: int) -> None:
        if attendees < 1 or attendees > room.capacity:
            raise CapacityExceededError(
                f"Requested attendees ({attendees}) invalid or exceeds capacity ({room.capacity}) of '{room.name}'."
            )

    def find_available_rooms(
        self,
        date_str: str,
        start_hour: int,
        end_hour: int,
        min_capacity: int = 1,
        room_type: Optional[RoomType] = None,
    ) -> List[Room]:
        """
        Discovers active rooms free during [start_hour, end_hour) meeting min_capacity and optional room_type.
        Sorted by best-fit capacity ascending, then hourly rate ascending.
        """
        self._validate_operating_window(start_hour, end_hour)
        if min_capacity < 1:
            raise CapacityExceededError(f"Minimum capacity filter must be >= 1 (received {min_capacity}).")

        candidates: List[Room] = []
        for room in self.repo.list_active_rooms():
            if room.capacity < min_capacity:
                continue
            if room_type is not None and room.room_type != room_type:
                continue
            room_bookings = self.repo.find_by_room_and_date(room.room_id, date_str)
            if not self.conflict.has_overlap(room_bookings, start_hour, end_hour):
                candidates.append(room)

        return sorted(candidates, key=lambda r: (r.capacity, r.hourly_rate, r.room_id))

    def create_booking(
        self,
        user_id: str,
        room_id: str,
        date_str: str,
        start_hour: int,
        end_hour: int,
        attendees: int = 1,
    ) -> Reservation:
        user = self.repo.get_user(user_id)
        if not user or not user.is_active:
            raise ResourceNotFoundError(f"Active user '{user_id}' not found.")

        room = self.repo.get_room(room_id)
        if not room or not room.is_active:
            raise ResourceNotFoundError(f"Active room '{room_id}' not found.")

        # Operating hours & Room capacity validation
        self._validate_operating_window(start_hour, end_hour)
        self._validate_capacity(room, attendees)

        # O(1)-indexed collision validation
        existing_room_bookings = self.repo.find_by_room_and_date(room_id, date_str)
        if self.conflict.has_overlap(existing_room_bookings, start_hour, end_hour):
            raise SlotConflictError(f"Room '{room.name}' is already reserved for requested time on {date_str}.")

        # O(1)-indexed student quota validation
        duration = end_hour - start_hour
        if user.is_student():
            user_bookings = self.repo.find_by_user_and_date(user_id, date_str)
            if self.conflict.exceeds_daily_quota(user_bookings, duration, limit=self.STUDENT_DAILY_LIMIT):
                raise QuotaExceededError(
                    f"Student '{user.name}' exceeded daily quota of {self.STUDENT_DAILY_LIMIT} hours."
                )

        breakdown = self.pricing.calculate(room, user, date_str, duration)

        # Generate confirmation token, persist, and dispatch decoupled notification
        clean_date = date_str.replace("-", "")
        suffix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        token = f"SKD-{clean_date}-{suffix}"
        reservation = Reservation(
            booking_id=0,
            token=token,
            user_id=user_id,
            room_id=room_id,
            date_str=date_str,
            start_hour=start_hour,
            end_hour=end_hour,
            base_cost=breakdown.base_cost,
            discount=breakdown.discount,
            surcharge=breakdown.surcharge,
            total_cost=breakdown.total_cost,
            attendees=attendees,
            status=ReservationStatus.CONFIRMED,
        )
        saved = self.repo.save_reservation(reservation)
        self.notifier.notify_confirmed(saved, user, room, breakdown)
        return saved

    def cancel_booking(self, booking_id: int) -> bool:
        res = self.repo.get_reservation(booking_id)
        if not res:
            raise ResourceNotFoundError(f"Booking #{booking_id} not found.")
        if not res.is_active:
            return False
        res.status = ReservationStatus.CANCELLED
        self.notifier.notify_cancelled(res)
        return True
