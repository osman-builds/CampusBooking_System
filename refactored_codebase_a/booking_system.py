"""
Campus Facility & Room Booking System
Refactored Codebase A: Fowler-Refactored Implementation

Refactorings Applied to Resolve Code Smells in Codebase A:
1. Extract Class:
   - 'PricingCalculator' handles rates, discounts, and surcharges (resolves Duplicate Code & God Class).
   - 'ReceiptPrinter' handles output formatting (resolves God Class SRP violation).
2. Extract Method:
   - Decomposes monolithic 'create_booking' into:
     _validate_entities, _validate_operating_hours, _check_slot_conflict, _check_student_quota.
3. Replace Magic Numbers with Symbolic Constants (8, 22, 2).
4. Guard Clauses: Early exits replacing deeply nested conditionals.
"""

import datetime
import secrets
import string
from dataclasses import dataclass
from typing import Dict, List, Optional


# =============================================================================
# Refactoring 1: Extract Class (Pricing Calculation)
# =============================================================================
@dataclass(frozen=True)
class PricingResult:
    duration: int
    hourly_rate: float
    base_cost: float
    discount: float
    surcharge: float
    total_cost: float


class PricingCalculator:
    """Extracted class with single responsibility for calculating pricing & discounts."""

    RATES: Dict[str, float] = {
        "standard": 20.0,
        "lab": 35.0,
        "studio": 35.0,
    }
    STUDENT_DISCOUNT_RATE: float = 0.15
    WEEKEND_SURCHARGE_RATE: float = 0.20

    @classmethod
    def calculate(cls, room_type: str, user_role: str, date_str: str, duration: int) -> PricingResult:
        booking_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        is_weekend = booking_date.weekday() >= 5

        rate = cls.RATES.get(room_type.lower(), 20.0)
        base = round(duration * rate, 2)
        discount = round(base * cls.STUDENT_DISCOUNT_RATE, 2) if user_role.lower() == "student" else 0.0
        subtotal = round(base - discount, 2)
        surcharge = round(subtotal * cls.WEEKEND_SURCHARGE_RATE, 2) if is_weekend else 0.0
        total = round(subtotal + surcharge, 2)

        return PricingResult(
            duration=duration,
            hourly_rate=rate,
            base_cost=base,
            discount=discount,
            surcharge=surcharge,
            total_cost=total
        )


# =============================================================================
# Refactoring 2: Extract Class (Receipt Printer)
# =============================================================================
class ReceiptPrinter:
    """Extracted class with single responsibility for formatting and dispatching receipts."""

    @staticmethod
    def print_receipt(record: dict, user: dict, room: dict, pricing: PricingResult) -> None:
        print(f"\n[RECEIPT] Booking #{record['booking_id']} | Token: {record['token']}")
        print(f"  User: {user['name']} ({user['role'].title()}) | Room: {room['name']} ({room['room_type'].title()})")
        print(f"  Slot: {record['date']} {record['start_hour']:02d}:00-{record['end_hour']:02d}:00 ({pricing.duration} hrs)")
        print(f"  Cost: Base ${pricing.base_cost:.2f} - Disc ${pricing.discount:.2f} + Surch ${pricing.surcharge:.2f} = Total ${pricing.total_cost:.2f}\n")


# =============================================================================
# Refactored BookingSystem (Cohesive, Clean Coordination)
# =============================================================================
class BookingSystem:
    """Refactored Booking System with extracted methods and separated responsibilities."""

    OPERATING_START: int = 8
    OPERATING_END: int = 22
    STUDENT_DAILY_QUOTA: int = 2

    def __init__(self):
        self.users: Dict[str, dict] = {}
        self.rooms: Dict[str, dict] = {}
        self.reservations: List[dict] = []
        self.booking_counter: int = 1

    def register_user(self, user_id: str, name: str, role: str, email: str = "") -> bool:
        role_clean = str(role).strip().lower()
        if role_clean not in ["student", "faculty", "staff", "admin"]:
            print(f"[ERROR] Invalid role '{role}'. Allowed: student, faculty, staff, admin.")
            return False
        if user_id in self.users:
            print(f"[ERROR] User ID '{user_id}' already exists.")
            return False
        self.users[user_id] = {
            "user_id": user_id,
            "name": name,
            "role": role_clean,
            "email": email,
            "is_active": True
        }
        print(f"[SUCCESS] Registered User '{name}' ({role_clean}) [{user_id}]")
        return True

    def register_room(self, room_id: str, name: str, room_type: str, capacity: int) -> bool:
        type_clean = str(room_type).strip().lower()
        if type_clean not in ["standard", "lab", "studio"]:
            print(f"[ERROR] Invalid room_type '{room_type}'. Allowed: standard, lab, studio.")
            return False
        if room_id in self.rooms:
            print(f"[ERROR] Room ID '{room_id}' already exists.")
            return False
        self.rooms[room_id] = {
            "room_id": room_id,
            "name": name,
            "room_type": type_clean,
            "capacity": capacity,
            "is_active": True
        }
        print(f"[SUCCESS] Registered Room '{name}' ({type_clean}, Cap: {capacity}) [{room_id}]")
        return True

    # -------------------------------------------------------------------------
    # Extracted Helper Validation Methods (Extract Method)
    # -------------------------------------------------------------------------
    def _validate_entities(self, user_id: str, room_id: str) -> Optional[tuple]:
        user = self.users.get(user_id)
        if not user or not user.get("is_active"):
            print(f"[REJECTED] Active user '{user_id}' not found.")
            return None
        room = self.rooms.get(room_id)
        if not room or not room.get("is_active"):
            print(f"[REJECTED] Active room '{room_id}' not found.")
            return None
        return user, room

    def _validate_operating_hours(self, start_hour: int, end_hour: int) -> bool:
        if start_hour < self.OPERATING_START or end_hour > self.OPERATING_END or start_hour >= end_hour:
            print(f"[REJECTED] Operating bounds exceeded: 08:00-22:00 required (requested {start_hour}:00-{end_hour}:00).")
            return False
        return True

    def _has_slot_conflict(self, room_id: str, date_str: str, start: int, end: int) -> bool:
        for r in self.reservations:
            if r["room_id"] == room_id and r["date"] == date_str and r["status"] == "CONFIRMED":
                if max(start, r["start_hour"]) < min(end, r["end_hour"]):
                    return True
        return False

    def _exceeds_student_quota(self, user_id: str, date_str: str, duration: int) -> bool:
        booked = sum(
            (r["end_hour"] - r["start_hour"])
            for r in self.reservations
            if r["user_id"] == user_id and r["date"] == date_str and r["status"] == "CONFIRMED"
        )
        return (booked + duration) > self.STUDENT_DAILY_QUOTA

    # -------------------------------------------------------------------------
    # Refactored create_booking (Clean Linear Flow)
    # -------------------------------------------------------------------------
    def create_booking(self, user_id: str, room_id: str, date_str: str, start_hour: int, end_hour: int) -> Optional[dict]:
        # Guard clause 1: Entity validation
        entities = self._validate_entities(user_id, room_id)
        if not entities:
            return None
        user, room = entities

        # Guard clause 2: Operating hours
        if not self._validate_operating_hours(start_hour, end_hour):
            return None

        # Guard clause 3: Schedule conflict
        if self._has_slot_conflict(room_id, date_str, start_hour, end_hour):
            print(f"[CONFLICT] Room '{room['name']}' already booked during requested time slot.")
            return None

        # Guard clause 4: Student quota
        duration = end_hour - start_hour
        if user["role"] == "student" and self._exceeds_student_quota(user_id, date_str, duration):
            print(f"[QUOTA] Student '{user['name']}' exceeded daily limit (max {self.STUDENT_DAILY_QUOTA} hrs).")
            return None

        # Delegated Pricing Calculation (Extract Class)
        pricing = PricingCalculator.calculate(room["room_type"], user["role"], date_str, duration)

        # Generate Token & Record
        suffix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        token = f"SKD-{date_str.replace('-', '')}-{suffix}"
        record = {
            "booking_id": self.booking_counter,
            "token": token,
            "user_id": user_id,
            "room_id": room_id,
            "date": date_str,
            "start_hour": start_hour,
            "end_hour": end_hour,
            "duration": duration,
            "hourly_rate": pricing.hourly_rate,
            "base_cost": pricing.base_cost,
            "discount": pricing.discount,
            "surcharge": pricing.surcharge,
            "total_cost": pricing.total_cost,
            "status": "CONFIRMED"
        }
        self.reservations.append(record)
        self.booking_counter += 1

        # Delegated Receipt Printing (Extract Class)
        ReceiptPrinter.print_receipt(record, user, room, pricing)
        return record

    def cancel_booking(self, booking_id: int) -> bool:
        for r in self.reservations:
            if r["booking_id"] == booking_id:
                if r["status"] == "CANCELLED":
                    print(f"[NOTICE] Booking #{booking_id} is already cancelled.")
                    return False
                r["status"] = "CANCELLED"
                print(f"[CANCELLED] Booking #{booking_id} (Token: {r['token']}) cancelled successfully.")
                return True
        print(f"[ERROR] Booking #{booking_id} not found.")
        return False

    def get_booking(self, booking_id: int) -> Optional[dict]:
        return next((r for r in self.reservations if r["booking_id"] == booking_id), None)


if __name__ == "__main__":
    print("=== Campus Room Booking System (Refactored Codebase A) ===")
    bs = BookingSystem()
    bs.register_user("U-101", "Alice Johnson", "student", "alice@campus.edu")
    bs.register_user("U-102", "Dr. Robert Smith", "faculty", "rsmith@campus.edu")
    bs.register_room("R-SR1", "Seminar Room Alpha", "standard", 30)
    bs.register_room("R-LB2", "Computer Vision Lab", "lab", 15)

    print("\n--- 1. Valid Bookings ---")
    bs.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)  # Weekday Student: $34.00
    bs.create_booking("U-102", "R-LB2", "2026-10-17", 14, 17)  # Weekend Faculty: $126.00

    print("--- 2. Schedule Conflict Test ---")
    bs.create_booking("U-102", "R-SR1", "2026-10-12", 11, 13)

    print("--- 3. Student Daily Quota Test ---")
    bs.create_booking("U-101", "R-LB2", "2026-10-12", 15, 16)

    print("--- 4. Cancellation & Re-booking ---")
    bs.cancel_booking(1)
    bs.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)
