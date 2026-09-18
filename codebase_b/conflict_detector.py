"""
Pure Domain Service for Collision and Policy Detection (Codebase B).
Adheres strictly to Single Responsibility Principle (SRP) by decoupling conflict rules.
"""

from datetime import datetime
from typing import Iterable

try:
    from models import Reservation
except ImportError:
    from .models import Reservation


class ConflictDetector:
    """Encapsulates collision logic and quota constraint validation."""

    @staticmethod
    def has_overlap(
        existing_reservations: Iterable[Reservation],
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """
        Determines if [start_time, end_time) intersects with any active booking.
        Intervals [A, B) and [C, D) overlap if max(A, C) < min(B, D).
        """
        for reservation in existing_reservations:
            if not reservation.is_active:
                continue

            # Standard interval intersection condition for half-open intervals
            if max(start_time, reservation.start_time) < min(end_time, reservation.end_time):
                return True

        return False

    @staticmethod
    def exceeds_daily_quota(
        user_reservations: Iterable[Reservation],
        new_duration_hours: float,
        max_daily_hours: float = 2.0
    ) -> bool:
        """
        Calculates cumulative booked hours for the given user reservations
        and checks if adding `new_duration_hours` exceeds `max_daily_hours`.
        """
        active_hours = sum(
            res.duration_hours
            for res in user_reservations
            if res.is_active
        )
        return (active_hours + new_duration_hours) > max_daily_hours
