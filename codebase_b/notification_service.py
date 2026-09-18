"""
Notification Service Layer for Campus Booking System (Codebase B).
Adheres to Interface Segregation and Dependency Inversion Principles.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

try:
    from models import Reservation, Room, User
    from pricing_service import PricingBreakdown
except ImportError:
    from .models import Reservation, Room, User
    from .pricing_service import PricingBreakdown


@dataclass(frozen=True)
class NotificationPayload:
    """Structured payload capturing all essential details of a booking event."""
    event_type: str  # "CONFIRMATION" or "CANCELLATION"
    booking_id: int
    confirmation_token: str
    user_id: str
    user_name: str
    user_email: str
    room_id: str
    room_name: str
    start_time: datetime
    end_time: datetime
    total_cost: float
    pricing_breakdown: Optional[PricingBreakdown] = None
    timestamp: datetime = datetime.now()


class NotificationService(ABC):
    """Abstract contract for sending booking notifications and receipts."""

    @abstractmethod
    def send_confirmation(
        self,
        reservation: Reservation,
        user: User,
        room: Room,
        breakdown: PricingBreakdown
    ) -> NotificationPayload:
        """Sends or logs a confirmation receipt upon successful booking."""
        pass

    @abstractmethod
    def send_cancellation(
        self,
        reservation: Reservation,
        user: User,
        room: Room
    ) -> NotificationPayload:
        """Sends or logs a cancellation notice."""
        pass


class InMemoryNotificationService(NotificationService):
    """
    Concrete in-memory implementation storing sent payloads and formatting structured receipts.
    """

    def __init__(self) -> None:
        self.sent_notifications: List[NotificationPayload] = []

    def send_confirmation(
        self,
        reservation: Reservation,
        user: User,
        room: Room,
        breakdown: PricingBreakdown
    ) -> NotificationPayload:
        payload = NotificationPayload(
            event_type="CONFIRMATION",
            booking_id=reservation.id,
            confirmation_token=reservation.confirmation_token,
            user_id=user.user_id,
            user_name=user.name,
            user_email=user.email,
            room_id=room.room_id,
            room_name=room.name,
            start_time=reservation.start_time,
            end_time=reservation.end_time,
            total_cost=reservation.total_cost,
            pricing_breakdown=breakdown
        )
        self.sent_notifications.append(payload)
        self._print_receipt(payload)
        return payload

    def send_cancellation(
        self,
        reservation: Reservation,
        user: User,
        room: Room
    ) -> NotificationPayload:
        payload = NotificationPayload(
            event_type="CANCELLATION",
            booking_id=reservation.id,
            confirmation_token=reservation.confirmation_token,
            user_id=user.user_id,
            user_name=user.name,
            user_email=user.email,
            room_id=room.room_id,
            room_name=room.name,
            start_time=reservation.start_time,
            end_time=reservation.end_time,
            total_cost=reservation.total_cost,
            pricing_breakdown=None
        )
        self.sent_notifications.append(payload)
        print(f"[NOTIFICATION] Cancellation dispatched for Booking #{reservation.id} (Token: {reservation.confirmation_token}) to {user.name} <{user.email}>")
        return payload

    def _print_receipt(self, payload: NotificationPayload) -> None:
        """Formats and outputs structured human-readable receipt."""
        bd = payload.pricing_breakdown
        print("\n" + "=" * 65)
        print("          CAMPUS BOOKING SYSTEM - NOTIFICATION RECEIPT          ")
        print("=" * 65)
        print(f" Event Type          : {payload.event_type}")
        print(f" Confirmation Token  : {payload.confirmation_token}")
        print(f" Booking ID          : #{payload.booking_id}")
        print(f" Recipient           : {payload.user_name} <{payload.user_email}>")
        print(f" Facility / Space    : {payload.room_name} (ID: {payload.room_id})")
        print(f" Scheduled Time      : {payload.start_time.strftime('%Y-%m-%d %H:%M')} to {payload.end_time.strftime('%H:%M')}")
        if bd:
            print(f" Hourly Rate         : ${bd.hourly_rate:.2f}/hr")
            print(f" Duration            : {bd.duration_hours:.1f} Hour(s)")
            print(f" Base Subtotal       : ${bd.base_cost:.2f}")
            print(f" Policy Discount     : -${bd.discount_amount:.2f}")
            print(f" Weekend Peak Charge : +${bd.surcharge_amount:.2f}")
            print(f" Total Amount Paid   : ${bd.total_cost:.2f}")
        else:
            print(f" Total Cost          : ${payload.total_cost:.2f}")
        print("=" * 65 + "\n")
