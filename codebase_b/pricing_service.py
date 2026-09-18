"""
Domain Service for Pricing and Fee Calculations (Codebase B).
Adheres to Single Responsibility Principle (SRP) and Open/Closed Principle (OCP)
by decomposing pricing rules into distinct, testable methods.
"""

from dataclasses import dataclass
from datetime import datetime

try:
    from models import Room, User, UserRole
except ImportError:
    from .models import Room, User, UserRole


@dataclass(frozen=True)
class PricingBreakdown:
    """Detailed itemized financial breakdown for a reservation."""
    duration_hours: float
    hourly_rate: float
    base_cost: float
    discount_amount: float
    surcharge_amount: float
    total_cost: float


class PricingService:
    """Calculates reservation pricing with discount policies and weekend surcharges."""

    STUDENT_DISCOUNT_RATE: float = 0.15
    WEEKEND_SURCHARGE_RATE: float = 0.20

    def calculate_base_cost(self, room: Room, duration_hours: float) -> float:
        """Calculates undiscounted baseline cost based on room hourly rate."""
        return round(room.base_hourly_rate * duration_hours, 2)

    def calculate_discount(self, base_cost: float, user: User) -> float:
        """Applies policy discount based on user classification."""
        if user.role == UserRole.STUDENT:
            return round(base_cost * self.STUDENT_DISCOUNT_RATE, 2)
        return 0.0

    def is_weekend_slot(self, slot_time: datetime) -> bool:
        """Checks if a given timestamp falls on a weekend (Saturday=5, Sunday=6)."""
        return slot_time.weekday() >= 5

    def calculate_surcharge(self, subtotal: float, slot_time: datetime) -> float:
        """Applies peak surcharge for weekend facility utilization."""
        if self.is_weekend_slot(slot_time):
            return round(subtotal * self.WEEKEND_SURCHARGE_RATE, 2)
        return 0.0

    def calculate_total(
        self,
        room: Room,
        user: User,
        start_time: datetime,
        end_time: datetime
    ) -> PricingBreakdown:
        """
        Orchestrates full fee computation through isolated pricing rules.
        """
        duration = (end_time - start_time).total_seconds() / 3600.0
        base = self.calculate_base_cost(room, duration)
        discount = self.calculate_discount(base, user)
        subtotal = base - discount
        surcharge = self.calculate_surcharge(subtotal, start_time)
        total = round(subtotal + surcharge, 2)

        return PricingBreakdown(
            duration_hours=duration,
            hourly_rate=room.base_hourly_rate,
            base_cost=base,
            discount_amount=discount,
            surcharge_amount=surcharge,
            total_cost=total
        )
